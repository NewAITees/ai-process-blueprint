import pytest
from app.schemas.models import TemplateCreate, TemplateUpdate
from app.core.services import TemplateNotFoundError, TemplateAlreadyExistsError

async def test_create_template(template_service, sample_template_data):
    # テンプレート作成テスト
    template_create = TemplateCreate(**sample_template_data)
    template = await template_service.create_template(template_create)
    
    assert template.title == sample_template_data["title"]
    assert hasattr(template, "created_at")
    assert hasattr(template, "updated_at")
    
    # 同じタイトルで2回目の作成は失敗するはず
    with pytest.raises(TemplateAlreadyExistsError):
        await template_service.create_template(template_create)

async def test_get_template(template_service, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    created_template = await template_service.create_template(template_create)
    
    # テンプレート取得テスト
    template = await template_service.get_template(sample_template_data["title"])
    
    assert template.title == sample_template_data["title"]
    assert template.content == sample_template_data["content"]
    
    # 存在しないテンプレートの取得は失敗するはず
    with pytest.raises(TemplateNotFoundError):
        await template_service.get_template("not-exist")

async def test_update_template(template_service, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    created_template = await template_service.create_template(template_create)
    
    # 更新データ
    update_data = {
        "description": "更新された説明",
        "content": "更新された内容"
    }
    template_update = TemplateUpdate(**update_data)
    
    # テンプレート更新テスト
    updated_template = await template_service.update_template(
        sample_template_data["title"],
        template_update
    )
    
    assert updated_template.description == update_data["description"]
    assert updated_template.content == update_data["content"]
    assert updated_template.title == sample_template_data["title"]
    assert updated_template.updated_at > updated_template.created_at

async def test_delete_template(template_service, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    created_template = await template_service.create_template(template_create)
    
    # テンプレート削除テスト
    await template_service.delete_template(sample_template_data["title"])
    
    # 削除後の取得は失敗するはず
    with pytest.raises(TemplateNotFoundError):
        await template_service.get_template(sample_template_data["title"])

async def test_list_templates(template_service, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    created_template = await template_service.create_template(template_create)
    
    # テンプレート一覧取得テスト
    templates = await template_service.list_templates()
    
    assert len(templates) >= 1
    template = next(t for t in templates if t.title == sample_template_data["title"])
    assert template.content == sample_template_data["content"] 