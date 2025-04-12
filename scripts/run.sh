#!/bin/bash

# 環境変数ファイルがあれば読み込み
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# テンプレートディレクトリが存在しない場合は作成
mkdir -p templates

# 開発環境での実行
echo "Starting Docker containers..."
docker-compose up -d

# コンテナの状態を表示
docker-compose ps

# ログを表示
echo "Docker container logs:"
docker-compose logs -f 