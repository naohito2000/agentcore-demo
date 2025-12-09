FROM 246283478365.dkr.ecr.ap-northeast-1.amazonaws.com/bedrock-agentcore-aws_api_mcp_server:1.1.7

# 環境変数設定（タイポ修正版）
ENV AUTH_TYPE=no-auth \
    AWS_API_MCP_HOST=0.0.0.0 \
    AWS_API_MCP_PORT=8000 \
    AWS_API_MCP_STATELESS_HTTP=true \
    AWS_API_MCP_TRANSPORT=streamable-http \
    AWS_API_MCP_ALLOWED_HOSTS=* \
    AWS_API_MCP_ALLOWED_ORIGINS=* \
    AWS_REGION=ap-northeast-1

EXPOSE 8000
