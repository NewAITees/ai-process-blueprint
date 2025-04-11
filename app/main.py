"""
Main application module for AI Process Blueprint.
Sets up the FastAPI application with MCP integration.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings, setup_logging
from app.api.routes import router as api_router

# ロギング設定を初期化 (configモジュールで既に実行されている場合もあるが念のため)
setup_logging()
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Process Blueprint",
        description="テンプレートベースでAIに作業手順を提供するサービス",
        version=settings.VERSION,
        debug=settings.DEBUG,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Application startup")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"Template directory: {settings.TEMPLATE_DIR}")
        logger.info(f"HTTP API Enabled: {settings.ENABLE_HTTP}")
        logger.info(f"MCP Enabled: {settings.ENABLE_MCP}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Application shutdown")

    # 基本的なルート (動作確認用)
    @app.get("/")
    async def read_root():
        return {"message": "Welcome to AI Process Blueprint"}

    # ヘルスチェックエンドポイント (手順6で追加予定だが、ここで定義)
    @app.get("/health")
    async def health_check():
        """ヘルスチェックエンドポイント"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": settings.VERSION
        }

    # APIルーターとMCPサーバーのマウント
    if settings.ENABLE_HTTP:
        from app.api.routes import template_router
        logger.info("Registering HTTP API routes...")
        app.include_router(template_router)

    if settings.ENABLE_MCP:
        from app.mcp.tools import mcp_server
        logger.info("Mounting MCP server...")
        # FastMCP v0.4.0以降では .app は不要かもしれないが、互換性のために残す
        # ドキュメントを確認すること
        try:
            app.mount("/mcp", mcp_server.app)
        except AttributeError:
             # もし .app がなければ mcp_server 自体を渡す (FastMCPのバージョンによる)
             logger.warning("mcp_server.app not found, attempting to mount mcp_server directly.")
             app.mount("/mcp", mcp_server)

        # MCPツール定義を提供するエンドポイント
        @app.get("/mcp/tools.json")
        async def get_mcp_tools():
            """Returns the MCP tool definitions in OpenAPI format."""
            logger.debug("Request received for /mcp/tools.json")
            return mcp_server.get_tool_definitions()

    return app


# Create the application instance
app = create_app()
