#!/bin/bash

# 仮想環境の確認
if [ ! -d ".venv" ]; then
    echo "❌ 仮想環境が見つかりません。先に ./setup_env.sh を実行してください。"
    exit 1
fi

# 仮想環境をアクティベート
source .venv/bin/activate

# 必要なパッケージの確認
if ! command -v uvicorn &> /dev/null; then
    echo "❌ uvicorn がインストールされていません。先に ./setup_env.sh を実行してください。"
    exit 1
fi

# デフォルト設定
TEMPLATE_DIR=${TEMPLATE_DIR:-./templates}
PORT=${PORT:-8080}
LOG_LEVEL=${LOG_LEVEL:-info}
ENABLE_MCP=${ENABLE_MCP:-true}
ENABLE_HTTP=${ENABLE_HTTP:-true}

# テンプレートディレクトリの確認
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "📁 テンプレートディレクトリを作成します: $TEMPLATE_DIR"
    mkdir -p "$TEMPLATE_DIR"
fi

# 環境変数の設定
export TEMPLATE_DIR
export PORT
export LOG_LEVEL
export ENABLE_MCP
export ENABLE_HTTP

echo "🚀 AI Process Blueprint サーバーを起動します"
echo "📝 テンプレートディレクトリ: $TEMPLATE_DIR"
echo "🔌 ポート: $PORT"
echo "🌐 MCP有効: $ENABLE_MCP"
echo "🌐 HTTP有効: $ENABLE_HTTP"

# サーバー起動
uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level $LOG_LEVEL 