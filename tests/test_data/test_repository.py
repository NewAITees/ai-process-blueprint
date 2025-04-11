import pytest
import os
from app.schemas.models import TemplateCreate, TemplateUpdate

async def test_create_template(template_repository, sample_template_data):
    # テンプレート作成テスト
    template_create = TemplateCreate(**sample_template_data)
    template = await template_repository.create(template_create)
    
    assert template.title == sample_template_data["title"]
    assert template.content == sample_template_data["content"]
    assert template.description == sample_template_data["description"]
    assert template.username == sample_template_data["username"]
    
    # ファイルが作成されたか確認
    expected_filename = os.path.join(
        template_repository.templates_dir,
        template_repository._title_to_filename(sample_template_data["title"])
    )
    assert os.path.exists(expected_filename)

async def test_get_template(template_repository, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    created_template = await template_repository.create(template_create)
    
    # テンプレート取得テスト
    template = await template_repository.get(sample_template_data["title"])
    
    assert template.title == sample_template_data["title"]
    assert template.content == sample_template_data["content"]

async def test_update_template(template_repository, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    created_template = await template_repository.create(template_create)
    
    # 更新データ
    update_data = {
        "description": "更新された説明",
        "content": "更新された内容"
    }
    template_update = TemplateUpdate(**update_data)
    
    # テンプレート更新テスト
    updated_template = await template_repository.update(
        sample_template_data["title"], 
        template_update
    )
    
    assert updated_template.description == update_data["description"]
    assert updated_template.content == update_data["content"]
    assert updated_template.title == sample_template_data["title"]

async def test_delete_template(template_repository, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    created_template = await template_repository.create(template_create)
    
    # テンプレート削除テスト
    await template_repository.delete(sample_template_data["title"])
    
    # ファイルが削除されたか確認
    expected_filename = os.path.join(
        template_repository.templates_dir,
        template_repository._title_to_filename(sample_template_data["title"])
    )
    assert not os.path.exists(expected_filename)

async def test_list_templates(template_repository, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    created_template = await template_repository.create(template_create)
    
    # テンプレート一覧取得テスト
    templates = await template_repository.list()
    
    assert len(templates) >= 1
    template = next(t for t in templates if t.title == sample_template_data["title"])
    assert template.content == sample_template_data["content"] 