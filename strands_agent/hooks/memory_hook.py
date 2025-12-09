"""Memory統合 - AgentCoreMemorySessionManager使用"""
import os
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig


def sanitize_for_memory(value: str) -> str:
    """Memory API用にIDをサニタイズ（ドットをハイフンに置換）"""
    return value.replace(".", "-")


def create_memory_session_manager(memory_id: str, actor_id: str, session_id: str) -> AgentCoreMemorySessionManager:
    """AgentCoreMemorySessionManagerを作成
    
    Args:
        memory_id: Memory ID
        actor_id: Actor ID (Slackユーザー)
        session_id: Session ID (Slackスレッド)
    
    Returns:
        AgentCoreMemorySessionManager: セッションマネージャー
    """
    config = AgentCoreMemoryConfig(
        memory_id=memory_id,
        actor_id=actor_id,
        session_id=sanitize_for_memory(session_id)
    )
    
    return AgentCoreMemorySessionManager(
        agentcore_memory_config=config,
        region_name=os.environ.get("AWS_REGION", "ap-northeast-1")
    )
