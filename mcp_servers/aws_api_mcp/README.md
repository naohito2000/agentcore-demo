# AWS API MCP Server

AWS API MCP ServerをAgentCore Runtimeにデプロイし、AgentCore Gateway経由でアクセス可能にします。

## 概要

AWS API MCP Serverは15,000以上のAWS APIへのアクセスを提供し、タスクアプリのヘルスチェック機能を実現します。

## デプロイ

### 前提条件

- AgentCore Gateway、Runtime、Memoryがデプロイ済み
- OAuth2 Credential Provider設定済み（`config/runtime_oauth_config.json`）
- AWS CLIとPython 3.11+がインストール済み

### デプロイ手順

```bash
# 1. AgentCore Runtimeにデプロイ
cd mcp_servers/aws_api_mcp
python3 deploy_runtime.py

# 2. 60秒待機（Runtimeの起動を待つ）
sleep 60

# 3. Gateway Target作成
python3 create_gateway_target.py
```

### 設定ファイル

デプロイ後、以下のファイルが生成されます：

- `config/aws_api_mcp_config.json` - Runtime設定（Agent ARN、MCP URL等）

## 監視対象リソース

### CloudFront Distribution
- 状態確認: `aws cloudfront get-distribution`
- メトリクス: `aws cloudwatch get-metric-statistics`

### S3バケット
- 状態確認: `aws s3api head-bucket`
- メトリクス: `aws cloudwatch get-metric-statistics`

### API Gateway REST API
- 状態確認: `aws apigateway get-rest-api`
- メトリクス: `aws cloudwatch get-metric-statistics`

### Lambda関数
- 状態確認: `aws lambda get-function`
- ログ: `aws logs filter-log-events`

### DynamoDBテーブル
- 状態確認: `aws dynamodb describe-table`
- アイテム数: `aws dynamodb scan --select COUNT`

## IAM権限

AWS API MCP ServerのExecution Roleには以下の権限が必要です：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:GetDistribution",
        "s3:HeadBucket",
        "s3:GetBucketLocation",
        "apigateway:GET",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "dynamodb:DescribeTable",
        "dynamodb:Scan",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:GetMetricData",
        "logs:FilterLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## トラブルシューティング

### Runtime起動エラー

```bash
# Runtime状態確認
aws bedrock-agentcore-runtime get-agent-runtime \
  --agent-id <agent-id> \
  --region ap-northeast-1
```

### Gateway Target同期エラー

```bash
# Target状態確認
aws bedrock-agentcore-control get-gateway-target \
  --gateway-identifier <gateway-id> \
  --target-id <target-id> \
  --region ap-northeast-1
```

### ツール一覧確認

```bash
# Gateway経由でツール一覧取得
python3 ../../scripts/test_gateway_tools.py
```
