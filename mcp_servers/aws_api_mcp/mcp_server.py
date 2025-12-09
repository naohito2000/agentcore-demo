"""
AWS API MCP Server - AgentCore Runtime Entrypoint
"""
import os
import sys

# AWS API MCP Serverをインポート
# AgentCore Runtimeは公式イメージを使用するため、
# このファイルは最小限の設定のみ行う

# 環境変数設定
os.environ.setdefault('AWS_REGION', 'ap-northeast-1')
os.environ.setdefault('READ_OPERATIONS_ONLY', 'false')

# AWS API MCP Serverのメインモジュールを実行
from awslabs.aws_api_mcp_server import server

if __name__ == "__main__":
    server.main()
