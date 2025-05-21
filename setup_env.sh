#!/bin/bash

# 仮想環境のディレクトリ名
VENV_DIR=".venv"

# 必要なコマンドの存在確認
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 がインストールされていません"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "❌ curl がインストールされていません"; exit 1; }

# UVのインストール（システム全体にインストール）
echo "📦 UVをインストールします..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # PATHの更新
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 仮想環境が存在しない場合は作成
if [ ! -d "$VENV_DIR" ]; then
    echo "🌱 仮想環境を作成します..."
    uv venv $VENV_DIR
fi

# 仮想環境をアクティベート
echo "🔌 仮想環境をアクティベートします..."
source $VENV_DIR/bin/activate

# 依存関係のインストール
echo "📚 依存関係をインストールします..."
uv pip install -r requirements.txt

# 開発用パッケージのインストール
echo "🔧 開発用パッケージをインストールします..."
uv pip install -e .

echo "✨ セットアップが完了しました！"
echo "🚀 サーバーを起動するには:"
echo "   source $VENV_DIR/bin/activate  # 仮想環境をアクティベート"
echo "   ./start_server.sh              # サーバーを起動" 