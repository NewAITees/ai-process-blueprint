# AI Process Blueprint

<div align="center">
  <img src="https://via.placeholder.com/150" alt="AI Process Blueprint ロゴ">
  <p>テンプレートベースでAIに作業手順を提供するサービス</p>
</div>

## 👋 はじめに

AI Process Blueprint は、AIに対して明確な作業手順を提供するためのテンプレートを管理するサービスです。ユーザーは作業テンプレートを登録し、AIはそのテンプレートに従って一貫性のある方法でタスクを実行します。

### 📌 主な機能

- **テンプレート管理**: 作業手順テンプレートの作成・取得・更新・削除
- **多重インターフェース**: HTTP API と MCP（Model Context Protocol）の両方をサポート
- **軽量アーキテクチャ**: Docker コンテナで簡単にデプロイ可能
- **Markdown 対応**: 豊かな表現が可能なMarkdown形式でテンプレートを記述

## 🚀 クイックスタート

### Docker を使用した起動

```bash
# イメージをビルド
docker build -t ai-process-blueprint .

# コンテナを起動
docker run -d -p 8080:8080 -v blueprint-data:/app/data ai-process-blueprint
```

### API エンドポイント

| エンドポイント | メソッド | 説明 |
|--------------|--------|------|
| `/api/templates` | GET | テンプレート一覧の取得 |
| `/api/templates/{title}` | GET | 指定タイトルのテンプレート取得 |
| `/api/templates` | POST | 新規テンプレートの登録 |
| `/api/templates/{title}` | PUT | 既存テンプレートの更新 |
| `/api/templates/{title}` | DELETE | テンプレートの削除 |

詳細は [API ドキュメント](API_DOCUMENTATION.md) を参照してください。

## 🧩 使用例

### 1. テンプレートの登録

```bash
curl -X POST http://localhost:8080/api/templates \
  -H "Content-Type: application/json" \
  -d '{
    "title": "データ分析レポート作成",
    "content": "# データ分析レポート\n\n## 1. データセットの理解\n- データソースを特定\n- 各列の意味を把握\n- 基本統計量を計算\n\n## 2. データクリーニング\n- 欠損値の処理\n- 外れ値の検出と処理\n- データ型の変換\n\n## 3. 探索的データ分析\n- 分布の可視化\n- 相関関係の分析\n- パターンの発見\n\n## 4. 結論と洞察\n- 主要な発見事項\n- ビジネスへの示唆\n- 次のステップ",
    "description": "データ分析プロジェクトを体系的に進めるためのガイド",
    "username": "data_analyst"
  }'
```

### 2. テンプレートの取得

```bash
curl http://localhost:8080/api/templates/データ分析レポート作成
```

### 3. AI アシスタントからの利用 (MCP)

AI アシスタントは MCP インターフェースを通じて直接テンプレートにアクセスできます。

```python
# AI アシスタントからのアクセス例
result = await get_template(title="データ分析レポート作成")
print(f"テンプレート内容: {result['content']}")
```

## 🛠️ 開発

開発環境のセットアップと貢献方法については [開発セットアップガイド](DEVELOPMENT_SETUP.md) を参照してください。

## 📐 アーキテクチャ

サービスのアーキテクチャについては [アーキテクチャドキュメント](ARCHITECTURE.md) を参照してください。

## 📝 ライセンス

MIT License
