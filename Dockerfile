# ベースイメージの選択
FROM python:3.10-slim

# 作業ディレクトリの設定
WORKDIR /app

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    TEMPLATE_DIR=/app/templates

# 依存関係ファイルのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# テンプレートディレクトリの作成と権限設定
RUN mkdir -p /app/templates && \
    chmod 755 /app/templates

# エントリーポイントの設定
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8080}"] 