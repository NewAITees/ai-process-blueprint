"""
Application startup script.
"""

import uvicorn
import logging
from app.config import settings

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting server on port {settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
