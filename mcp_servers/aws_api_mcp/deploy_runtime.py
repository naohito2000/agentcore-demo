"""
AWS API MCP ServerをAgentCore Runtimeにデプロイ
"""
import boto3
import os
import json
import re
import sys
from bedrock_agentcore_starter_toolkit import Runtime

# 設定ファイル読み込み
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
config_path = os.path.join(os.path.dirname(__file__), '../../config/gateway_config.json')

if not os.path.exists(config_path):
    print("Error: config/gateway_config.json not found")
    print("Run deploy_step1_foundation.sh first")
    sys.exit(1)

with open(config_path, 'r') as f:
    gateway_config = json.load(f)

# Cognito設定を動的に取得
token_endpoint = gateway_config['token_endpoint']
match = re.search(r'https://([^.]+)\.auth\.([^.]+)\.amazoncognito\.com', token_endpoint)

if not match:
    print("Error: Could not parse token_endpoint")
    sys.exit(1)

domain = match.group(1)
REGION = match.group(2)

# Runtime OAuth設定読み込み
runtime_oauth_path = os.path.join(os.path.dirname(__file__), '../../config/runtime_oauth_config.json')

if os.path.exists(runtime_oauth_path):
    with open(runtime_oauth_path, 'r') as f:
        runtime_oauth = json.load(f)
    
    COGNITO_CLIENT_ID = runtime_oauth['client_id']
    COGNITO_USER_POOL_ID = runtime_oauth['user_pool_id']
    ALLOWED_CLIENTS = [gateway_config['client_id'], runtime_oauth['client_id']]
    
    print(f"Using Runtime OAuth Client: {COGNITO_CLIENT_ID}")
else:
    print("Error: config/runtime_oauth_config.json not found")
    print("This file should be created by deploy_step3_targets.sh (Step 3.4.1)")
    sys.exit(1)

DISCOVERY_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/openid-configuration"

print("Deploying AWS API MCP Server to AgentCore Runtime...")

# Runtime設定
runtime = Runtime()

runtime.configure(
    entrypoint="mcp_server.py",
    protocol="MCP",
    agent_name="aws_api_mcp_server",
    auto_create_execution_role=True,
    authorizer_configuration={
        "customJWTAuthorizer": {
            "allowedClients": ALLOWED_CLIENTS,
            "discoveryUrl": DISCOVERY_URL
        }
    }
)

print("Launching Runtime...")
launch_result = runtime.launch()

agent_arn = launch_result.agent_arn
agent_id = agent_arn.split('/')[-1]
print(f"\n✓ Runtime deployed successfully!")
print(f"Agent ARN: {agent_arn}")
print(f"Agent ID: {agent_id}")

# MCP Server URL生成
mcp_url = f"https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{agent_id}/invocations"
print(f"MCP Server URL: {mcp_url}")

# 設定を保存
config = {
    "agent_arn": agent_arn,
    "agent_id": agent_id,
    "mcp_url": mcp_url,
    "region": REGION
}

config_output_path = os.path.join(os.path.dirname(__file__), '../../config/aws_api_mcp_config.json')
with open(config_output_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"\nConfiguration saved to: {config_output_path}")
print("\nNext: Create Gateway Target using this MCP Server URL")
