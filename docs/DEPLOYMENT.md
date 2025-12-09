# AgentCore DevOps Assistant - デプロイ手順

このドキュメントは、空のAWSアカウントに全リソースをデプロイする手順を説明します。

## 前提条件

### 必須ツール
- AWS CLI（設定済み）
- Python 3.11+
- eksctl
- kubectl
- Finch または Docker

### 必須情報
- Slack Bot Token
- Slack App Token
- Slack Incoming Webhook URL

## デプロイ手順

### 所要時間: 約40分

```
Step 1: 基盤リソース (5分)
  ↓
Step 2: Interceptor (2分)
  ↓
Step 2.5: Task API Lambda (3分) ← 追加
  ↓
Step 3: Gateway Targets (10分)
  ↓
Step 4: EKSデプロイ (20分)
```

---

## Step 1: 基盤リソース作成（5分）

AgentCore GatewayとMemoryを作成します。

```bash
./scripts/deploy_step1_foundation.sh
```

**作成されるリソース:**
- AgentCore Gateway
- Cognito User Pool（OAuth認証）
- AgentCore Memory（STM + LTM）

**出力ファイル:**
- `config/gateway_config.json`
- `config/memory_config.json`

---

## Step 2: Request Interceptor作成（2分）

スキーマ変換用のLambda関数を作成します。

```bash
./scripts/deploy_step2_interceptor.sh
```

**作成されるリソース:**
- Lambda Function: `agentcore-gateway-interceptor`
- IAM Role: `AgentCoreGatewayInterceptorRole`
- Gateway Interceptor設定

---

## Step 2.5: Task API完全セットアップ（5分）

Task API用のLambda、API Gateway、フロントエンドを作成します。

```bash
./scripts/deploy_step2_5_task_api.sh
```

**作成されるリソース:**
- DynamoDB: `agentcore-tasks`
- Lambda: `task-api-simple`, `task-api-read-simple`, `task-api-delete`
- REST API Gateway（API Key認証）
- S3バケット: `agentcore-task-app-{ACCOUNT_ID}`
- CloudFront Distribution

**出力ファイル:**
- `config/task_rest_api_config.json`
- `config/frontend_config.json`

---

## Step 3: Gateway Targets作成（10分）

5つのGateway Targetを作成します。

```bash
./scripts/deploy_step3_targets.sh
```

**⚠️ 重要: Gateway Target設定**

スクリプト実行後、**AWS Consoleで以下の設定を確認してください**：

1. Amazon Bedrock Console → Agent Gateways
2. Gateway ID: `agentcoredevopsgateway-*` を選択
3. Targets タブ → `task-rest-api` を選択
4. **Credentials** セクション:
   - **API key** を選択
   - **TaskAPIKeyProvider-{最新のタイムスタンプ}** を選択
   - 保存

この設定がないと、タスク作成時に"An internal error occurred"エラーが発生します。

**対話的入力:**
- Slack Incoming Webhook URL

**作成されるリソース:**
1. **Slack Webhook Target** (OpenAPI)
2. **Task REST API Gateway** (OpenAPI)
   - API Gateway (REST API)
   - Lambda: task-api-simple, task-api-read-simple, task-api-delete
   - DynamoDB: agentcore-tasks
3. **DuckDuckGo Lambda Target** (Lambda)
4. **EKS MCP Server Target** (MCP Server)
   - AgentCore Runtime
   - FastMCP Server
5. **AWS API MCP Server Target** (MCP Server) ← 新規
   - AgentCore Runtime
   - AWS API MCP Server
   - タスクアプリヘルスチェック機能

**出力ファイル:**
- `config/task_rest_api_config.json`
- `config/runtime_oauth_config.json`
- `mcp_servers/eks_mcp/eks_mcp_config.json`
- `config/aws_api_mcp_config.json`

---

## Step 4: EKSデプロイ（20分）

EKSクラスタを作成してSlack Botをデプロイします。

```bash
./scripts/deploy_step4_eks.sh
```

**対話的入力:**
- Slack Bot Token
- Slack App Token

**作成されるリソース:**
- EKS Cluster: `agentcore-demo-cluster`
- Managed NodeGroup (t3.medium × 1)
- OIDC Provider
- IAM Role: `SlackDevOpsAssistantRole`（IRSA）
- ECR Repository: `slack-devops-assistant`
- Kubernetes Resources:
  - Namespace: apps
  - ServiceAccount
  - ConfigMap
  - Secret
  - Deployment

---

## デプロイ完了後

### 動作確認

```bash
# Pod状態確認
kubectl get pods -n apps -l app=slack-devops-assistant

# ログ確認
kubectl logs -n apps -l app=slack-devops-assistant -f
```

### Slackでテスト

Slack Botをチャンネルに招待して、メンションしてテスト：

```
@bot EKSクラスタの状態を確認して
@bot 明日までにデプロイ作業のタスクを作成して
@bot Kubernetes 1.32の新機能を調べて
```

---

## トラブルシューティング

### 重要な注意事項

#### 1. Interceptor設定
**問題**: Task APIへのリクエストが失敗する

**原因**: InterceptorがMCP形式を変換してしまう

**解決策**: Interceptorは**パススルー**（変換しない）設定にする必要があります。
- `createTask`, `listTasks`はMCP形式のまま返す
- GatewayがOpenAPI仕様に基づいて自動的にHTTPリクエストに変換

#### 2. Lambda権限
**問題**: API Gateway経由でLambda実行時に500エラー

**原因**: 
- Lambda関数にDynamoDB権限がない
- Lambda関数に新しいAPI Gateway IDからの実行権限がない

**解決策**: 
```bash
# DynamoDB権限追加（Step 2.5で自動実行）
# Lambda実行権限追加（Step 3で自動実行）
```

#### 3. CORS設定
**問題**: フロントエンドからAPI呼び出し時にCORSエラー

**原因**: API GatewayにOPTIONSメソッドとCORSヘッダーがない

**解決策**: `create_task_rest_api.py`でOPTIONSメソッドを自動作成（Step 2.5で実行済み）

#### 4. Gateway Target設定
**問題**: Gateway経由でタスク作成時に"An internal error occurred"

**原因**: Gateway TargetにAPI Key Credential Providerが設定されていない

**解決策**: AWS Consoleで以下を設定：
1. Gateway Target → Credentials → **API key**を選択
2. **TaskAPIKeyProvider-{最新のタイムスタンプ}**を選択
3. 保存

---

## トラブルシューティング

### Pod起動エラー

```bash
# ログ確認
kubectl logs -n apps -l app=slack-devops-assistant

# 一般的な問題:
# 1. IAM権限不足 → scripts/create_eks_iam_role.sh再実行
# 2. イメージプル失敗 → ECRログイン確認
# 3. 環境変数不足 → ConfigMap/Secret確認
```

### Gateway接続エラー

```bash
# Gateway設定確認
cat config/gateway_config.json

# Interceptorログ確認
aws logs tail /aws/lambda/agentcore-gateway-interceptor --follow
```

---

## クリーンアップ

全リソースを削除：

```bash
# EKSクラスタ削除
eksctl delete cluster --name agentcore-demo-cluster --region ap-northeast-1

# Gateway削除
python3 << 'EOF'
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import json

with open('config/gateway_config.json', 'r') as f:
    config = json.load(f)

client = GatewayClient()
client.cleanup_gateway(config['gateway_id'], config)
EOF

# Memory削除
# （AWS Console or boto3）

# Lambda関数削除
aws lambda delete-function --function-name agentcore-gateway-interceptor
aws lambda delete-function --function-name task-api-simple
aws lambda delete-function --function-name task-api-read-simple
aws lambda delete-function --function-name task-api-delete
aws lambda delete-function --function-name duckduckgo-mcp-server

# API Gateway削除
# （AWS Console）

# DynamoDB削除
aws dynamodb delete-table --table-name agentcore-tasks
```

---

## アーキテクチャ

```
[Slack User]
    ↓
[EKS Pod: Slack Bot + Strands Agent]
    ↓
[AgentCore Gateway]
    ↓
[Request Interceptor Lambda]
    ↓
┌───┴────┬──────────┬──────────┬──────────┐
↓        ↓          ↓          ↓          ↓
Slack    Task API   DuckDuckGo EKS MCP
Webhook  REST API   Lambda     Runtime
```

---

## 設定ファイル

デプロイ後、以下の設定ファイルが生成されます：

- `config/gateway_config.json` - Gateway設定
- `config/memory_config.json` - Memory設定
- `config/task_rest_api_config.json` - Task API設定
- `config/runtime_oauth_config.json` - Runtime OAuth設定
- `mcp_servers/eks_mcp/eks_mcp_config.json` - EKS MCP設定

**⚠️ 注意:** これらのファイルには認証情報が含まれるため、Gitにコミットしないでください。
