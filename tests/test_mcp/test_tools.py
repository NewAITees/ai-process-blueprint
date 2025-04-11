import pytest
from app.schemas.models import TemplateCreate
from app.mcp.tools import get_template, register_template, update_template, delete_template, list_templates

async def test_get_template_tool(template_service, sample_template_data):
    # サービスを使用してテンプレートを作成
    template_create = TemplateCreate(**sample_template_data)
    await template_service.create_template(template_create)
    
    # MCPツールでのテンプレート取得テスト
    result = await get_template(title=sample_template_data["title"])
    
    assert result["title"] == sample_template_data["title"]
    assert result["content"] == sample_template_data["content"]
    
    # 存在しないテンプレートの取得
    result = await get_template(title="not-exist")
    assert "error" in result
    assert result["error"] == "Template not found"

async def test_register_template_tool(template_service, sample_template_data):
    # MCPツールでのテンプレート登録テスト
    result = await register_template(**sample_template_data)
    
    assert result["title"] == sample_template_data["title"]
    assert result["content"] == sample_template_data["content"]
    
    # 同じタイトルで2回目の登録
    result = await register_template(**sample_template_data)
    assert "error" in result
    assert result["error"] == "Template already exists"

async def test_update_template_tool(template_service, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    await template_service.create_template(template_create)
    
    # 更新データ
    update_data = {
        "title": sample_template_data["title"],
        "description": "更新された説明",
        "content": "更新された内容"
    }
    
    # MCPツールでのテンプレート更新テスト
    result = await update_template(**update_data)
    
    assert result["description"] == update_data["description"]
    assert result["content"] == update_data["content"]
    
    # 存在しないテンプレートの更新
    result = await update_template(title="not-exist", content="新しい内容")
    assert "error" in result
    assert result["error"] == "Template not found"

async def test_delete_template_tool(template_service, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    await template_service.create_template(template_create)
    
    # MCPツールでのテンプレート削除テスト
    result = await delete_template(title=sample_template_data["title"])
    assert result["success"] is True
    
    # 削除確認
    result = await get_template(title=sample_template_data["title"])
    assert "error" in result
    
    # 存在しないテンプレートの削除
    result = await delete_template(title="not-exist")
    assert "error" in result
    assert result["error"] == "Template not found"

async def test_list_templates_tool(template_service, sample_template_data):
    # テンプレート作成
    template_create = TemplateCreate(**sample_template_data)
    await template_service.create_template(template_create)
    
    # MCPツールでのテンプレート一覧取得テスト
    result = await list_templates()
    
    assert "templates" in result
    templates = result["templates"]
    assert len(templates) >= 1
    template = next(t for t in templates if t["title"] == sample_template_data["title"])
    assert template["content"] == sample_template_data["content"] 