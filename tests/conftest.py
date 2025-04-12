"""
Test configuration and fixtures.
"""

import os
import pytest
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.core.services import TemplateService
from app.data.repository import FileSystemTemplateRepository
from app.schemas.models import TemplateCreate


@pytest.fixture
def test_template_dir(tmp_path):
    """テスト用の一時テンプレートディレクトリを作成"""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    # 環境変数を一時的に上書き
    original_template_dir = os.environ.get("TEMPLATE_DIR")
    os.environ["TEMPLATE_DIR"] = str(template_dir)
    yield template_dir
    # テスト後に環境変数を元に戻す
    if original_template_dir:
        os.environ["TEMPLATE_DIR"] = original_template_dir
    else:
        os.environ.pop("TEMPLATE_DIR", None)
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
def api_client(test_template_dir):
    """テスト用のFastAPI TestClientを作成"""
    # アプリケーションがTEMPLATE_DIRを読み込み直すようにする
    from app.config import settings
    settings.TEMPLATE_DIR = test_template_dir
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


@pytest.fixture
async def sample_template(template_service, sample_template_data):
    """事前に作成されたサンプルテンプレートを提供"""
    template_create = TemplateCreate(**sample_template_data)
    return await template_service.create_template(template_create)
