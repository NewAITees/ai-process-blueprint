"""
Application startup script.
"""

import uvicorn
import logging
from app.config import settings

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting server on port {settings.port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
