# API ドキュメント

このドキュメントでは、AI Process Blueprint サービスが提供するAPIインターフェースの詳細を説明します。

## 1. HTTP API

### 基本情報

- **ベースURL**: `http://<host>:<port>/api`
- **コンテンツタイプ**: `application/json`
- **文字エンコーディング**: UTF-8

### 1.1 テンプレート一覧の取得

複数のテンプレートを一覧で取得します。

**エンドポイント**:
```
GET /templates
```

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|----------|-----|------|------|
| `limit` | 整数 | いいえ | 取得するテンプレートの最大数 (デフォルト: 20, 最大: 100) |
| `offset` | 整数 | いいえ | 結果セットの開始位置 (デフォルト: 0) |
| `username` | 文字列 | いいえ | 特定ユーザーのテンプレートのみをフィルタリング |

**レスポンス**:

- **ステータスコード**: 200 OK

```json
{
  "templates": [
    {
      "title": "データ分析レポート作成",
      "content": "# データ分析レポート\n\n...",
      "description": "データ分析プロジェクトを体系的に進めるためのガイド",
      "username": "data_analyst",
      "created_at": "2025-04-11T10:30:00Z",
      "updated_at": "2025-04-11T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### 1.2 特定テンプレートの取得

タイトルを指定して単一のテンプレートを取得します。

**エンドポイント**:
```
GET /templates/{title}
```

**パスパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|----------|-----|------|------|
| `title` | 文字列 | はい | 取得するテンプレートのタイトル |

**レスポンス**:

- **ステータスコード**: 200 OK

```json
{
  "title": "データ分析レポート作成",
  "content": "# データ分析レポート\n\n## 1. データセットの理解\n- データソースを特定\n- 各列の意味を把握\n- 基本統計量を計算\n\n## 2. データクリーニング\n- 欠損値の処理\n- 外れ値の検出と処理\n- データ型の変換\n\n## 3. 探索的データ分析\n- 分布の可視化\n- 相関関係の分析\n- パターンの発見\n\n## 4. 結論と洞察\n- 主要な発見事項\n- ビジネスへの示唆\n- 次のステップ",
  "description": "データ分析プロジェクトを体系的に進めるためのガイド",
  "username": "data_analyst",
  "created_at": "2025-04-11T10:30:00Z",
  "updated_at": "2025-04-11T10:30:00Z"
}
```

- **ステータスコード**: 404 Not Found

```json
{
  "error": "Template not found",
  "message": "指定されたタイトルのテンプレートが見つかりません"
}
```

### 1.3 テンプレートの作成

新しいテンプレートを登録します。

**エンドポイント**:
```
POST /templates
```

**リクエストボディ**:

```json
{
  "title": "会議議事録作成",
  "content": "# 会議議事録\n\n## 基本情報\n- 日時: [日付と時間]\n- 参加者: [参加者リスト]\n- 場所: [会議場所/オンライン]\n\n## アジェンダ\n1. [議題1]\n2. [議題2]\n3. [議題3]\n\n## 議論内容\n### [議題1]\n- [ポイント1]\n- [ポイント2]\n\n### [議題2]\n- [ポイント1]\n- [ポイント2]\n\n## 決定事項\n- [決定1]\n- [決定2]\n\n## アクションアイテム\n- [ ] [タスク1] - 担当: [名前], 期限: [日付]\n- [ ] [タスク2] - 担当: [名前], 期限: [日付]",
  "description": "効果的な会議議事録を作成するためのテンプレート",
  "username": "project_manager"
}
```

**必須フィールド**:
- `title`: テンプレートのタイトル（一意）
- `content`: Markdown形式のテンプレート内容

**オプションフィールド**:
- `description`: テンプレートの説明（デフォルト: 空文字列）
- `username`: 作成者名（デフォルト: "anonymous"）

**レスポンス**:

- **ステータスコード**: 201 Created

```json
{
  "title": "会議議事録作成",
  "content": "# 会議議事録\n\n## 基本情報\n...(省略)...",
  "description": "効果的な会議議事録を作成するためのテンプレート",
  "username": "project_manager",
  "created_at": "2025-04-11T15:20:00Z",
  "updated_at": "2025-04-11T15:20:00Z"
}
```

- **ステータスコード**: 422 Unprocessable Entity

```json
{
  "error": "Validation Error",
  "message": "Template title cannot be empty"
}
```

- **ステータスコード**: 409 Conflict

```json
{
  "error": "Template already exists",
  "message": "同じタイトルのテンプレートが既に存在します"
}
```

### 1.4 テンプレートの更新

既存のテンプレートを更新します。

**エンドポイント**:
```
PUT /templates/{title}
```

**パスパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|----------|-----|------|------|
| `title` | 文字列 | はい | 更新するテンプレートのタイトル |

**リクエストボディ**:

```json
{
  "content": "# 更新されたテンプレート内容\n\n...",
  "description": "更新された説明文",
  "username": "editor"
}
```

**オプションフィールド**:
- `content`: 更新後のテンプレート内容
- `description`: 更新後の説明文
- `username`: 更新者名

**レスポンス**:

- **ステータスコード**: 200 OK

```json
{
  "title": "会議議事録作成",
  "content": "# 更新されたテンプレート内容\n\n...",
  "description": "更新された説明文",
  "username": "editor",
  "created_at": "2025-04-11T15:20:00Z",
  "updated_at": "2025-04-11T16:45:00Z"
}
```

- **ステータスコード**: 404 Not Found

```json
{
  "error": "Template not found",
  "message": "指定されたタイトルのテンプレートが見つかりません"
}
```

### 1.5 テンプレートの削除

テンプレートを削除します。

**エンドポイント**:
```
DELETE /templates/{title}
```

**パスパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|----------|-----|------|------|
| `title` | 文字列 | はい | 削除するテンプレートのタイトル |

**レスポンス**:

- **ステータスコード**: 204 No Content

- **ステータスコード**: 404 Not Found

```json
{
  "error": "Template not found",
  "message": "指定されたタイトルのテンプレートが見つかりません"
}
```

## 2. MCP インターフェース

MCP (Model Context Protocol) インターフェースは、AI アシスタントが直接テンプレートを操作するための機能を提供します。

### 2.1 MCP ツール定義

```json
{
  "tools": [
    {
      "name": "get_template",
      "description": "指定したタイトルのテンプレートを取得します",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "取得するテンプレートのタイトル"
          }
        },
        "required": ["title"]
      }
    },
    {
      "name": "list_templates",
      "description": "テンプレート一覧を取得します",
      "parameters": {
        "type": "object",
        "properties": {
          "limit": {
            "type": "integer",
            "description": "取得するテンプレートの最大数（オプション、デフォルト: 20）"
          },
          "offset": {
            "type": "integer",
            "description": "結果セットの開始位置（オプション、デフォルト: 0）"
          },
          "username": {
            "type": "string",
            "description": "特定ユーザーのテンプレートのみをフィルタリング（オプション）"
          }
        }
      }
    },
    {
      "name": "register_template",
      "description": "新しいテンプレートを登録します",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "テンプレートのタイトル"
          },
          "content": {
            "type": "string",
            "description": "Markdown形式のテンプレート内容"
          },
          "description": {
            "type": "string",
            "description": "テンプレートの説明（オプション、デフォルト: 空文字列）"
          },
          "username": {
            "type": "string",
            "description": "作成者のユーザー名（オプション、デフォルト: ai_assistant）"
          }
        },
        "required": ["title", "content"]
      }
    },
    {
      "name": "update_template",
      "description": "既存のテンプレートを更新します",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "更新するテンプレートのタイトル"
          },
          "content": {
            "type": "string",
            "description": "新しいテンプレート内容（オプション）"
          },
          "description": {
            "type": "string",
            "description": "新しい説明（オプション）"
          },
          "username": {
            "type": "string",
            "description": "更新者のユーザー名（オプション）"
          }
        },
        "required": ["title"]
      }
    },
    {
      "name": "delete_template",
      "description": "指定したタイトルのテンプレートを削除します",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "削除するテンプレートのタイトル"
          }
        },
        "required": ["title"]
      }
    }
  ]
}
```

### 2.2 MCP ツール使用例

#### テンプレート取得

```python
result = await get_template(title="データ分析レポート作成")
if "error" not in result:
    print(f"テンプレート: {result['title']}")
    print(f"内容: {result['content']}")
else:
    print(f"エラー: {result['message']}")
```

#### テンプレート一覧取得

```python
result = await list_templates(limit=5, offset=0)
if "templates" in result:
    for template in result['templates']:
        print(f"- {template['title']} (作成者: {template['username']})")
else:
    print(f"エラー: {result.get('message', '不明なエラー')}")
```

#### テンプレート登録

```python
result = await register_template(
    title="新しいテンプレート",
    content="# 新しいテンプレート\n\n## セクション1\n...",
    description="テスト用テンプレート",
    username="tester"
)
if "error" not in result:
    print(f"作成成功: {result['title']}")
else:
    print(f"エラー: {result['message']}")
```

## 3. エラーレスポンス

共通のエラーレスポンスとそのステータスコードを示します。

| エラー | HTTPステータス | レスポンス形式 |
|-------|--------------|-------------|
| テンプレートが見つからない | 404 | `{"error": "Template not found", "message": "..."}` |
| テンプレートが既に存在する | 409 | `{"error": "Template already exists", "message": "..."}` |
| 入力バリデーションエラー | 422 | `{"error": "Validation Error", "message": "..."}` |
| サーバー内部エラー | 500 | `{"error": "Internal Server Error", "message": "..."}` |

## 4. データモデル

### 4.1 Template

テンプレートはMarkdownファイルとして保存され、メタデータはYAMLフロントマターとして各ファイルの先頭に記述されます。

#### 4.1.1 ファイル構造

```
templates/
  ├── データ分析レポート作成.md
  ├── 会議議事録作成.md
  ├── バグ修正手順.md
  └── ...
```

#### 4.1.2 テンプレートファイル形式

```markdown
---
title: "データ分析レポート作成"
description: "データ分析プロジェクトを体系的に進めるためのガイド"
username: "data_analyst"
created_at: "2025-04-11T10:30:00Z"
updated_at: "2025-04-11T10:30:00Z"
---

# データ分析レポート

## 1. データセットの理解
- データソースを特定
- 各列の意味を把握
- 基本統計量を計算

...（以下テンプレート内容）
```

#### 4.1.3 メタデータフィールド

| フィールド | 型 | 説明 |
|----------|-----|------|
| `title` | 文字列 | テンプレートのタイトル (一意、ファイル名にも使用) |
| `description` | 文字列 | テンプレートの説明 |
| `username` | 文字列 | 作成者/更新者のユーザー名 |
| `created_at` | ISO8601文字列 | 作成日時 |
| `updated_at` | ISO8601文字列 | 最終更新日時 |

## 5. 制限事項

- テンプレートタイトルは最大100文字
- テンプレート内容は最大100KBまで
- 1分あたりの最大リクエスト数: 60
- 同時接続数の上限: 100

## 6. バージョニング

このAPIはセマンティックバージョニングに従います。現在のバージョンは v1.0 です。

APIのバージョンはURLパスに含まれます。例: `/api/v1/templates`