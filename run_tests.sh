#!/bin/bash

# 古いテスト結果をクリーンアップ
rm -rf htmlcov/* test-results/*

# Dockerイメージをビルドしてテストを実行
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# テスト終了後にコンテナを削除
docker-compose -f docker-compose.test.yml down

# テスト結果の表示
echo "Test results are available in test-results/junit.xml"
echo "Coverage report is available in htmlcov/index.html" 