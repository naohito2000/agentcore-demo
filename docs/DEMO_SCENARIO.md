# AgentCore DevOps Assistant - デモシナリオ

このデモは、AgentCoreの4つの主要機能を実際のDevOps業務フローで紹介します。

## デモの目的

**AgentCoreの価値提案を実証:**
- **Memory**: 会話履歴とコンテキストの永続化
- **Gateway**: 複数ツールの統合と管理
- **Identity**: セキュアな認証・認可
- **Observability**: 実行状況の可視化

## デモ環境

- **Slack**: ユーザーインターフェース
- **EKS**: エージェント実行環境
- **AgentCore**: Memory、Gateway、Runtime

---

## シナリオ1: Memory - セッション内記憶とクロスセッション記憶

**目的:** AgentCore Memoryの短期記憶（STM）と長期記憶（LTM）を実証

### デモフロー

#### Part 1: セッション内記憶（Short-term Memory）

**Slackスレッド1で:**

```
ユーザー: @bot 私の名前はTaroです。今日はKubernetes 1.32のアップグレードを予定しています。
Bot: 了解しました、Taroさん！Kubernetes 1.32へのアップグレード作業ですね。
     何かサポートできることはありますか？

ユーザー: さっき話したアップグレードのタスクを作成して
Bot: はい、Kubernetes 1.32アップグレードのタスクを作成しますね！
     [createTask実行]
     ✓ タスクを作成しました！
```

**技術的な動作:**
```
1. 最初のメッセージ
   → Memory.create_event()
   → actor_id: U12345678（Slackユーザー）
   → session_id: 1234567890.111111（スレッドTS）

2. 2番目のメッセージ
   → Memory.get_last_k_turns(k=3)
   → 同じsession_idから会話履歴取得
   → "Kubernetes 1.32アップグレード"を参照
```

**ポイント:**
- ✅ 同じスレッド内で「さっき話した」を理解
- ✅ Short-term Memoryが会話履歴を保持
- ✅ Slackスレッド = Memoryセッション

#### Part 2: クロスセッション記憶（Long-term Memory）

**Slackスレッド2（別スレッド）で:**

```
ユーザー: @bot 私が予定していた作業を教えて
Bot: Taroさんが予定されていたのは、Kubernetes 1.32へのアップグレード作業ですね。
     タスクも作成済みです。

ユーザー: 私の名前も覚えてる？
Bot: はい、Taroさんですね！
```

**技術的な動作:**
```
1. 別スレッドでのメッセージ
   → session_id: 1234567890.222222（異なる）
   → Short-term Memoryでは取得できない

2. Long-term Memory検索
   → actor_id: U12345678（同じユーザー）
   → Semantic Memory: "名前: Taro"
   → User Preference: "Kubernetes 1.32アップグレード予定"
```

**ポイント:**
- ✅ 別スレッドでも情報を記憶
- ✅ Long-term Memoryがユーザー情報を抽出・保持
- ✅ Actor ID（Slackユーザー）で記憶を分離

**メッセージング:**
> "AgentCore Memoryは、会話履歴（STM）と重要情報の抽出（LTM）を自動化。
> Slackスレッド単位でセッション管理し、ユーザー単位で長期記憶を保持。
> エージェントがユーザーのコンテキストを理解し、パーソナライズされた応答を実現。"

**デモ時の説明:**
```
Memory設定:
- STM: Slackスレッド単位で会話履歴を保存
- LTM: ユーザー単位で重要情報を抽出
- Actor ID: Slackユーザー（U12345678）
- Session ID: スレッドタイムスタンプ（1234567890.111111）

これにより、同じスレッド内では会話が継続し、
別スレッドでもユーザー情報を記憶できます。
```

---

## シナリオ3: Identity - セキュアな認証統合

**目的:** インバウンド/アウトバウンド認証とToken Vaultを実証

### デモフロー

#### Part 1: 認証フローの全体像

**アーキテクチャ図を表示（画像のシナリオ#4）:**

```
【インバウンド認証】
エージェント/ユーザー
  ↓ (Bearer Token)
AgentCore Gateway
  ↓ (Cognito JWT検証)
  ↓ (discovery_url、allowed_clients確認)
✅ 認証成功

【アウトバウンド認証】
AgentCore Gateway
  ↓ (Token Vault参照)
AgentCore Identity
  ↓ (Credential Provider取得)
  ↓ (API Key or OAuth Token)
外部サービス（Task API、Slack、Runtime）
```

**説明:**
```
AgentCore Identityは、2つの役割を担います:

1. インバウンド認証（Gateway自身の認証）
   - Cognito（外部IdP）でユーザー/エージェントを認証
   - JWT検証
   - allowed_clients、allowed_audiencesで制御

2. アウトバウンド認証（Gatewayからツールへの認証）
   - Token Vaultで認証情報を一元管理
   - Credential Providers:
     * API Key Provider（Task API、Slack）
     * OAuth Provider（Runtime MCP）
   - Gatewayが自動的に適切な認証情報を付与
```

#### Part 2: Token Vaultの実演

**AWS Console表示:**
- Identity → Credential Providers
- 5つのProviderを表示

**説明:**
```
Token Vaultに保存されている認証情報:
1. TaskAPIKeyProvider-v2
   - Task REST APIのAPI Key
   - x-api-keyヘッダーに自動付与

2. RuntimeMCPOAuthProvider-final
   - Runtime専用のOAuth Client
   - Gatewayが自動的にトークン取得・付与

3. SlackWebhookDummyProvider
   - Slack Webhook用（形式的）

全てセキュアに暗号化保存され、
エージェントコードには一切記述されていません。
```

#### Part 3: コード表示

**strands_agent/tools/gateway_tools.py を表示:**

```python
# 認証情報なし！
class GatewayToolProvider:
    def __init__(self):
        self.gateway_url = os.environ["GATEWAY_URL"]
        # Client ID/Secretは環境変数（Inbound認証用）
        # Outbound認証情報は一切記述されていない
```

**説明:**
```
エージェントコードには:
- ✅ Gateway URL
- ✅ Inbound認証情報（Client ID/Secret）
- ❌ Outbound認証情報（API Key、OAuth）

Outbound認証情報は全てToken Vaultで管理され、
Gatewayが自動的に使用します。
```

#### Part 4: 実際の認証フロー

**Slackで:**
```
ユーザー: @bot EKSクラスタを確認して、タスク化して、通知して
Bot: [処理中...]
     
     1. EKS確認
        → Inbound: JWT（Cognito）
        → Outbound: OAuth（RuntimeMCPOAuthProvider）
     
     2. タスク作成
        → Inbound: JWT（Cognito）
        → Outbound: API Key（TaskAPIKeyProvider）
     
     3. Slack通知
        → Inbound: JWT（Cognito）
        → Outbound: API Key（SlackWebhookDummyProvider）
     
     ✓ 全て完了！
```

**ポイント:**
- ✅ 1つのリクエストで3つの異なるOutbound認証
- ✅ 全てToken Vaultから自動取得
- ✅ エージェントは認証を意識しない

**メッセージング:**
> "AgentCore Identityは、インバウンド/アウトバウンド認証を統合管理。
> Cognitoで外部IdP統合、Token Vaultで認証情報を一元管理。
> エージェントコードに認証情報を記述せず、セキュアで保守性の高い
> アーキテクチャを実現。"

**デモ時の強調ポイント:**
1. **Token Vault画面** - 5つのCredential Providers
2. **コード表示** - 認証情報がないこと
3. **実行** - 複数の認証方式を自動使用
4. **セキュリティ** - 暗号化保存、ローテーション容易

---

**目的:** Gateway Interceptorsと複数Target Typeの統合を実証

### デモフロー

#### Part 1: OpenAPI Target（Slack通知）

```
ユーザー: @bot デプロイ完了を#team-devに通知して
Bot: #team-devに通知しますね！
     [slack-webhook___notifySlack実行]
     ✓ 通知を送信しました！
```

**ポイント:**
- ✅ OpenAPI Target（Slack Incoming Webhook）
- ✅ Interceptorがスキーマ変換（message → text）
- ✅ API Key認証

#### Part 2: OpenAPI Target（Task API）

```
ユーザー: @bot タスク一覧を表示して
Bot: 現在のタスク一覧です：
     1. Kubernetes 1.32アップグレード（優先度: 高）
     2. デプロイ作業（優先度: 中）
     [task-rest-api___listTasks実行]
```

**ポイント:**
- ✅ OpenAPI Target（REST API Gateway）
- ✅ Interceptorがスキーマ変換
- ✅ API Key認証

#### Part 3: Lambda Target（DuckDuckGo検索）

```
ユーザー: @bot Kubernetes 1.32の新機能を調べて
Bot: Kubernetes 1.32の主な新機能を調べました：
     - Feature Gate の改善
     - ...
     [duckduckgo-search___search実行]
```

**ポイント:**
- ✅ Lambda Target
- ✅ Gateway IAM Role認証
- ✅ 外部API統合

#### Part 4: MCP Server Target（EKS監視）

```
ユーザー: @bot EKSクラスタの状態を確認して
Bot: EKSクラスタの状態を確認しました：
     - クラスタ: agentcore-demo-cluster
     - ステータス: ACTIVE
     - バージョン: 1.32
     [eks-mcp-v2___list_clusters, describe_cluster実行]
```

**ポイント:**
- ✅ MCP Server Target（AgentCore Runtime）
- ✅ OAuth認証
- ✅ FastMCP実装

**メッセージング:**
> "AgentCore Gatewayは、OpenAPI、Lambda、MCP Serverなど複数のTarget Typeを統合。
> Interceptorsで統一的なスキーマ変換を実現し、エージェントからシームレスにアクセス。"

---

## シナリオ3: Identity - セキュアな認証・認可

**目的:** 多層認証とIRSAを実証

### デモフロー

#### Part 1: 認証フローの説明

**アーキテクチャ図を表示:**

```
[Slack User]
    ↓ (Slack Token)
[EKS Pod]
    ↓ (IRSA - IAM Role)
[AgentCore Gateway]
    ↓ (JWT - Cognito)
[Gateway Interceptor]
    ↓ (OAuth - Runtime専用)
[AgentCore Runtime]
    ↓ (IAM - EKS API)
[AWS Services]
```

**説明:**
1. **Slack認証** - Bot Token、App Token
2. **IRSA** - EKS PodがIAM Roleを取得
3. **Gateway Inbound** - JWT（Cognito）でGateway認証
4. **Gateway Outbound** - OAuth（Runtime専用）でRuntime呼び出し
5. **AWS API** - IAM RoleでEKS API呼び出し

#### Part 2: 実際の認証フロー

```
ユーザー: @bot EKSクラスタを確認して、問題があればタスク化して通知して
Bot: [処理中...]
     
     1. EKSクラスタ確認（OAuth認証 → Runtime）
     2. タスク作成（API Key認証 → REST API）
     3. Slack通知（API Key認証 → Webhook）
     
     ✓ 全て完了しました！
```

**ポイント:**
- ✅ 1つのリクエストで3つの異なる認証方式
- ✅ Gateway Interceptorが認証ヘッダーを適切に処理
- ✅ セキュアな多層認証

**メッセージング:**
> "AgentCore Identityは、JWT、OAuth、API Key、IAMなど複数の認証方式を統合。
> Gateway Interceptorsで認証ヘッダーを動的に変換し、セキュアなツールアクセスを実現。"

---

## シナリオ4: Observability - 実行状況の可視化

**目的:** CloudWatch Logsでエージェント実行を追跡

### デモフロー

#### Part 1: リアルタイムログ表示

**ターミナル1（Interceptorログ）:**
```bash
aws logs tail /aws/lambda/agentcore-gateway-interceptor --follow
```

**ターミナル2（Runtimeログ）:**
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/eks_mcp_server-xxx-DEFAULT --follow
```

**ターミナル3（Podログ）:**
```bash
kubectl logs -n apps -l app=slack-devops-assistant -f
```

#### Part 2: エージェント実行

**Slackで:**
```
ユーザー: @bot EKSクラスタの状態を確認してタスク化して
```

**ログに表示される内容:**

**Interceptorログ:**
```
Tool name: list_clusters
Transformed eks-mcp: passthrough
Tool name: createTask
Transformed task-api: title=EKS状態確認
```

**Runtimeログ:**
```
INFO: Received request: tools/call
INFO: Executing tool: list_clusters
INFO: EKS API call: ListClusters
INFO: Response: 1 cluster found
```

**Podログ:**
```
INFO: Received Slack message
INFO: Gateway tools: 7 found
INFO: Agent processing...
INFO: Tool execution: list_clusters
INFO: Tool execution: createTask
INFO: Response sent to Slack
```

**ポイント:**
- ✅ 全レイヤーでログ出力
- ✅ リクエストフローを追跡可能
- ✅ エラー発生時の原因特定が容易

**メッセージング:**
> "AgentCore Observabilityは、Gateway、Runtime、Interceptorの全レイヤーでログを統合。
> CloudWatch Logsでリアルタイム監視し、エージェント実行を完全に可視化。"

---

## 統合デモ: 全機能を組み合わせたワークフロー

### シナリオ: インシデント対応フロー

**Slackスレッドで連続実行:**

```
ユーザー: @bot EKSクラスタの状態を確認して
Bot: クラスタ状態を確認しました。
     - クラスタ: agentcore-demo-cluster
     - ステータス: ACTIVE
     - ノード: 1個（正常）
     [Memory: EKS確認実行を記録]

ユーザー: 問題なさそうだね。念のためタスクを作成して
Bot: はい、EKS状態確認のタスクを作成しました。
     [Memory: タスク作成を記録]
     [createTask実行]

ユーザー: #opsチームに共有して
Bot: #opsチームに通知しました！
     「EKSクラスタ正常、確認タスク作成済み」
     [notifySlack実行]

--- 別のスレッド ---

ユーザー: @bot さっき何してた？
Bot: EKSクラスタの状態確認を行い、確認タスクを作成して、
     #opsチームに通知しました。
     [Memory: 別スレッドでも記憶を取得]
```

**デモのポイント:**
1. ✅ **Memory** - 会話履歴とアクション履歴を記憶
2. ✅ **Gateway** - 3つのツール（EKS、Task、Slack）をシームレスに実行
3. ✅ **Identity** - 各ツールで適切な認証方式を使用
4. ✅ **Observability** - 全実行をログで追跡

---

## デモ実施ガイド

### 準備

1. **ターミナル準備** - ログ表示用に3つ
2. **Slack準備** - デモ用チャンネル作成
3. **タスクアプリ** - ブラウザで開く（https://xxx.cloudfront.net）

### デモの流れ（15分）

**0-3分: イントロダクション**
- AgentCoreとは
- 4つの主要機能紹介

**3-6分: Memory デモ**
- シナリオ1実行
- STMとLTMの違い説明

**6-10分: Gateway デモ**
- シナリオ2実行
- 4つのTarget Type紹介
- Interceptorsの役割説明

**10-12分: Identity デモ**
- シナリオ3実行
- 認証フロー図表示
- 多層認証の説明

**12-14分: Observability デモ**
- シナリオ4実行
- ログをリアルタイム表示
- トレーシング説明

**14-15分: 統合デモ**
- 全機能を組み合わせたワークフロー
- まとめ

---

## 各機能のメッセージング

### Memory

**価値提案:**
> "エージェントに記憶を。会話履歴の永続化と重要情報の自動抽出で、
> パーソナライズされた応答を実現。"

**技術的特徴:**
- Short-term Memory: セッション内の会話履歴
- Long-term Memory: セマンティック抽出とクロスセッション記憶
- Actor/Session分離: マルチユーザー対応

### Gateway

**価値提案:**
> "ツール統合を簡単に。OpenAPI、Lambda、MCP Serverを統一的に管理。
> Interceptorsで柔軟なスキーマ変換を実現。"

**技術的特徴:**
- 4つのTarget Type: OpenAPI、Lambda、MCP Server、Smithy
- Gateway Interceptors: リクエスト/レスポンス変換
- Semantic Search: ツール検索機能

### Identity

**価値提案:**
> "セキュアなツールアクセス。JWT、OAuth、API Key、IAMを統合し、
> きめ細かいアクセス制御を実現。"

**技術的特徴:**
- Inbound認証: JWT（Cognito）
- Outbound認証: OAuth、API Key、IAM
- IRSA: EKS Pod Identity
- Fine-Grained Access Control: ツール単位の権限管理

### Observability

**価値提案:**
> "エージェント実行を完全に可視化。CloudWatch Logsで全レイヤーを監視し、
> トラブルシューティングを迅速化。"

**技術的特徴:**
- Gateway Logs: リクエスト/レスポンス
- Runtime Logs: MCP Server実行
- Interceptor Logs: スキーマ変換
- Application Logs: エージェントロジック

---

## Q&A想定

### Q1: "Memoryはどのように動作しますか？"

**A:** 
- Short-term: 会話をそのまま保存、セッション内で取得
- Long-term: LLMで重要情報を抽出、セマンティック検索で取得
- 自動化: Hooksで透過的に動作

### Q2: "Gatewayの利点は？"

**A:**
- 統一的なツール管理
- 複数の認証方式をサポート
- Interceptorsで柔軟な変換
- Semantic Searchでツール発見

### Q3: "本番環境での運用は？"

**A:**
- Runtime: マネージドでスケーラブル
- Memory: 自動バックアップ
- Gateway: 高可用性
- Observability: CloudWatch統合

---

## デモ後のアクション

**参加者に提供:**
1. GitHubリポジトリ
2. デプロイスクリプト
3. ドキュメント（DEPLOYMENT.md）
4. サンプルコード

**次のステップ:**
- 自社ユースケースでのPoC
- カスタムツール追加
- Memory戦略のカスタマイズ
