# ベースイメージをシンプルに
FROM python:3.10-slim

# 作業ディレクトリ設定
WORKDIR /app

# 必要最低限の環境変数
ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    TEMPLATE_DIR=/app/templates \
    LOG_LEVEL=info \
    ENABLE_MCP=true \
    ENABLE_HTTP=true

# 依存関係ファイルのコピーとuvでのインストール
COPY requirements.txt .
RUN pip install uv && \
    uv pip install -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# テンプレートディレクトリの作成
RUN mkdir -p /app/templates && chmod 755 /app/templates

# ヘルスチェックの設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# エントリーポイントの設定
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"] 