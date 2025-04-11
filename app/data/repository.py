import os
import re
import yaml
import logging
import aiofiles
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from pathlib import Path
import unicodedata

from app.schemas.models import Template, TemplateCreate, TemplateUpdate
# サービス層で定義した例外をインポート（またはリポジトリ固有の例外を定義）
from app.core.services import TemplateNotFoundError, TemplateAlreadyExistsError, TemplateValidationError

logger = logging.getLogger(__name__)

# --- リポジトリ固有の例外 --- #
class RepositoryError(Exception):
    """Base exception for repository errors."""
    pass

class TemplateIOError(RepositoryError):
    """Raised for file I/O errors during template operations."""
    pass

# --- 抽象リポジトリインターフェース --- #
class TemplateRepository(ABC):
    """Abstract base class for template repositories."""

    @abstractmethod
    async def create(self, template_data: TemplateCreate) -> Template:
        """Creates a new template entry."""
        pass

    @abstractmethod
    async def get(self, title: str) -> Template:
        """Retrieves a template by its title."""
        pass

    @abstractmethod
    async def update(self, title: str, template_update: TemplateUpdate) -> Template:
        """Updates an existing template."""
        pass

    @abstractmethod
    async def delete(self, title: str) -> bool:
        """Deletes a template by its title."""
        pass

    @abstractmethod
    async def list(self, limit: int = 20, offset: int = 0, username: Optional[str] = None) -> List[Template]:
        """Lists templates with filtering and pagination."""
        pass

# --- ファイルシステムベースのリポジトリ実装 --- #
class FileSystemTemplateRepository(TemplateRepository):
    """Template repository implementation using the local file system."""

    def __init__(self, templates_dir: str):
        """Initializes the repository with the template directory.
        
        Args:
            templates_dir: The path to the directory where templates are stored.
        """
        self.templates_dir = Path(templates_dir)
        # テンプレートディレクトリが存在しない場合は作成
        try:
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Template directory initialized: {self.templates_dir}")
        except OSError as e:
            logger.error(f"Failed to create template directory {self.templates_dir}: {e}")
            raise TemplateIOError(f"Failed to initialize template directory: {e}") from e

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitizes a string to be used as a valid filename."""
        # NFKC正規化で互換文字を統一
        normalized = unicodedata.normalize('NFKC', filename)
        # 無効な文字や区切り文字をアンダースコアに置換
        # (POSIXファイルシステムの一般的な制限に基づく)
        sanitized = re.sub(r'[\\s<>:"/\\\\|?*.,;!#%=+~']+', '_', normalized)
        # 先頭と末尾のアンダースコアやドットを削除
        sanitized = sanitized.strip('_.')
        # 連続するアンダースコアを1つにまとめる
        sanitized = re.sub(r'_{2,}', '_', sanitized)
        # 小文字化
        sanitized = sanitized.lower()
        # 長すぎるファイル名を切り詰める（例: 100文字）
        max_len = 100
        if len(sanitized) > max_len:
            sanitized = sanitized[:max_len]
            # 切り詰めた場合、末尾のアンダースコアを削除
            sanitized = sanitized.strip('_')
        # 空のファイル名を防ぐ
        if not sanitized:
            return "default_template"
        return sanitized

    def _title_to_filename(self, title: str) -> str:
        """Converts a template title to a safe filename (without extension)."""
        return self._sanitize_filename(title) + ".md"

    def _filename_to_title(self, filename: str) -> str:
        """Attempts to convert a filename back to a title (best effort)."""
        title = Path(filename).stem # 拡張子を除去
        # 簡単な逆変換（アンダースコアをスペースに戻すなど）が必要ならここで行う
        # ただし、完全な復元は困難な場合が多い
        return title.replace('_', ' ').title() # 例: アンダースコアをスペースに、タイトルケースに

    async def _read_template_file(self, file_path: Path) -> Template:
        """Reads a template file and parses its content and metadata."""
        try:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
            
            metadata = {}
            markdown_content = content
            
            # YAMLフロントマターの抽出
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = parts[1].strip()
                        if frontmatter: # 空のフロントマターを許容しない場合
                             metadata = yaml.safe_load(frontmatter)
                             if not isinstance(metadata, dict):
                                 logger.warning(f"Invalid YAML front matter format in {file_path}, treating as content.")
                                 metadata = {} # 無効な場合は無視
                             else:
                                 markdown_content = parts[2].strip()
                        else:
                             markdown_content = parts[2].strip() # ---が2つあっても中身が空ならコンテンツのみ
                    except yaml.YAMLError as e:
                        logger.warning(f"Failed to parse YAML front matter in {file_path}: {e}. Treating entire file as content.")
                        # YAMLパース失敗時はファイル全体をコンテンツとして扱う
                        metadata = {}
                        markdown_content = content
                else:
                    # `---` が1つしかない場合などは全体をコンテンツとして扱う
                    markdown_content = content
            
            # メタデータからTemplateオブジェクトを作成 (デフォルト値と型変換を含む)
            # created_at/updated_atがない場合はファイルのmtimeを使うか、エラーとするか
            # ここではファイル内に必須とする前提で進めるが、より堅牢にするならフォールバックが必要
            title = metadata.get('title', self._filename_to_title(file_path.name))
            created_at_str = metadata.get('created_at')
            updated_at_str = metadata.get('updated_at')

            if not created_at_str or not updated_at_str:
                 logger.warning(f"Missing timestamp metadata in {file_path}. Using file modification time.")
                 stat_result = await asyncio.to_thread(os.stat, file_path)
                 mtime_dt = datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc)
                 created_at = mtime_dt # 簡易的にmtimeを使用
                 updated_at = mtime_dt
            else:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                    updated_at = datetime.fromisoformat(updated_at_str)
                    # タイムゾーン情報がない場合はUTCとみなす（要検討）
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    if updated_at.tzinfo is None:
                        updated_at = updated_at.replace(tzinfo=timezone.utc)
                except ValueError:
                     logger.error(f"Invalid timestamp format in {file_path}. Using file modification time.")
                     stat_result = await asyncio.to_thread(os.stat, file_path)
                     mtime_dt = datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc)
                     created_at = mtime_dt
                     updated_at = mtime_dt

            return Template(
                title=title, # YAMLのタイトルを優先
                content=markdown_content,
                description=metadata.get('description', ""),
                username=metadata.get('username', "unknown"),
                created_at=created_at,
                updated_at=updated_at,
            )

        except FileNotFoundError:
            logger.warning(f"Template file not found: {file_path}")
            raise TemplateNotFoundError(f"Template file not found: {file_path.name}")
        except IOError as e:
            logger.error(f"Error reading template file {file_path}: {e}")
            raise TemplateIOError(f"Error reading template file: {e}") from e
        except Exception as e: # yaml.YAMLErrorなども含む予期せぬエラー
             logger.error(f"Unexpected error processing template file {file_path}: {e}")
             raise TemplateIOError(f"Unexpected error processing template file {file_path.name}: {e}") from e

    async def _safe_write(self, file_path: Path, content: str) -> None:
        """Writes content to a file safely using a temporary file."""
        temp_file_path = file_path.with_suffix(f'{file_path.suffix}.tmp')
        try:
            async with aiofiles.open(temp_file_path, mode='w', encoding='utf-8') as f:
                await f.write(content)
            # アトミックにリネーム (Windowsではアトミック性が保証されない場合がある)
            await asyncio.to_thread(os.replace, temp_file_path, file_path)
            logger.debug(f"Safely wrote content to {file_path}")
        except IOError as e:
            logger.error(f"Error writing template file {file_path}: {e}")
            # 一時ファイルの削除を試みる
            try:
                if await asyncio.to_thread(temp_file_path.exists):
                     await asyncio.to_thread(os.remove, temp_file_path)
            except OSError as rm_err:
                 logger.warning(f"Failed to remove temporary file {temp_file_path}: {rm_err}")
            raise TemplateIOError(f"Error writing template file: {e}") from e
        except Exception as e:
             logger.error(f"Unexpected error during safe write to {file_path}: {e}")
             raise TemplateIOError(f"Unexpected error writing template file: {e}") from e

    async def _write_template_file(self, template: Template, file_path: Path) -> None:
        """Writes a Template object to a file with YAML front matter."""
        metadata = {
            "title": template.title,
            "description": template.description,
            "username": template.username,
            # 日時はISO 8601形式で保存
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat(),
        }
        try:
            yaml_frontmatter = yaml.dump(metadata, sort_keys=False, allow_unicode=True)
        except yaml.YAMLError as e:
            logger.error(f"Failed to serialize YAML front matter for {template.title}: {e}")
            raise TemplateIOError(f"Failed to generate YAML for template {template.title}: {e}") from e

        file_content = f"---
{yaml_frontmatter}---

{template.content}"
        
        await self._safe_write(file_path, file_content)

    # --- TemplateRepository ABC 実装 --- #

    async def create(self, template_data: TemplateCreate) -> Template:
        if not template_data.title:
             raise TemplateValidationError("Template title cannot be empty.")
             
        filename = self._title_to_filename(template_data.title)
        file_path = self.templates_dir / filename

        if await asyncio.to_thread(file_path.exists):
            logger.warning(f"Attempted to create template that already exists: {template_data.title} ({filename})")
            raise TemplateAlreadyExistsError(f"Template with title '{template_data.title}' already exists.")

        now = datetime.now(timezone.utc)
        template = Template(
            **template_data.model_dump(),
            created_at=now,
            updated_at=now,
        )

        try:
            await self._write_template_file(template, file_path)
            logger.info(f"Successfully created template: {template.title} ({filename})")
            return template
        except TemplateIOError as e:
             logger.error(f"Failed to create template file for {template.title}: {e}")
             # 作成失敗時は具体的なエラーを上位に伝播させる
             raise TemplateIOError(f"Failed to create template '{template.title}': {e}") from e

    async def get(self, title: str) -> Template:
        if not title:
             raise TemplateValidationError("Template title cannot be empty.")
             
        filename = self._title_to_filename(title)
        file_path = self.templates_dir / filename
        
        # _read_template_file内でFileNotFoundError -> TemplateNotFoundError変換を行う
        return await self._read_template_file(file_path)

    async def update(self, title: str, template_update: TemplateUpdate) -> Template:
        if not title:
             raise TemplateValidationError("Template title cannot be empty.")

        filename = self._title_to_filename(title)
        file_path = self.templates_dir / filename

        try:
            # 既存のテンプレートを読み込む (存在確認を兼ねる)
            existing_template = await self._read_template_file(file_path)
        except TemplateNotFoundError:
             logger.warning(f"Attempted to update non-existent template: {title}")
             raise TemplateNotFoundError(f"Template with title '{title}' not found for update.")

        # 更新データで既存テンプレートを更新
        update_data = template_update.model_dump(exclude_unset=True) # Noneでない値のみ取得
        updated_template = existing_template.model_copy(update=update_data)
        
        # 更新日時を現在時刻に設定
        updated_template.updated_at = datetime.now(timezone.utc)
        # ユーザー名が指定されていなければ既存のものを維持、指定されていれば更新
        if template_update.username is None:
             updated_template.username = existing_template.username

        try:
            await self._write_template_file(updated_template, file_path)
            logger.info(f"Successfully updated template: {title} ({filename})")
            return updated_template
        except TemplateIOError as e:
            logger.error(f"Failed to update template file for {title}: {e}")
            raise TemplateIOError(f"Failed to update template '{title}': {e}") from e

    async def delete(self, title: str) -> bool:
        if not title:
             raise TemplateValidationError("Template title cannot be empty.")
             
        filename = self._title_to_filename(title)
        file_path = self.templates_dir / filename

        try:
            await asyncio.to_thread(os.remove, file_path)
            logger.info(f"Successfully deleted template: {title} ({filename})")
            return True
        except FileNotFoundError:
            logger.warning(f"Attempted to delete non-existent template: {title}")
            raise TemplateNotFoundError(f"Template with title '{title}' not found for deletion.")
        except OSError as e:
            logger.error(f"Error deleting template file {file_path}: {e}")
            raise TemplateIOError(f"Error deleting template '{title}': {e}") from e

    async def list(self, limit: int = 20, offset: int = 0, username: Optional[str] = None) -> List[Template]:
        templates: List[Template] = []
        try:
            # ディレクトリ内の全.mdファイルを非同期にリストアップ
            all_files = await asyncio.to_thread(lambda: list(self.templates_dir.glob('*.md')))
            
            # 各ファイルを読み込み、フィルタリング
            read_tasks = []
            for file_path in all_files:
                # 一時ファイルはスキップ
                if file_path.suffix == '.tmp':
                    continue
                read_tasks.append(self._read_template_file(file_path))
            
            results = await asyncio.gather(*read_tasks, return_exceptions=True)

            valid_templates = []
            for result in results:
                if isinstance(result, Template):
                    valid_templates.append(result)
                elif isinstance(result, Exception):
                     # 読み込みエラーがあったファイルはログに記録し、リストからは除外
                     logger.error(f"Failed to read or parse a template file during list operation: {result}")
                     # 特定のエラー（例：NotFoundError）は無視してもよいが、基本的にはログ出力

            # フィルタリング (username)
            if username:
                filtered_templates = [t for t in valid_templates if t.username == username]
            else:
                filtered_templates = valid_templates

            # ソート (更新日時の降順)
            filtered_templates.sort(key=lambda t: t.updated_at, reverse=True)

            # ページネーション
            start = offset
            end = offset + limit
            templates = filtered_templates[start:end]
            
            logger.info(f"Listed {len(templates)} templates (limit={limit}, offset={offset}, username={username})")
            return templates

        except OSError as e:
            logger.error(f"Error listing template directory {self.templates_dir}: {e}")
            raise TemplateIOError(f"Error listing templates: {e}") from e
        except Exception as e:
             logger.error(f"Unexpected error during template listing: {e}")
             raise TemplateIOError(f"Unexpected error listing templates: {e}") from e
