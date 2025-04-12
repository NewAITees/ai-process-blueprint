# ベースイメージの選択
FROM python:3.10-slim

# 作業ディレクトリの設定
WORKDIR /app

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    TEMPLATE_DIR=/app/templates \
    LOG_LEVEL=info \
    ENABLE_MCP=true \
    ENABLE_HTTP=true

# 依存関係ファイルのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# テンプレートディレクトリの作成と権限設定
RUN mkdir -p /app/templates && \
    chmod 755 /app/templates

# ヘルスチェックの設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# エントリーポイントの設定
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"] 