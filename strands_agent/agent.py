"""Strands Agent本体"""
import os
import asyncio
from typing import Optional, Callable
from strands import Agent
from strands_agent.hooks.memory_hook import create_memory_session_manager
from strands_agent.tools.gateway_tools import GatewayToolProvider


class TaskBotAgent:
    """DevOps/タスク管理アシスタント"""
    
    SYSTEM_PROMPT = """あなたはタスクボットです。
DevOpsタスクの管理とチーム支援を行うカジュアルなアシスタントです。

## 重要な動作ルール

**段階的な報告**: 複数のツールを使用する場合、各ツール実行後に中間結果を報告してください。

例:
ユーザー: 「タスクアプリの状態を確認して」
あなた: （ツール実行後）「CloudFrontを確認したよ！正常に動作してる。次はS3を確認するね。」
あなた: （ツール実行後）「S3も正常だった！次はLambda関数を確認するよ。」
あなた: （最終）「全部確認完了！すべて正常に動作してるよ！」

## 利用可能なツール

### EKS監視
- list_clusters: EKSクラスタ一覧を取得
- describe_cluster: クラスタの詳細情報を取得
- list_nodegroups: ノードグループ一覧を取得

### Web検索
- search: DuckDuckGoでWeb検索を実行

### Slack通知
- notifySlack: 指定したSlackチャネルにメッセージを送信

### タスク管理
- createTask: 新しいタスクを作成
- listTasks: タスク一覧を取得

### コードレビュー（DeepWiki MCP）
- read_wiki_structure: GitHubリポジトリのドキュメント構造を取得
- read_wiki_contents: ドキュメント内容を取得
- ask_question: AI質問応答（コンテキストベース）

**対象リポジトリ:**
- リポジトリ名: `{GITHUB_USER}/agentcore-task-app`（owner/repo形式）

**パラメータ形式:**
- `repoName`: "owner/repo" 形式（例: "{GITHUB_USER}/agentcore-task-app"）
- `path`: ファイルパス（例: "README.md", "lambda/task_api/lambda_function.py"）

**レビュー項目:**
1. セキュリティチェック - 脆弱性の検出、認証・認可の確認
2. コード品質 - ベストプラクティス、可読性、エラーハンドリング
3. ドキュメント確認 - README、API仕様の確認

**使用例:**
- 「タスクアプリのコードをレビューして」→ repoName="{GITHUB_USER}/agentcore-task-app"でリポジトリ全体をレビュー
- 「Lambda関数のセキュリティを確認して」→ path="lambda/task_api/lambda_function.py"でLambda関数を確認
- 「React SPAのベストプラクティスを確認して」→ path="task_app/src/App.js"でフロントエンドを確認

### インフラヘルスチェック（AWS CLI）
AWS CLIコマンドを使用してタスクアプリのインフラ監視を実行できます。

**監視対象リソース（正確なID）:**
- CloudFront Distribution ID: {CLOUDFRONT_DISTRIBUTION_ID}
- S3バケット名: agentcore-task-app-{ACCOUNT_ID_2}
- Lambda関数: task-api-simple, task-api-delete
- DynamoDBテーブル名: agentcore-tasks

**ヘルスチェック方法:**
1. AWS CLIコマンドを実行して状態確認
2. CloudWatch Metricsでメトリクス取得
3. CloudWatch Logsでログ確認
4. 結果を解釈して自然言語で報告

**例:**
- 「タスクアプリの状態を確認して」→ 全リソースの状態確認
- 「CloudFrontの状態を教えて」→ CloudFront Distribution確認
- 「Lambdaの直近のエラーログを確認して」→ CloudWatch Logs確認

## 振る舞い

- カジュアルな口調で話してください
- タスク作成時は、適切な優先度と期限を設定してください
- 重要な情報はSlackで通知してください
- EKSの問題を検出したら、すぐにタスク化してください
- ヘルスチェック結果は分かりやすく整理して報告してください
- コードレビュー時は、セキュリティ、品質、ドキュメントの観点で確認してください

## 例

ユーザー: 「明日までにデプロイ作業のタスクを作成して、#team-devに通知して」
あなた: 「了解！デプロイ作業のタスクを作成して、#team-devに通知するね！」
→ createTask実行
→ notifySlack実行
あなた: 「タスクを作成して、#team-devに通知したよ！明日までに完了させよう！」

ユーザー: 「タスクアプリのコードをレビューして」
あなた: 「タスクアプリのコードをレビューするね！」
→ read_wiki_structure実行（repoName="{GITHUB_USER}/agentcore-task-app"）
→ read_wiki_contents実行（主要ファイル確認）
→ ask_question実行（セキュリティ、品質確認）
あなた: 「タスクアプリのコードをレビューしたよ！

✅ React SPA:
  - コンポーネント構成は適切
  - 状態管理はシンプルで理解しやすい

⚠️ Lambda関数:
  - エラーハンドリングの改善が必要
  - ログ出力の追加を推奨

✅ ドキュメント:
  - README、API仕様は充実している

推奨事項:
1. Lambda関数にtry-catchを追加
2. CloudWatch Logsの設定を追加
3. API Gatewayのスロットリング設定を追加」

ユーザー: 「タスクアプリの状態を確認して」
あなた: 「タスクアプリの状態を確認するね！」
→ AWS CLIコマンド実行（cloudfront, s3, apigateway, lambda, dynamodb）
あなた: 「タスクアプリの状態を確認したよ！
✅ CloudFront: 正常稼働中
✅ S3バケット: 正常
✅ API Gateway: 正常
✅ Lambda関数: 正常
✅ DynamoDB: 正常、アイテム数: 42件
すべて正常に動作してるよ！」"""
    
    def __init__(self, actor_id: str, session_id: str):
        self.actor_id = actor_id
        self.session_id = session_id
        self.memory_id = os.environ["MEMORY_ID"]
        
        # Memory Session Manager
        self.session_manager = create_memory_session_manager(
            memory_id=self.memory_id,
            actor_id=actor_id,
            session_id=session_id
        )
        
        # Gateway Tools
        self.gateway_provider = GatewayToolProvider()
    
    async def run(self, message: str, slack_callback: Optional[Callable[[str], None]] = None) -> str:
        """メッセージ処理"""
        # Gateway Tools取得
        tools = await self._get_gateway_tools()
        
        # CallbackHandler設定
        callback_handler = None
        if slack_callback:
            from strands_agent.handlers.slack_callback_handler import SlackCallbackHandler
            callback_handler = SlackCallbackHandler(slack_callback)
        
        # Agent作成
        agent = Agent(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            system_prompt=self.SYSTEM_PROMPT,
            session_manager=self.session_manager,
            tools=tools,
            callback_handler=callback_handler
        )
        
        # メッセージ処理
        response = agent(message)
        # responseはdictなので、textを抽出
        if isinstance(response, dict):
            return response.get('content', [{}])[0].get('text', str(response))
        return str(response)
    
    async def run_stream(self, message: str):
        """ストリーミング処理"""
        # Gateway Tools取得
        tools = await self._get_gateway_tools()
        
        agent = Agent(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            system_prompt=self.SYSTEM_PROMPT,
            session_manager=self.session_manager,
            tools=tools
        )
        
        # ストリーミング実行
        for chunk in agent.stream(message):
            yield chunk
    
    async def _get_gateway_tools(self):
        """Gateway経由でツール取得してStrands Toolに変換"""
        from strands import tool
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Gateway MCPからツール一覧取得
        logger.info("Fetching tools from Gateway...")
        tools_response = await self.gateway_provider.list_tools()
        tools_list = tools_response.get('result', {}).get('tools', [])
        logger.info(f"Found {len(tools_list)} tools: {[t['name'] for t in tools_list]}")
        
        strands_tools = []
        for tool_def in tools_list:
            tool_name = tool_def['name']
            tool_description = tool_def.get('description', '')
            tool_schema = tool_def.get('inputSchema', {})
            
            # クロージャで各ツールの関数を作成
            def make_tool(name: str, description: str, schema: dict):
                @tool(name=name, description=description)
                async def gateway_tool(**kwargs):
                    logger.info(f"Calling Gateway tool: {name} with args: {kwargs}")
                    try:
                        # kwargsキーでラップされている場合は展開
                        if 'kwargs' in kwargs and len(kwargs) == 1:
                            import json
                            kwargs_value = kwargs['kwargs']
                            # 空文字列または空の場合は空のdictとして扱う
                            if not kwargs_value or kwargs_value == '':
                                actual_args = {}
                            elif isinstance(kwargs_value, str):
                                actual_args = json.loads(kwargs_value)
                            else:
                                actual_args = kwargs_value
                        else:
                            actual_args = kwargs
                        
                        result = await self.gateway_provider.call_tool(name, actual_args)
                        logger.info(f"Gateway tool {name} result: {result}")
                        return result.get('result', {}).get('content', [{}])[0].get('text', str(result))
                    except Exception as e:
                        logger.error(f"Gateway tool {name} error: {e}", exc_info=True)
                        raise
                return gateway_tool
            
            strands_tools.append(make_tool(tool_name, tool_description, tool_schema))
        
        return strands_tools


async def main():
    """CLI実行用"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python agent.py <message>")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    
    # テスト用のactor_id/session_id
    actor_id = "cli_user"
    session_id = "cli_session_001"
    
    agent = RestaurantAgent(actor_id=actor_id, session_id=session_id)
    response = await agent.run(message)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
