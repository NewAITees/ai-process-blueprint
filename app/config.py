"""
Configuration module for the AI Process Blueprint application.
Handles loading of environment variables and application settings.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    port: int = Field(default=8080, env="PORT")
    template_dir: Path = Field(default=Path("./templates"), env="TEMPLATE_DIR")
    log_level: str = Field(default="info", env="LOG_LEVEL")
    enable_mcp: bool = Field(default=True, env="ENABLE_MCP")
    enable_http: bool = Field(default=True, env="ENABLE_HTTP")
    
    # Development settings
    debug: bool = Field(default=False, env="DEBUG")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Create a global settings instance
settings = Settings()
