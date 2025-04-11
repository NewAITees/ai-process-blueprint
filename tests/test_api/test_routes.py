import pytest
from fastapi import status

def test_create_template(api_client, sample_template_data):
    # テンプレート作成APIテスト
    response = api_client.post("/api/templates", json=sample_template_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == sample_template_data["title"]
    assert data["content"] == sample_template_data["content"]
    
    # 同じタイトルで2回目の作成は409エラーになるはず
    response = api_client.post("/api/templates", json=sample_template_data)
    assert response.status_code == status.HTTP_409_CONFLICT

def test_get_template(api_client, sample_template_data):
    # まずテンプレートを作成
    api_client.post("/api/templates", json=sample_template_data)
    
    # テンプレート取得APIテスト
    response = api_client.get(f"/api/templates/{sample_template_data['title']}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == sample_template_data["title"]
    
    # 存在しないテンプレートの取得は404エラーになるはず
    response = api_client.get("/api/templates/not-exist")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_template(api_client, sample_template_data):
    # まずテンプレートを作成
    api_client.post("/api/templates", json=sample_template_data)
    
    # 更新データ
    update_data = {
        "description": "更新された説明",
        "content": "更新された内容"
    }
    
    # テンプレート更新APIテスト
    response = api_client.put(
        f"/api/templates/{sample_template_data['title']}", 
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["content"] == update_data["content"]
    
    # 存在しないテンプレートの更新は404エラーになるはず
    response = api_client.put("/api/templates/not-exist", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_template(api_client, sample_template_data):
    # まずテンプレートを作成
    api_client.post("/api/templates", json=sample_template_data)
    
    # テンプレート削除APIテスト
    response = api_client.delete(f"/api/templates/{sample_template_data['title']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # 削除後の取得は404エラーになるはず
    response = api_client.get(f"/api/templates/{sample_template_data['title']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_templates(api_client, sample_template_data):
    # まずテンプレートを作成
    api_client.post("/api/templates", json=sample_template_data)
    
    # テンプレート一覧取得APIテスト
    response = api_client.get("/api/templates")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "templates" in data
    templates = data["templates"]
    assert len(templates) >= 1
    template = next(t for t in templates if t["title"] == sample_template_data["title"])
    assert template["content"] == sample_template_data["content"] 