#!/bin/bash

# 古いテスト結果をクリーンアップ
rm -rf htmlcov/* test-results/*

# テストディレクトリが存在しない場合は作成
mkdir -p test-results

# 環境変数を設定
export PYTHONPATH=$PYTHONPATH:$(pwd)
export TEMPLATE_DIR=$(pwd)/test_templates
mkdir -p $TEMPLATE_DIR

# Pythonの直接実行でテストを実行
echo "Running tests..."
python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing --junitxml=test-results/junit.xml

# 終了コードを保存
TEST_EXIT_CODE=$?

# テスト結果の表示
echo "Test results are available in test-results/junit.xml"
echo "Coverage report is available in htmlcov/index.html"

# テストの終了コードを返す
exit $TEST_EXIT_CODE 