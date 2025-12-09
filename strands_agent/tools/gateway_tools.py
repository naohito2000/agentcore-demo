"""Gateway MCP統合ツール"""
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class GatewayTokenManager:
    """OAuth2トークン管理"""
    
    def __init__(self, client_id: str, client_secret: str, token_endpoint: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_endpoint = token_endpoint
        self._token: Optional[str] = None
        self._expires_at: Optional[datetime] = None
    
    async def get_token(self) -> str:
        """トークン取得（自動リフレッシュ）"""
        if self._token and self._expires_at and self._expires_at > datetime.now():
            return self._token
        
        # トークン取得
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.token_endpoint,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            data = response.json()
            self._token = data['access_token']
            expires_in = data.get('expires_in', 3600) - 300  # 5分前にリフレッシュ
            self._expires_at = datetime.now() + timedelta(seconds=expires_in)
            return self._token


class GatewayToolProvider:
    """Gateway MCP統合"""
    
    def __init__(self):
        self.gateway_url = os.environ["GATEWAY_URL"]
        self.token_manager = GatewayTokenManager(
            client_id=os.environ["GATEWAY_CLIENT_ID"],
            client_secret=os.environ["GATEWAY_CLIENT_SECRET"],
            token_endpoint=os.environ["GATEWAY_TOKEN_ENDPOINT"]
        )
    
    async def list_tools(self) -> Dict[str, Any]:
        """利用可能なツール一覧を取得"""
        token = await self.token_manager.get_token()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.gateway_url,
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """ツール実行"""
        token = await self.token_manager.get_token()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.gateway_url,
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
            )
            response.raise_for_status()
            return response.json()
