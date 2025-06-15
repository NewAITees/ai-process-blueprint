# MCP 動作検証ガイド

このガイドは、AI Process BlueprintのMCP（Model Context Protocol）機能が正しく動作していることを確認するための手順を説明します。

## 前提条件

- 開発環境が正しくセットアップされていること
- サーバーが起動していること（ポート8081で起動中）

## 1. HTTP API動作確認

### テンプレート一覧の取得
```bash
curl -s http://localhost:8081/api/templates/ | python3 -m json.tool
```

### テンプレート作成
```bash
curl -X POST http://localhost:8081/api/templates/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "検証用テンプレート",
    "content": "# 検証用テンプレート\n\nこれは検証用のテンプレートです。",
    "description": "API経由で作成したテンプレート",
    "username": "test_user"
  }'
```

### 特定テンプレートの取得
```bash
curl -s "http://localhost:8081/api/templates/検証用テンプレート" | python3 -m json.tool
```

## 2. MCP機能の直接テスト

以下のPythonスクリプトを実行してMCP機能をテストします：

```python
import asyncio
from app.mcp.tools import get_template, list_templates, register_template, update_template, delete_template

async def comprehensive_mcp_test():
    print("=== MCP 機能総合テスト ===\n")
    
    # 1. テンプレート一覧取得
    print("1. テンプレート一覧取得")
    result = await list_templates()
    print(f"結果: {len(result.get('templates', []))}個のテンプレートが見つかりました")
    print(f"詳細: {result}\n")
    
    # 2. 新しいテンプレート作成
    print("2. 新しいテンプレート作成")
    result = await register_template(
        title="MCP検証テンプレート",
        content="# MCP検証テンプレート\n\n## 概要\nこれはMCP機能を検証するためのテンプレートです。\n\n## 手順\n1. 準備\n2. 実行\n3. 確認",
        description="MCP機能の検証用テンプレート",
        username="mcp_tester"
    )
    if 'error' in result:
        print(f"エラー: {result}")
    else:
        print(f"成功: テンプレート '{result['title']}' が作成されました")
    print()
    
    # 3. 作成したテンプレートの取得
    print("3. 作成したテンプレートの取得")
    result = await get_template("MCP検証テンプレート")
    if 'error' in result:
        print(f"エラー: {result}")
    else:
        print(f"成功: テンプレート '{result['title']}' を取得しました")
        print(f"作成者: {result['username']}")
        print(f"説明: {result['description']}")
    print()
    
    # 4. テンプレート更新
    print("4. テンプレート更新")
    result = await update_template(
        title="MCP検証テンプレート",
        description="MCP機能の検証用テンプレート（更新済み）",
        username="mcp_tester_updated"
    )
    if 'error' in result:
        print(f"エラー: {result}")
    else:
        print(f"成功: テンプレート '{result['title']}' が更新されました")
        print(f"新しい説明: {result['description']}")
    print()
    
    # 5. 更新後の再確認
    print("5. 更新後の確認")
    result = await get_template("MCP検証テンプレート")
    if 'error' in result:
        print(f"エラー: {result}")
    else:
        print(f"確認完了: 説明が正しく更新されています")
        print(f"現在の説明: {result['description']}")
        print(f"更新者: {result['username']}")
    print()
    
    # 6. 最新のテンプレート一覧確認
    print("6. 最新のテンプレート一覧確認")
    result = await list_templates()
    print(f"現在のテンプレート数: {len(result.get('templates', []))}")
    for template in result.get('templates', []):
        print(f"  - {template['title']} (作成者: {template['username']})")
    print()
    
    print("=== MCP機能テスト完了 ===")

# テスト実行
asyncio.run(comprehensive_mcp_test())
```

## 3. ファイルシステムでの確認

### テンプレートファイルの確認
```bash
ls -la templates/
```

### 作成されたテンプレートファイルの内容確認
```bash
cat templates/mcp_test_template.md
cat templates/mcp*.md
```

## 4. 期待される結果

### HTTP API
- ✅ テンプレート一覧が正常に取得できる
- ✅ 新しいテンプレートが作成できる
- ✅ 作成したテンプレートが取得できる
- ✅ JSON形式で正しいレスポンスが返される

### MCP機能
- ✅ `list_templates`: テンプレート一覧を辞書形式で返す
- ✅ `register_template`: 新しいテンプレートを作成し、作成されたテンプレート情報を返す
- ✅ `get_template`: 指定されたテンプレートの詳細情報を返す
- ✅ `update_template`: テンプレートを更新し、更新後の情報を返す
- ✅ `delete_template`: テンプレートを削除し、成功メッセージを返す

### ファイルシステム
- ✅ `templates/` ディレクトリにMarkdownファイルが作成される
- ✅ ファイル名はタイトルから生成される（例: `mcp_test_template.md`）
- ✅ YAMLフロントマターが正しく設定される
- ✅ Markdownコンテンツが正しく保存される

## 5. エラーハンドリングの確認

### 存在しないテンプレートの取得
```python
result = await get_template("存在しないテンプレート")
# 期待される結果: {"error": "Template not found", "message": "..."}
```

### 重複テンプレートの作成
```python
# 同じタイトルで2回作成を試行
result = await register_template("重複テスト", "内容", "説明")
# 期待される結果: {"error": "Template already exists", "message": "..."}
```

## 6. パフォーマンステスト

### 大量テンプレートの処理
```python
import time

async def performance_test():
    start_time = time.time()
    
    # 100個のテンプレートを作成
    for i in range(100):
        await register_template(
            title=f"パフォーマンステスト{i}",
            content=f"# テスト{i}\n\nこれは{i}番目のテストテンプレートです。",
            description=f"パフォーマンステスト用のテンプレート{i}"
        )
    
    # 一覧取得
    result = await list_templates(limit=100)
    
    end_time = time.time()
    print(f"100個のテンプレート作成と取得にかかった時間: {end_time - start_time:.2f}秒")
    print(f"作成されたテンプレート数: {len(result.get('templates', []))}")

asyncio.run(performance_test())
```

## 7. トラブルシューティング

### よくある問題と解決方法

#### サーバーが起動しない
```bash
# ポートが使用中の場合
PORT=8082 ./start_server.sh
```

#### MCPツールが応答しない
```bash
# 設定確認
python -c "from app.config import settings; print(f'MCP有効: {settings.enable_mcp}')"

# ログ確認
tail -f logs/app.log  # ログファイルがある場合
```

#### テンプレートファイルが作成されない
```bash
# ディレクトリ権限確認
ls -la templates/
chmod 755 templates/
```

## 8. 継続的な監視

### 定期的なヘルスチェック
```bash
# API ヘルスチェック
curl http://localhost:8081/health

# MCP機能の簡単なテスト
python -c "
import asyncio
from app.mcp.tools import list_templates
result = asyncio.run(list_templates())
print('MCP正常' if 'templates' in result else 'MCP異常')
"
```

このガイドに従って検証を行うことで、AI Process BlueprintのMCP機能が正常に動作していることを確認できます。