"""
Test configuration and fixtures.
"""

import os
import pytest
import shutil
from fastapi.testclient import TestClient
from app.main import app
from app.core.services import TemplateService
from app.data.repository import FileSystemTemplateRepository


@pytest.fixture
def test_template_dir(tmp_path):
    """テスト用の一時テンプレートディレクトリを作成"""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    yield template_dir
    # テスト後にクリーンアップ
    shutil.rmtree(template_dir)


@pytest.fixture
def template_repository(test_template_dir):
    """テスト用のテンプレートリポジトリを作成"""
    return FileSystemTemplateRepository(str(test_template_dir))


@pytest.fixture
def template_service(template_repository):
    """テスト用のテンプレートサービスを作成"""
    return TemplateService(template_repository)


@pytest.fixture
def api_client():
    """テスト用のFastAPI TestClientを作成"""
    return TestClient(app)


@pytest.fixture
def sample_template_data():
    """テスト用のサンプルテンプレートデータを提供"""
    return {
        "title": "テストテンプレート",
        "content": "# テストテンプレート\n\nこれはテスト用のテンプレートです。",
        "description": "テスト用のテンプレート説明",
        "username": "tester"
    }
