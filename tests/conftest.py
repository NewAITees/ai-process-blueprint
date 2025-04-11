"""
Test configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def template_dir(tmp_path):
    """Create a temporary template directory for testing."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return template_dir
