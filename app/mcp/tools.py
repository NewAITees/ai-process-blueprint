import logging
from typing import Optional, Dict, Any, List

from fastapi import Depends
from fastmcp import FastMCP

from app.schemas.models import Template, TemplateCreate, TemplateUpdate
from app.core.services import (
    TemplateService,
    TemplateNotFoundError,
    TemplateAlreadyExistsError,
    TemplateValidationError,
    TemplateServiceError
)
from app.data.repository import TemplateIOError
# APIルートから依存性注入関数をインポート (循環参照に注意)
# より良い設計は、依存性注入の設定を別の共有モジュール (例: app/dependencies.py) に置くこと
try:
    from app.api.routes import get_template_service
except ImportError:
     # 暫定対応: routesが先に読み込まれていない場合、ここで再定義
     # 本来は DI コンテナや共有モジュールを使うべき
     from app.data.repository import FileSystemTemplateRepository, TemplateRepository
     from app.config import settings
     def get_template_repository() -> TemplateRepository:
         return FileSystemTemplateRepository(settings.template_dir)
     def get_template_service() -> TemplateService:
         return TemplateService(get_template_repository())

logger = logging.getLogger(__name__)

# FastMCP サーバーのインスタンスを作成
mcp_server = FastMCP(
    title="AI Process Blueprint MCP Server",
    description="MCP service for managing AI process templates.",
    version="1.0.0",
    log_level="INFO"  # 注意: ログレベルは大文字で指定する必要がある
)

# --- MCP ツール定義 --- #

def get_service():
    """Helper to get template service instance without FastAPI dependency injection"""
    repo = FileSystemTemplateRepository(settings.template_dir)
    return TemplateService(repo)

@mcp_server.tool()
async def get_template(title: str) -> Dict[str, Any]:
    """
    Retrieves a template by its unique title.

    Args:
        title (str): The title of the template to retrieve.

    Returns:
        Dict[str, Any]: A dictionary containing the template data if found,
                      or an error message if not found or an error occurred.
                      Example success: {"title": "...", "content": "...", ...}
                      Example error: {"error": "Template not found", "message": "..."}

    Raises:
        Does not raise exceptions directly to the MCP client, returns error dictionary instead.
    """
    service = get_template_service()
    logger.info(f"[MCP] Received request to get template: {title}")
    service = get_service()
    try:
        template = await service.get_template(title)
        # Pydanticモデルを辞書に変換して返す
        logger.info(f"[MCP] Successfully retrieved template: {title}")
        return template.model_dump() # Pydantic V2
    except TemplateNotFoundError as e:
        logger.warning(f"[MCP] Template not found: {title} - {e}")
        return {"error": "Template not found", "message": str(e)}
    except (TemplateIOError, TemplateServiceError) as e:
        logger.error(f"[MCP] Error retrieving template '{title}': {e}", exc_info=True)
        return {"error": "Internal Server Error", "message": f"An internal error occurred: {e}"}
    except Exception as e:
        logger.error(f"[MCP] Unexpected error retrieving template '{title}': {e}", exc_info=True)
        return {"error": "Unexpected Error", "message": f"An unexpected error occurred: {e}"}


@mcp_server.tool()
async def list_templates(
    limit: int = 20,
    offset: int = 0,
    username: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lists registered templates with pagination and optional filtering by username.

    Args:
        limit (int): Maximum number of templates to return (default: 20, max: 100).
        offset (int): Number of templates to skip (default: 0).
        username (Optional[str]): Filter templates by this username if provided.

    Returns:
        Dict[str, Any]: A dictionary containing a list of templates and pagination info,
                      or an error message if an error occurred.
                      Example success: {"templates": [...], "total": N, "limit": L, "offset": O}
                      Example error: {"error": "Internal Server Error", "message": "..."}
    """
    service = get_template_service()
    logger.info(f"[MCP] Received request to list templates: limit={limit}, offset={offset}, username={username}")
    service = get_service()
    
    # 引数のバリデーション (FastAPIのQueryのような機能はないため手動で)
    if not (1 <= limit <= 100):
        limit = 20 # 不正な値はデフォルト値にフォールバック
        logger.warning(f"[MCP] Invalid limit value provided. Using default: {limit}")
    if offset < 0:
        offset = 0
        logger.warning(f"[MCP] Invalid offset value provided. Using default: {offset}")
        
    try:
        templates = await service.list_templates(limit=limit, offset=offset, username=username)
        # TODO: list_templatesが全件数を返すように修正する（APIと同様の課題）
        total_count = len(templates) # 仮
        logger.info(f"[MCP] Successfully listed {len(templates)} templates.")
        return {
            "templates": [t.model_dump() for t in templates],
            "total": total_count, # 本来はフィルタリング後の全件数
            "limit": limit,
            "offset": offset
        }
    except (TemplateIOError, TemplateServiceError) as e:
        logger.error(f"[MCP] Error listing templates: {e}", exc_info=True)
        return {"error": "Internal Server Error", "message": f"An internal error occurred: {e}"}
    except Exception as e:
        logger.error(f"[MCP] Unexpected error listing templates: {e}", exc_info=True)
        return {"error": "Unexpected Error", "message": f"An unexpected error occurred: {e}"}


@mcp_server.tool()
async def register_template(
    title: str,
    content: str,
    description: str = "",
    username: str = "ai_assistant"
) -> Dict[str, Any]:
    """
    Registers a new template.

    Args:
        title (str): The title of the template (must be unique).
        content (str): The Markdown content of the template.
        description (str): An optional description for the template (default: "").
        username (str): The username of the creator (default: "ai_assistant").

    Returns:
        Dict[str, Any]: A dictionary containing the created template data if successful,
                      or an error message if the title already exists or an error occurred.
                      Example success: {"title": "...", "content": "...", ...}
                      Example error: {"error": "Template already exists", "message": "..."}
    """
    service = get_template_service()
    logger.info(f"[MCP] Received request to register template: {title}")
    service = get_service()
    try:
        template_create = TemplateCreate(
            title=title,
            content=content,
            description=description,
            username=username
        )
        created_template = await service.create_template(template_create)
        logger.info(f"[MCP] Successfully registered template: {title}")
        return created_template.model_dump()
    except TemplateAlreadyExistsError as e:
        logger.warning(f"[MCP] Template already exists: {title} - {e}")
        return {"error": "Template already exists", "message": str(e)}
    except TemplateValidationError as e:
         logger.warning(f"[MCP] Validation error registering template '{title}': {e}")
         return {"error": "Validation Error", "message": str(e)}
    except (TemplateIOError, TemplateServiceError) as e:
        logger.error(f"[MCP] Error registering template '{title}': {e}", exc_info=True)
        return {"error": "Internal Server Error", "message": f"An internal error occurred: {e}"}
    except Exception as e:
        logger.error(f"[MCP] Unexpected error registering template '{title}': {e}", exc_info=True)
        return {"error": "Unexpected Error", "message": f"An unexpected error occurred: {e}"}


@mcp_server.tool()
async def update_template(
    title: str,
    content: Optional[str] = None,
    description: Optional[str] = None,
    username: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates an existing template. Only provided fields (content, description, username) are updated.

    Args:
        title (str): The title of the template to update.
        content (Optional[str]): The new Markdown content (if updating).
        description (Optional[str]): The new description (if updating).
        username (Optional[str]): The username of the updater (if updating).

    Returns:
        Dict[str, Any]: A dictionary containing the updated template data if successful,
                      or an error message if the template is not found or an error occurred.
                      Example success: {"title": "...", "content": "...", ...}
                      Example error: {"error": "Template not found", "message": "..."}
    """
    service = get_template_service()
    logger.info(f"[MCP] Received request to update template: {title}")
    service = get_service()
    
    if content is None and description is None and username is None:
        logger.warning(f"[MCP] Update request for '{title}' received no fields to update.")
        return {"error": "Validation Error", "message": "No fields provided to update."}
        
    try:
        template_update = TemplateUpdate(
            content=content,
            description=description,
            username=username
        )
        updated_template = await service.update_template(title, template_update)
        logger.info(f"[MCP] Successfully updated template: {title}")
        return updated_template.model_dump()
    except TemplateNotFoundError as e:
        logger.warning(f"[MCP] Template not found for update: {title} - {e}")
        return {"error": "Template not found", "message": str(e)}
    except TemplateValidationError as e:
         logger.warning(f"[MCP] Validation error updating template '{title}': {e}")
         return {"error": "Validation Error", "message": str(e)}
    except (TemplateIOError, TemplateServiceError) as e:
        logger.error(f"[MCP] Error updating template '{title}': {e}", exc_info=True)
        return {"error": "Internal Server Error", "message": f"An internal error occurred: {e}"}
    except Exception as e:
        logger.error(f"[MCP] Unexpected error updating template '{title}': {e}", exc_info=True)
        return {"error": "Unexpected Error", "message": f"An unexpected error occurred: {e}"}


@mcp_server.tool()
async def delete_template(title: str) -> Dict[str, Any]:
    """
    Deletes a template by its title.

    Args:
        title (str): The title of the template to delete.

    Returns:
        Dict[str, Any]: A dictionary indicating success or failure.
                      Example success: {"status": "success", "message": "Template '...' deleted successfully"}
                      Example error: {"error": "Template not found", "message": "..."}
    """
    service = get_template_service()
    logger.info(f"[MCP] Received request to delete template: {title}")
    service = get_service()
    try:
        success = await service.delete_template(title)
        if success:
            logger.info(f"[MCP] Successfully deleted template: {title}")
            return {"status": "success", "message": f"Template '{title}' deleted successfully"}
        else:
            # このケースは通常発生しないはず (エラーは例外で捕捉される)
            logger.error(f"[MCP] delete_template for '{title}' returned False unexpectedly.")
            return {"status": "error", "message": f"Failed to delete template '{title}' for an unknown reason."}
    except TemplateNotFoundError as e:
        logger.warning(f"[MCP] Template not found for deletion: {title} - {e}")
        return {"error": "Template not found", "message": str(e)}
    except (TemplateIOError, TemplateServiceError) as e:
        logger.error(f"[MCP] Error deleting template '{title}': {e}", exc_info=True)
        return {"error": "Internal Server Error", "message": f"An internal error occurred: {e}"}
    except Exception as e:
        logger.error(f"[MCP] Unexpected error deleting template '{title}': {e}", exc_info=True)
        return {"error": "Unexpected Error", "message": f"An unexpected error occurred: {e}"}
