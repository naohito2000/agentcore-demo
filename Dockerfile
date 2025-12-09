FROM python:3.11-slim

WORKDIR /app

# UTF-8ロケール設定
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY slack_bot/ ./slack_bot/
COPY strands_agent/ ./strands_agent/

# 環境変数（Kubernetesで上書き）
ENV PYTHONUNBUFFERED=1

# Slack Bot起動
CMD ["python", "-m", "slack_bot.bot"]
