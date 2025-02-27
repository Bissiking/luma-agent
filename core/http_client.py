import aiohttp
from typing import Any, Dict, Optional
import json

class HTTPClient:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def ensure_session(self):
        """S'assure qu'une session est active"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def close(self):
        """Ferme la session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def post(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Effectue une requête POST"""
        await self.ensure_session()
        async with self._session.post(url, json=data, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Effectue une requête GET"""
        await self.ensure_session()
        async with self._session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def send_discord_webhook(self, webhook_url: str, message: str, username: Optional[str] = None) -> bool:
        """Envoie un message via webhook Discord"""
        try:
            payload = {
                "content": message,
                "username": username or "LUMA Agent"
            }
            await self.post(webhook_url, payload)
            return True
        except Exception:
            return False

    async def send_luma_request(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None,
                              api_key: Optional[str] = None) -> Dict[str, Any]:
        """Envoie une requête à l'API LUMA"""
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            if method.upper() == "GET":
                return await self.get(endpoint, headers=headers)
            elif method.upper() == "POST":
                return await self.post(endpoint, data or {}, headers=headers)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
        except Exception as e:
            return {"error": str(e)} 