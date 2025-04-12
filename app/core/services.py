import logging
from typing import List, Optional
from datetime import datetime, timezone

# 注意: 循環参照を避けるため、型ヒントには文字列を使用する
# from app.data.repository import TemplateRepository # 実行時インポートまたは型チェックブロック内でのみ使用
from app.schemas.models import Template, TemplateCreate, TemplateUpdate

logger = logging.getLogger(__name__)

class TemplateServiceError(Exception):
    """Base exception for template service errors."""
    pass

class TemplateNotFoundError(TemplateServiceError):
    """Raised when a template is not found."""
    pass

class TemplateAlreadyExistsError(TemplateServiceError):
    """Raised when attempting to create a template that already exists."""
    pass

class TemplateValidationError(TemplateServiceError):
    """Raised for template validation errors."""
    pass

class TemplateService:
    """Provides business logic for template management."""
    def __init__(self, repository):
        """Initializes the service with a template repository."""
        logger.debug(f"Initializing TemplateService with repository: {type(repository).__name__}")
        self.repository = repository

    async def create_template(self, template: TemplateCreate) -> Template:
        """Creates a new template.
        
        Args:
            template: The template data to create.
            
        Returns:
            The created template with timestamps.
            
        Raises:
            TemplateAlreadyExistsError: If a template with the same title already exists.
            TemplateIOError: If there is a file system error during creation.
        """
        logger.info(f"Attempting to create template: {template.title}")
        
        if not template.title:
            raise TemplateValidationError("Template title cannot be empty")

        try:
            # タイトルの存在チェック（重複確認）- 実装によっては不要
            # リポジトリの実装によっては、この確認はcreateメソッド内で行われる場合があります
            try:
                await self.repository.get(template.title)
                # 既に存在する場合はエラー
                logger.warning(f"Template with title '{template.title}' already exists")
                raise TemplateAlreadyExistsError(f"Template with title '{template.title}' already exists")
            except TemplateNotFoundError:
                # 存在しない場合は問題なし（続行）
                pass
                
            # 新しいテンプレートをリポジトリで作成
            created_template = await self.repository.create(template)
            logger.info(f"Successfully created template: {template.title}")
            return created_template
            
        except TemplateAlreadyExistsError:
            # 既に処理済みの例外を再発生
            raise
        except Exception as e:
            # その他の例外をログに記録して再発生
            logger.error(f"Error creating template '{template.title}': {e}", exc_info=True)
            raise

    async def get_template(self, title: str) -> Template:
        """Retrieves a template by its title.
        
        Args:
            title: The title of the template to retrieve.
            
        Returns:
            The found template.
            
        Raises:
            TemplateNotFoundError: If the template is not found.
            TemplateIOError: If there is a file system error during retrieval.
        """
        logger.info(f"Attempting to retrieve template: {title}")
        
        if not title:
            raise TemplateValidationError("Template title cannot be empty")
            
        try:
            template = await self.repository.get(title)
            logger.info(f"Successfully retrieved template: {title}")
            return template
        except TemplateNotFoundError:
            # リポジトリからの例外をそのまま再発生
            logger.warning(f"Template not found: {title}")
            raise
        except Exception as e:
            # その他の例外をログに記録して再発生
            logger.error(f"Error retrieving template '{title}': {e}", exc_info=True)
            raise

    async def update_template(self, title: str, template_update: TemplateUpdate) -> Template:
        """Updates an existing template.
        
        Args:
            title: The title of the template to update.
            template_update: The data to update the template with.
            
        Returns:
            The updated template.
            
        Raises:
            TemplateNotFoundError: If the template is not found.
            TemplateIOError: If there is a file system error during update.
        """
        logger.info(f"Attempting to update template: {title}")
        
        if not title:
            raise TemplateValidationError("Template title cannot be empty")
            
        try:
            # 既存テンプレートの取得（存在確認）
            # 一部のリポジトリ実装では、updateメソッド内で存在確認が行われる場合があります
            try:
                existing_template = await self.repository.get(title)
                logger.debug(f"Template found for update: {title}")
            except TemplateNotFoundError:
                logger.warning(f"Template not found for update: {title}")
                raise
                
            # 更新をリポジトリに委譲
            updated_template = await self.repository.update(title, template_update)
            logger.info(f"Successfully updated template: {title}")
            return updated_template
            
        except TemplateNotFoundError:
            # 既に処理済みの例外を再発生
            raise
        except Exception as e:
            # その他の例外をログに記録して再発生
            logger.error(f"Error updating template '{title}': {e}", exc_info=True)
            raise

    async def delete_template(self, title: str) -> bool:
        """Deletes a template by its title.
        
        Args:
            title: The title of the template to delete.
            
        Returns:
            True if deletion was successful, False otherwise.
            
        Raises:
            TemplateNotFoundError: If the template is not found.
            TemplateIOError: If there is a file system error during deletion.
        """
        logger.info(f"Attempting to delete template: {title}")
        
        if not title:
            raise TemplateValidationError("Template title cannot be empty")
            
        try:
            # 削除をリポジトリに委譲
            result = await self.repository.delete(title)
            if result:
                logger.info(f"Successfully deleted template: {title}")
            else:
                logger.warning(f"Failed to delete template: {title}")
            return result
        except TemplateNotFoundError:
            # リポジトリからの例外をそのまま再発生
            logger.warning(f"Template not found for deletion: {title}")
            raise
        except Exception as e:
            # その他の例外をログに記録して再発生
            logger.error(f"Error deleting template '{title}': {e}", exc_info=True)
            raise

    async def list_templates(self, limit: int = 20, offset: int = 0, username: Optional[str] = None) -> List[Template]:
        """Lists templates, optionally filtered by username, with pagination.
        
        Args:
            limit: Maximum number of templates to return.
            offset: Number of templates to skip.
            username: Filter templates by this username if provided.
            
        Returns:
            A list of templates.
        """
        logger.info(f"Listing templates with limit={limit}, offset={offset}, username={username}")
        
        try:
            # クエリパラメータの検証とデフォルト値の適用
            limit = max(1, min(limit, 100))  # 1-100の範囲内に制限
            offset = max(0, offset)  # 0以上に制限
            
            # リポジトリの一覧メソッドを呼び出し
            templates = await self.repository.list(limit, offset, username)
            logger.info(f"Successfully listed {len(templates)} templates")
            return templates
        except Exception as e:
            # 例外をログに記録して再発生
            logger.error(f"Error listing templates: {e}", exc_info=True)
            raise

# --- YAML フロントマター処理、ファイル名変換、バリデーション、エラー処理などは --- #
# --- リポジトリ層 (FileSystemTemplateRepository) での実装が主となるか、 ------ #
# --- またはサービス層とリポジトリ層で分担することになります。 ----------------- #
# --- ここではサービスのインターフェース定義に注力します。 -------------------- #
