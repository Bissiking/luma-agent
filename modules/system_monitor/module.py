import asyncio
from core.base_module import BaseModule
from core.utils import get_system_info

class SystemMonitorModule(BaseModule):
    def __init__(self, module_manager):
        super().__init__(module_manager)
        self.monitor_task = None
        self.alert_thresholds = {
            'cpu': 80,  # %
            'memory': 80,  # %
            'disk': 90,  # %
        }

    async def on_load(self):
        self.logger.info("System Monitor module loaded")
        self.alert_thresholds.update(self.config.get('alert_thresholds', {}))
        
        # Démarrer la tâche de surveillance
        self.monitor_task = asyncio.create_task(self._monitor_loop())

    async def on_unload(self):
        self.logger.info("System Monitor module unloading")
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        while True:
            try:
                await self._check_system()
                await asyncio.sleep(self.config.get('check_interval', 60))
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)

    async def _check_system(self):
        system_info = await get_system_info()
        resources = system_info['resources']

        # Vérifier CPU
        if resources['cpu_percent'] > self.alert_thresholds['cpu']:
            await self._send_alert(
                'cpu',
                f"⚠️ CPU usage is high: {resources['cpu_percent']}%"
            )

        # Vérifier mémoire
        if resources['memory_percent'] > self.alert_thresholds['memory']:
            await self._send_alert(
                'memory',
                f"⚠️ Memory usage is high: {resources['memory_percent']}%"
            )

        # Vérifier disque
        if resources['disk_percent'] > self.alert_thresholds['disk']:
            await self._send_alert(
                'disk',
                f"⚠️ Disk usage is high: {resources['disk_percent']}%"
            )

        # Enregistrer les métriques pour l'historique
        self._update_metrics_history(resources)

    async def _send_alert(self, alert_type: str, message: str):
        # Vérifier si l'alerte a déjà été envoyée récemment
        if self._should_send_alert(alert_type):
            await self.send_discord_notification(message)
            self._mark_alert_sent(alert_type)

    def _should_send_alert(self, alert_type: str) -> bool:
        # Éviter le spam d'alertes en vérifiant la dernière alerte
        last_alert = self.config.get('last_alerts', {}).get(alert_type, 0)
        min_interval = self.config.get('alert_interval', 3600)  # 1 heure par défaut
        return (asyncio.get_event_loop().time() - last_alert) > min_interval

    def _mark_alert_sent(self, alert_type: str):
        if 'last_alerts' not in self.config:
            self.config['last_alerts'] = {}
        self.config['last_alerts'][alert_type] = asyncio.get_event_loop().time()

    def _update_metrics_history(self, resources: dict):
        # Garder un historique des métriques pour le dashboard
        history_size = self.config.get('history_size', 100)
        if 'metrics_history' not in self.config:
            self.config['metrics_history'] = []

        self.config['metrics_history'].append({
            'timestamp': asyncio.get_event_loop().time(),
            'cpu': resources['cpu_percent'],
            'memory': resources['memory_percent'],
            'disk': resources['disk_percent']
        })

        # Limiter la taille de l'historique
        if len(self.config['metrics_history']) > history_size:
            self.config['metrics_history'] = self.config['metrics_history'][-history_size:]

    def get_metrics_history(self):
        """Get metrics history for the dashboard"""
        return self.config.get('metrics_history', []) 