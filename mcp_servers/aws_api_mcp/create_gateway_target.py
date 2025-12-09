"""
AWS API MCP ServerをGateway MCP Server Targetとして追加
"""
import boto3
import json
import os
import urllib.parse
import sys

# 親ディレクトリのload_configをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '../../scripts'))
from load_config import load_config

REGION = os.environ.get('AWS_REGION', 'ap-northeast-1')

# 設定ファイルから読み込み
main_config = load_config()
GATEWAY_ID = main_config.get('gateway', {}).get('gateway_id')

if not GATEWAY_ID:
    print("Error: Gateway ID not found")
    sys.exit(1)

# AWS API MCP設定読み込み
aws_api_mcp_config_path = os.path.join(os.path.dirname(__file__), '../../config/aws_api_mcp_config.json')
with open(aws_api_mcp_config_path, 'r') as f:
    runtime_config = json.load(f)

# Runtime OAuth設定
runtime_oauth_file = os.path.join(os.path.dirname(__file__), '../../config/runtime_oauth_config.json')

if not os.path.exists(runtime_oauth_file):
    print("Error: runtime_oauth_config.json not found")
    print("Run deploy_step1_foundation.sh first")
    sys.exit(1)

with open(runtime_oauth_file, 'r') as f:
    oauth_config = json.load(f)
PROVIDER_ARN = oauth_config['provider_arn']

AGENT_ARN = runtime_config['agent_arn']
AGENT_ID = runtime_config['agent_id']
# Agent IDのみを使用（ARNではなく）
MCP_URL = f"https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{AGENT_ID}/invocations"
print(f"Agent ARN: {AGENT_ARN}")
print(f"Agent ID: {AGENT_ID}")
print(f"MCP URL: {MCP_URL}")

client = boto3.client('bedrock-agentcore-control', region_name=REGION)

# Gateway Target作成
print("Creating AWS API MCP Gateway Target...")
target = client.create_gateway_target(
    gatewayIdentifier=GATEWAY_ID,
    name="aws-api-mcp-v2",  # 名前を変更
    targetConfiguration={
        "mcp": {
            "mcpServer": {
                "endpoint": MCP_URL
            }
        }
    },
    credentialProviderConfigurations=[
        {
            "credentialProviderType": "OAUTH",
            "credentialProvider": {
                "oauthCredentialProvider": {
                    "providerArn": PROVIDER_ARN,
                    "scopes": []
                }
            }
        }
    ]
)

print(f"✓ AWS API MCP Target created: {target['targetId']}")
print(f"  Name: {target['name']}")
print(f"  Status: {target['status']}")

# 同期実行
print("\nSynchronizing Gateway Target...")
sync_response = client.synchronize_gateway_targets(
    gatewayIdentifier=GATEWAY_ID,
    targetIdList=[target['targetId']]
)

print(f"✓ Synchronization started")
print("\nWait 1-2 minutes for synchronization to complete")
