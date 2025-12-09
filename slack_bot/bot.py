"""Slack Bot - Socket Mode"""
import os
import sys
import asyncio
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# PYTHONPATHを設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strands_agent.agent import TaskBotAgent

# Slack App初期化
app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.event("app_mention")
def handle_mention(event, say, client):
    """メンション処理"""
    logger.info(f"Received mention event: {event}")
    
    try:
        # スレッド情報取得
        thread_ts = event.get("thread_ts") or event["ts"]
        channel_id = event["channel"]
        user_id = event["user"]
        text = event["text"]
        
        logger.info(f"Processing: channel={channel_id}, user={user_id}, thread={thread_ts}")
        
        # メンションを除去
        bot_user_id = client.auth_test()["user_id"]
        message = text.replace(f"<@{bot_user_id}>", "").strip()
        
        logger.info(f"Message after mention removal: {message}")
        
        # Agent実行
        agent = TaskBotAgent(
            actor_id=user_id,
            session_id=thread_ts
        )
        
        logger.info("Running agent with Slack notifications...")
        
        # Slack通知用コールバック
        def post_to_slack(text: str):
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text=text
                )
            except Exception as e:
                logger.error(f"Failed to post to Slack: {e}")
        
        # Agent実行（Slack通知Hook付き）
        result = asyncio.run(agent.run(message, slack_callback=post_to_slack))
        
        logger.info(f"Agent result: {result[:100]}...")
        
        # 最終応答
        # 日本語の文字化けを防ぐため、直接Web APIを使用
        result_text = result if isinstance(result, str) else str(result)
        
        # 初期メッセージを削除
        try:
            client.chat_delete(
                channel=channel_id,
                ts=message_ts
            )
        except:
            pass
        
        # 新しいメッセージを投稿（明示的にUTF-8エンコード）
        import requests
        import json as json_module
        slack_token = os.environ["SLACK_BOT_TOKEN"]
        
        payload = {
            "channel": channel_id,
            "thread_ts": thread_ts,
            "text": result_text
        }
        
        # デバッグ: 送信するペイロードをログ出力
        logger.info(f"Sending to Slack: {json_module.dumps(payload, ensure_ascii=False)[:200]}")
        
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {slack_token}",
                "Content-Type": "application/json; charset=utf-8"
            },
            data=json_module.dumps(payload, ensure_ascii=False).encode('utf-8')
        )
        
        logger.info(f"Slack API response: {response.json()}")
        
        if not response.json().get("ok"):
            logger.error(f"Slack API error: {response.json()}")
            # フォールバック: Bolt SDKを使用
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=result_text
            )
        
        logger.info("Response updated successfully")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        say(
            text=f"エラーが発生しました: {str(e)}",
            thread_ts=thread_ts
        )


@app.event("message")
def handle_message(event, logger):
    """全メッセージをログ出力（デバッグ用）"""
    logger.debug(f"Message event: {event}")


if __name__ == "__main__":
    # Socket Mode起動
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    logger.info("⚡️ Slack Bot is running!")
    handler.start()
