import pytest
from fastapi import status

async def test_template_workflow(api_client, sample_template_data):
    # テンプレート作成
    create_response = api_client.post("/api/templates", json=sample_template_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_data = create_response.json()
    assert created_data["title"] == sample_template_data["title"]
    
    # テンプレート取得
    get_response = api_client.get(f"/api/templates/{sample_template_data['title']}")
    assert get_response.status_code == status.HTTP_200_OK
    get_data = get_response.json()
    assert get_data["title"] == sample_template_data["title"]
    
    # テンプレート更新
    update_data = {
        "description": "更新された説明",
        "content": "更新された内容"
    }
    update_response = api_client.put(
        f"/api/templates/{sample_template_data['title']}", 
        json=update_data
    )
    assert update_response.status_code == status.HTTP_200_OK
    updated_data = update_response.json()
    assert updated_data["description"] == update_data["description"]
    assert updated_data["content"] == update_data["content"]
    
    # テンプレート一覧取得
    list_response = api_client.get("/api/templates")
    assert list_response.status_code == status.HTTP_200_OK
    list_data = list_response.json()
    templates = list_data["templates"]
    assert len(templates) >= 1
    template = next(t for t in templates if t["title"] == sample_template_data["title"])
    assert template["content"] == update_data["content"]
    
    # テンプレート削除
    delete_response = api_client.delete(f"/api/templates/{sample_template_data['title']}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # 削除確認
    get_deleted_response = api_client.get(f"/api/templates/{sample_template_data['title']}")
    assert get_deleted_response.status_code == status.HTTP_404_NOT_FOUND

async def test_concurrent_template_operations(api_client, sample_template_data):
    # 同時作成テスト
    import asyncio
    
    async def create_template():
        return api_client.post("/api/templates", json=sample_template_data)
    
    # 同時に2つのリクエストを送信
    responses = await asyncio.gather(
        create_template(),
        create_template(),
        return_exceptions=True
    )
    
    # 1つ目は成功、2つ目は409エラーになるはず
    success_count = sum(1 for r in responses if r.status_code == status.HTTP_201_CREATED)
    conflict_count = sum(1 for r in responses if r.status_code == status.HTTP_409_CONFLICT)
    assert success_count == 1
    assert conflict_count == 1

async def test_error_handling(api_client):
    # 無効なJSONデータでのテンプレート作成
    invalid_data = {
        "title": "",  # 空のタイトル
        "content": None,  # 無効なコンテンツ
        "description": "説明",
        "username": "tester"
    }
    response = api_client.post("/api/templates", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # 存在しないテンプレートの操作
    not_exist_title = "not-exist-template"
    
    # 取得
    get_response = api_client.get(f"/api/templates/{not_exist_title}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    # 更新
    update_response = api_client.put(
        f"/api/templates/{not_exist_title}",
        json={"content": "新しい内容"}
    )
    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    
    # 削除
    delete_response = api_client.delete(f"/api/templates/{not_exist_title}")
    assert delete_response.status_code == status.HTTP_404_NOT_FOUND 