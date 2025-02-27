from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional
from discord_webhook import AsyncDiscordWebhook
from core.utils import get_logger

class BaseModule(ABC):
    def __init__(self, module_manager: 'ModuleManager'):
        self.module_manager = module_manager
        self.config: Dict[str, Any] = {}
        self.name = self.__class__.__name__.lower()
        self.logger = get_logger(self.name)
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        if value != self._enabled:
            self._enabled = value
            if value:
                self.logger.info(f"Module {self.name} enabled")
            else:
                self.logger.info(f"Module {self.name} disabled")

    async def initialize(self, config: Dict[str, Any]):
        """Initialize the module with its configuration"""
        self.config = config
        self.enabled = config.get('enabled', True)
        if self.enabled:
            await self.on_load()

    async def cleanup(self):
        """Cleanup module resources"""
        if self.enabled:
            await self.on_unload()
        self.enabled = False

    @abstractmethod
    async def on_load(self):
        """Called when the module is loaded"""
        pass

    @abstractmethod
    async def on_unload(self):
        """Called when the module is unloaded"""
        pass

    async def send_discord_notification(self, message: str, webhook_url: Optional[str] = None):
        """Send a notification to Discord"""
        try:
            url = webhook_url or self.config.get('discord_webhook_url')
            if not url:
                self.logger.warning("No Discord webhook URL configured")
                return False

            webhook = AsyncDiscordWebhook(url=url, content=message)
            await webhook.execute()
            return True
        except Exception as e:
            self.logger.error(f"Failed to send Discord notification: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'config': self.config
        } 