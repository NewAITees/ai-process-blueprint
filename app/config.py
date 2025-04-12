"""
Configuration module for the AI Process Blueprint application.
Handles loading of environment variables and application settings.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # .envファイルから環境変数を読み込む

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    port: int = int(os.getenv("PORT", 8080))
    template_dir: Path = Path(os.getenv("TEMPLATE_DIR", "./templates"))
    log_level: str = os.getenv("LOG_LEVEL", "info")
    enable_mcp: bool = os.getenv("ENABLE_MCP", "true").lower() == "true"
    enable_http: bool = os.getenv("ENABLE_HTTP", "true").lower() == "true"
    
    # Development settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Application version (placeholder)
    version: str = "0.1.0"
    
    model_config = {
        # .envファイルを優先的に読み込む設定 (pydantic-settings v2以降)
        # env_file = ".env"
        # env_file_encoding = 'utf-8'
        "case_sensitive": True
    }


# Create a global settings instance
settings = Settings()

# テンプレートディレクトリの修正（Docker連携のため最適化）
if str(settings.template_dir) == "/templates":
    # プロジェクトルートディレクトリを取得
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent  # app/config.py から3階層上
    
    # プロジェクトルート直下のtemplatesディレクトリを使用
    settings.template_dir = project_root / "templates"
    
    # ディレクトリが存在しない場合は作成
    os.makedirs(settings.template_dir, exist_ok=True)
    print(f"Template directory set to: {settings.template_dir}")

def setup_logging():
    """アプリケーションのロギング設定を行います"""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # ライブラリの過剰なログを抑制 (例: uvicorn.access)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Setup logging when the module is imported
setup_logging()
