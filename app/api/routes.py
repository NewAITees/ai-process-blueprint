import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.schemas.models import Template, TemplateCreate, TemplateUpdate
from app.core.services import (
    TemplateService,
    TemplateNotFoundError,
    TemplateAlreadyExistsError,
    TemplateValidationError,
    TemplateServiceError # ベースのサービスエラーも捕捉する可能性を考慮
)
from app.data.repository import FileSystemTemplateRepository, TemplateRepository, TemplateIOError
from app.config import settings

logger = logging.getLogger(__name__)

# --- 依存性注入 --- #

def get_template_repository() -> TemplateRepository:
    """Dependency injector for the template repository."""
    # 設定からテンプレートディレクトリを取得
    return FileSystemTemplateRepository(settings.TEMPLATE_DIR)

def get_template_service(
    repository: TemplateRepository = Depends(get_template_repository)
) -> TemplateService:
    """Dependency injector for the template service."""
    return TemplateService(repository)

# --- APIルーター --- #

template_router = APIRouter(
    prefix="/api/templates",
    tags=["templates"],
    # ここで共通のエラーレスポンスを定義することも可能
    # responses={404: {"description": "Template not found"}}
)

# --- エンドポイント定義 --- #

@template_router.post(
    "/",
    response_model=Template,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new template",
    description="Registers a new template based on the provided title, content, and optional description/username."
)
async def create_template(
    template: TemplateCreate,
    service: TemplateService = Depends(get_template_service)
):
    """Creates a new template based on the provided data."""
    try:
        # サービスのメソッドを呼び出してテンプレートを作成
        created_template = await service.create_template(template)
        return created_template
    except TemplateAlreadyExistsError as e:
        logger.warning(f"Conflict creating template '{template.title}': {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except TemplateValidationError as e:
         logger.warning(f"Validation error creating template '{template.title}': {e}")
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (TemplateIOError, TemplateServiceError) as e:
         # リポジトリ/サービス層の他の予期せぬエラー
         logger.error(f"Error creating template '{template.title}': {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while creating the template.")

@template_router.get(
    "/{title}",
    response_model=Template,
    summary="Get a template by title",
    description="Retrieves the details of a specific template identified by its title.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Template not found"}
    }
)
async def get_template(
    title: str,
    service: TemplateService = Depends(get_template_service)
):
    """Retrieves a single template by its unique title."""
    try:
        # サービスのメソッドを呼び出してテンプレートを取得
        template = await service.get_template(title)
        return template
    except TemplateNotFoundError as e:
        logger.info(f"Template not found: {title}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (TemplateIOError, TemplateServiceError) as e:
         logger.error(f"Error retrieving template '{title}': {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while retrieving the template.")

# リスト取得用のレスポンスモデル
class TemplateListResponse(BaseModel):
    """Response model for listing templates."""
    templates: List[Template]
    total: int  # 全体の件数 (フィルタリング後)
    limit: int
    offset: int

    model_config = {
        "from_attributes": True  # Pydantic V2
    }

@template_router.get(
    "/",
    response_model=TemplateListResponse,
    summary="List templates",
    description="Retrieves a list of templates, with options for pagination and filtering by username."
)
async def list_templates(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of templates to return"),
    offset: int = Query(0, ge=0, description="Number of templates to skip for pagination"),
    username: Optional[str] = Query(None, description="Filter templates by username"),
    service: TemplateService = Depends(get_template_service)
):
    """Lists templates with pagination and optional username filtering."""
    try:
        # サービスのメソッドを呼び出してテンプレートリストを取得
        templates = await service.list_templates(limit=limit, offset=offset, username=username)
        # 注意: 現在のサービス/リポジトリ実装では全体の件数を効率的に取得できない
        # 全件取得するか、別途カウント用のメソッドが必要。ここでは取得した件数をtotalとする
        total_count = len(templates) # 仮。理想はフィルタリング後の全件数
        # TODO: 必要であれば、リポジトリに全件数をカウントするメソッドを追加する
        return TemplateListResponse(templates=templates, total=total_count, limit=limit, offset=offset)
    except (TemplateIOError, TemplateServiceError) as e:
         logger.error(f"Error listing templates: {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while listing templates.")

@template_router.put(
    "/{title}",
    response_model=Template,
    summary="Update a template",
    description="Updates an existing template identified by its title. Only provided fields are updated.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Template not found"}
    }
)
async def update_template(
    title: str,
    template_update: TemplateUpdate,
    service: TemplateService = Depends(get_template_service)
):
    """Updates an existing template identified by its title."""
    try:
        # サービスのメソッドを呼び出してテンプレートを更新
        updated_template = await service.update_template(title, template_update)
        return updated_template
    except TemplateNotFoundError as e:
        logger.info(f"Template not found for update: {title}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TemplateValidationError as e:
         logger.warning(f"Validation error updating template '{title}': {e}")
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (TemplateIOError, TemplateServiceError) as e:
         logger.error(f"Error updating template '{title}': {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while updating the template.")

@template_router.delete(
    "/{title}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a template",
    description="Deletes a template identified by its title.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Template not found"},
        status.HTTP_204_NO_CONTENT: {"description": "Template deleted successfully"}
    }
)
async def delete_template(
    title: str,
    service: TemplateService = Depends(get_template_service)
):
    """Deletes a template identified by its title."""
    try:
        # サービスのメソッドを呼び出してテンプレートを削除
        success = await service.delete_template(title)
        if not success:
            # 通常、deleteがFalseを返すのは予期せぬケースか、
            # リポジトリ実装によっては削除対象が見つからなかった場合かもしれない
            # TemplateNotFoundErrorで捕捉されるはずなので、ここはエラーログを出す程度に留める
            logger.error(f"Template deletion reported failure for title: {title}, though no exception was raised.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete template due to an unexpected error.")
        # 成功時は No Content なので本体は返さない
        return None # または return Response(status_code=status.HTTP_204_NO_CONTENT)
    except TemplateNotFoundError as e:
        logger.info(f"Template not found for deletion: {title}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (TemplateIOError, TemplateServiceError) as e:
         logger.error(f"Error deleting template '{title}': {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while deleting the template.")

# --- グローバル例外ハンドラー (オプション、main.py で定義する方が一般的) --- #
# FastAPIではHTTPExceptionを使うのが基本だが、カスタムエラーを直接返すことも可能
# 例:
# @template_router.exception_handler(TemplateNotFoundError)
# async def template_not_found_exception_handler(request: Request, exc: TemplateNotFoundError):
#     logger.info(f"Caught TemplateNotFoundError: {exc}")
#     return JSONResponse(
#         status_code=status.HTTP_404_NOT_FOUND,
#         content={"error": "Template not found", "message": str(exc)}
#     )
