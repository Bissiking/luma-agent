import time
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Gestionnaire d'alertes pour l'agent de monitoring.
    Vérifie les métriques collectées par rapport aux seuils définis et génère des alertes.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le gestionnaire d'alertes
        
        Args:
            config: Configuration des alertes
        """
        self.config = config or {}
        self.alerts_enabled = self.config.get('enabled', True)
        self.state = {}  # État des alertes actuelles
        self.alert_history = []  # Historique des alertes récentes
        self.max_history = 100  # Nombre maximal d'alertes à conserver dans l'historique
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Vérifie les métriques collectées par rapport aux seuils définis et génère des alertes
        
        Args:
            metrics: Métriques collectées par les différents collecteurs
            
        Returns:
            List[Dict[str, Any]]: Liste des alertes générées
        """
        if not self.alerts_enabled:
            return []
        
        alerts = []
        current_time = time.time()
        
        # Vérifier les alertes CPU
        cpu_alerts = self._check_cpu_alerts(metrics.get('cpu_collector', {}), current_time)
        alerts.extend(cpu_alerts)
        
        # Vérifier les alertes mémoire
        memory_alerts = self._check_memory_alerts(metrics.get('memory_collector', {}), current_time)
        alerts.extend(memory_alerts)
        
        # Vérifier les alertes disque
        disk_alerts = self._check_disk_alerts(metrics.get('disk_collector', {}), current_time)
        alerts.extend(disk_alerts)
        
        # Vérifier les alertes réseau
        network_alerts = self._check_network_alerts(metrics.get('network_collector', {}), current_time)
        alerts.extend(network_alerts)
        
        # Vérifier les alertes Docker
        docker_alerts = self._check_docker_alerts(metrics.get('docker_collector', {}), current_time)
        alerts.extend(docker_alerts)
        
        # Vérifier les alertes de services web
        web_alerts = self._check_web_service_alerts(metrics.get('web_service_collector', {}), current_time)
        alerts.extend(web_alerts)
        
        # Mettre à jour l'historique des alertes
        for alert in alerts:
            self.alert_history.append(alert)
        
        # Limiter la taille de l'historique
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        return alerts
    
    def _check_threshold(self, metric_value: float, threshold: float, 
                         threshold_type: str = 'above') -> bool:
        """
        Vérifie si une valeur dépasse un seuil
        
        Args:
            metric_value: Valeur de la métrique
            threshold: Valeur du seuil
            threshold_type: Type de seuil ('above' ou 'below')
            
        Returns:
            bool: True si le seuil est dépassé, False sinon
        """
        if threshold_type == 'above':
            return metric_value > threshold
        elif threshold_type == 'below':
            return metric_value < threshold
        else:
            return False
    
    def _update_alert_state(self, alert_id: str, metric_value: float, threshold: float,
                          duration: int, current_time: float, is_triggered: bool) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Met à jour l'état d'une alerte et vérifie si elle doit être déclenchée
        
        Args:
            alert_id: Identifiant unique de l'alerte
            metric_value: Valeur actuelle de la métrique
            threshold: Valeur du seuil
            duration: Durée (en secondes) pendant laquelle le seuil doit être dépassé
            current_time: Timestamp actuel
            is_triggered: Si le seuil est actuellement dépassé
            
        Returns:
            Tuple[bool, Optional[Dict[str, Any]]]: 
                - True si l'alerte doit être déclenchée, False sinon
                - État de l'alerte ou None
        """
        # Récupérer l'état actuel de l'alerte
        alert_state = self.state.get(alert_id)
        
        # Si l'alerte n'est pas déclenchée, réinitialiser son état
        if not is_triggered:
            if alert_state and alert_state.get('active'):
                # Si l'alerte était active, créer une alerte de fin
                self.state[alert_id] = {
                    'active': False,
                    'first_triggered': None,
                    'last_update': current_time,
                    'value': metric_value
                }
                return True, {
                    'id': alert_id,
                    'status': 'resolved',
                    'timestamp': current_time,
                    'value': metric_value,
                    'threshold': threshold
                }
            elif alert_state:
                # Mise à jour de l'état sans générer d'alerte
                self.state[alert_id] = {
                    'active': False,
                    'first_triggered': None,
                    'last_update': current_time,
                    'value': metric_value
                }
            return False, None
        
        # Le seuil est dépassé, mettre à jour l'état
        if not alert_state:
            # Première détection
            self.state[alert_id] = {
                'active': False,  # Pas encore active car la durée n'est pas atteinte
                'first_triggered': current_time,
                'last_update': current_time,
                'value': metric_value
            }
            return False, None
        
        # Mise à jour de l'état
        alert_state['last_update'] = current_time
        alert_state['value'] = metric_value
        
        # Vérifier si la durée est atteinte
        if (current_time - alert_state['first_triggered'] >= duration and not alert_state['active']):
            # Activer l'alerte
            alert_state['active'] = True
            self.state[alert_id] = alert_state
            
            return True, {
                'id': alert_id,
                'status': 'triggered',
                'timestamp': current_time,
                'first_triggered': alert_state['first_triggered'],
                'value': metric_value,
                'threshold': threshold,
                'duration': duration
            }
        
        return False, None
    
    def _check_cpu_alerts(self, cpu_metrics: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """
        Vérifie les alertes CPU
        
        Args:
            cpu_metrics: Métriques CPU collectées
            current_time: Timestamp actuel
            
        Returns:
            List[Dict[str, Any]]: Liste des alertes CPU générées
        """
        alerts = []
        
        if not cpu_metrics or not isinstance(cpu_metrics, dict):
            return alerts
        
        # Configuration des alertes CPU
        cpu_alerts_config = self.config.get('cpu', {})
        
        if not cpu_alerts_config.get('enabled', True):
            return alerts
            
        # Vérifier l'utilisation CPU élevée
        warning_threshold = cpu_alerts_config.get('warning', 70)
        critical_threshold = cpu_alerts_config.get('critical', 90)
        duration = cpu_alerts_config.get('duration', 300)
        recovery_threshold = cpu_alerts_config.get('recovery_threshold', 60)
        
        # Obtenir l'utilisation CPU actuelle
        cpu_percent = cpu_metrics.get('percent')
        
        if cpu_percent is not None:
            # Vérifier l'alerte critique
            alert_id = 'cpu.critical'
            is_triggered = self._check_threshold(cpu_percent, critical_threshold, 'above')
            
            should_alert, alert_data = self._update_alert_state(
                alert_id, cpu_percent, critical_threshold, duration, current_time, is_triggered
            )
            
            if should_alert and alert_data:
                alert_data.update({
                    'type': 'cpu',
                    'name': 'CPU Critical Usage',
                    'description': f"L'utilisation CPU ({cpu_percent:.1f}%) dépasse le seuil critique de {critical_threshold}% pendant plus de {duration/60:.1f} minutes",
                    'level': 'critical'
                })
                alerts.append(alert_data)
            
            # Vérifier l'alerte warning
            alert_id = 'cpu.warning'
            is_triggered = self._check_threshold(cpu_percent, warning_threshold, 'above')
            
            should_alert, alert_data = self._update_alert_state(
                alert_id, cpu_percent, warning_threshold, duration, current_time, is_triggered
            )
            
            if should_alert and alert_data:
                alert_data.update({
                    'type': 'cpu',
                    'name': 'CPU High Usage',
                    'description': f"L'utilisation CPU ({cpu_percent:.1f}%) dépasse le seuil d'avertissement de {warning_threshold}% pendant plus de {duration/60:.1f} minutes",
                    'level': 'warning'
                })
                alerts.append(alert_data)
        
        return alerts
    
    def _check_memory_alerts(self, memory_metrics: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """
        Vérifie les alertes mémoire
        
        Args:
            memory_metrics: Métriques mémoire collectées
            current_time: Timestamp actuel
            
        Returns:
            List[Dict[str, Any]]: Liste des alertes mémoire générées
        """
        alerts = []
        
        if not memory_metrics or not isinstance(memory_metrics, dict):
            return alerts
        
        # Configuration des alertes mémoire
        memory_alerts_config = self.config.get('memory', {})
        
        if not memory_alerts_config.get('enabled', True):
            return alerts
            
        # Vérifier l'utilisation mémoire élevée
        warning_threshold = memory_alerts_config.get('warning', 75)
        critical_threshold = memory_alerts_config.get('critical', 85)
        duration = memory_alerts_config.get('duration', 300)
        recovery_threshold = memory_alerts_config.get('recovery_threshold', 65)
        
        # Obtenir l'utilisation mémoire actuelle
        virtual_memory = memory_metrics.get('virtual', {})
        mem_percent = virtual_memory.get('percent')
        
        if mem_percent is not None:
            # Vérifier l'alerte critique
            alert_id = 'memory.critical'
            is_triggered = self._check_threshold(mem_percent, critical_threshold, 'above')
            
            should_alert, alert_data = self._update_alert_state(
                alert_id, mem_percent, critical_threshold, duration, current_time, is_triggered
            )
            
            if should_alert and alert_data:
                alert_data.update({
                    'type': 'memory',
                    'name': 'Memory Critical Usage',
                    'description': f"L'utilisation mémoire ({mem_percent:.1f}%) dépasse le seuil critique de {critical_threshold}% pendant plus de {duration/60:.1f} minutes",
                    'level': 'critical'
                })
                alerts.append(alert_data)
            
            # Vérifier l'alerte warning
            alert_id = 'memory.warning'
            is_triggered = self._check_threshold(mem_percent, warning_threshold, 'above')
            
            should_alert, alert_data = self._update_alert_state(
                alert_id, mem_percent, warning_threshold, duration, current_time, is_triggered
            )
            
            if should_alert and alert_data:
                alert_data.update({
                    'type': 'memory',
                    'name': 'Memory High Usage',
                    'description': f"L'utilisation mémoire ({mem_percent:.1f}%) dépasse le seuil d'avertissement de {warning_threshold}% pendant plus de {duration/60:.1f} minutes",
                    'level': 'warning'
                })
                alerts.append(alert_data)
        
        return alerts
    
    def _check_disk_alerts(self, disk_metrics: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """
        Vérifie les alertes disque
        
        Args:
            disk_metrics: Métriques disque collectées
            current_time: Timestamp actuel
            
        Returns:
            List[Dict[str, Any]]: Liste des alertes disque générées
        """
        alerts = []
        
        if not disk_metrics or not isinstance(disk_metrics, dict):
            return alerts
        
        # Configuration des alertes disque
        disk_alerts_config = self.config.get('disk', {})
        
        if not disk_alerts_config.get('enabled', True):
            return alerts
            
        # Vérifier l'utilisation disque élevée
        warning_threshold = disk_alerts_config.get('warning', 80)
        critical_threshold = disk_alerts_config.get('critical', 90)
        duration = disk_alerts_config.get('duration', 600)
        recovery_threshold = disk_alerts_config.get('recovery_threshold', 70)
        partitions = disk_alerts_config.get('partitions', ['*'])
        
        # Vérifier chaque partition
        disk_usage = disk_metrics.get('usage', {})
        for mount_point, usage in disk_usage.items():
            # Vérifier si cette partition doit être surveillée
            should_monitor = False
            if '*' in partitions:
                should_monitor = True
            elif mount_point in partitions:
                should_monitor = True
            
            if should_monitor and isinstance(usage, dict) and 'percent' in usage:
                usage_percent = usage.get('percent')
                
                if usage_percent is not None:
                    # Vérifier l'alerte critique
                    alert_id = f"disk.critical.{mount_point.replace('/', '_')}"
                    is_triggered = self._check_threshold(usage_percent, critical_threshold, 'above')
                    
                    should_alert, alert_data = self._update_alert_state(
                        alert_id, usage_percent, critical_threshold, duration, current_time, is_triggered
                    )
                    
                    if should_alert and alert_data:
                        alert_data.update({
                            'type': 'disk',
                            'name': f"Disk Critical Usage ({mount_point})",
                            'description': f"L'utilisation du disque sur {mount_point} ({usage_percent:.1f}%) dépasse le seuil critique de {critical_threshold}% pendant plus de {duration/60:.1f} minutes",
                            'level': 'critical',
                            'mount_point': mount_point
                        })
                        alerts.append(alert_data)
                    
                    # Vérifier l'alerte warning
                    alert_id = f"disk.warning.{mount_point.replace('/', '_')}"
                    is_triggered = self._check_threshold(usage_percent, warning_threshold, 'above')
                    
                    should_alert, alert_data = self._update_alert_state(
                        alert_id, usage_percent, warning_threshold, duration, current_time, is_triggered
                    )
                    
                    if should_alert and alert_data:
                        alert_data.update({
                            'type': 'disk',
                            'name': f"Disk High Usage ({mount_point})",
                            'description': f"L'utilisation du disque sur {mount_point} ({usage_percent:.1f}%) dépasse le seuil d'avertissement de {warning_threshold}% pendant plus de {duration/60:.1f} minutes",
                            'level': 'warning',
                            'mount_point': mount_point
                        })
                        alerts.append(alert_data)
        
        return alerts
    
    def _check_network_alerts(self, network_metrics: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """
        Vérifie les alertes réseau
        
        Args:
            network_metrics: Métriques réseau collectées
            current_time: Timestamp actuel
            
        Returns:
            List[Dict[str, Any]]: Liste des alertes réseau générées
        """
        # Pour l'instant, pas d'alertes réseau spécifiques définies
        # Cette méthode peut être étendue à l'avenir pour inclure des alertes sur le trafic réseau
        return []
    
    def _check_docker_alerts(self, docker_metrics: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """
        Vérifie les alertes Docker
        
        Args:
            docker_metrics: Métriques Docker collectées
            current_time: Timestamp actuel
            
        Returns:
            List[Dict[str, Any]]: Liste des alertes Docker générées
        """
        # Pour l'instant, pas d'alertes Docker spécifiques définies
        # Cette méthode peut être étendue à l'avenir pour inclure des alertes sur les conteneurs Docker
        return []
    
    def _check_web_service_alerts(self, web_metrics: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """
        Vérifie les alertes de services web
        
        Args:
            web_metrics: Métriques de services web collectées
            current_time: Timestamp actuel
            
        Returns:
            List[Dict[str, Any]]: Liste des alertes de services web générées
        """
        alerts = []
        
        if not web_metrics or not isinstance(web_metrics, dict):
            return alerts
        
        # Obtenir les résultats des vérifications de services web
        services = web_metrics.get('services', [])
        
        for service in services:
            if not isinstance(service, dict):
                continue
                
            service_name = service.get('name')
            service_url = service.get('url')
            service_status = service.get('status')
            
            if service_status == 'error':
                alert_id = f"web_service.error.{service_name or service_url}"
                
                # Pour les services web, on génère une alerte immédiatement (sans durée)
                error_message = service.get('error', 'Unknown error')
                
                alert_data = {
                    'id': alert_id,
                    'type': 'web_service',
                    'name': f"Web Service Error ({service_name or service_url})",
                    'description': f"Le service web {service_name or service_url} est en erreur: {error_message}",
                    'status': 'triggered',
                    'timestamp': current_time,
                    'service_name': service_name,
                    'service_url': service_url,
                    'error': error_message
                }
                
                # Vérifier si cette alerte a déjà été envoyée récemment
                existing_alert = False
                for hist_alert in self.alert_history:
                    if hist_alert.get('id') == alert_id and hist_alert.get('status') == 'triggered':
                        existing_alert = True
                        break
                
                if not existing_alert:
                    alerts.append(alert_data)
                
            elif service_status == 'ok':
                # Si le service fonctionne maintenant mais était en erreur avant, générer une alerte de résolution
                alert_id = f"web_service.error.{service_name or service_url}"
                
                for hist_alert in self.alert_history:
                    if hist_alert.get('id') == alert_id and hist_alert.get('status') == 'triggered':
                        alert_data = {
                            'id': alert_id,
                            'type': 'web_service',
                            'name': f"Web Service Recovered ({service_name or service_url})",
                            'description': f"Le service web {service_name or service_url} fonctionne à nouveau",
                            'status': 'resolved',
                            'timestamp': current_time,
                            'service_name': service_name,
                            'service_url': service_url
                        }
                        alerts.append(alert_data)
                        break
        
        return alerts
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des alertes actives
        
        Returns:
            List[Dict[str, Any]]: Liste des alertes actives
        """
        active_alerts = []
        
        for alert_id, state in self.state.items():
            if state.get('active'):
                # Trouver la dernière alerte déclenchée pour cet ID dans l'historique
                for alert in reversed(self.alert_history):
                    if alert.get('id') == alert_id and alert.get('status') == 'triggered':
                        active_alerts.append(alert)
                        break
        
        return active_alerts
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """
        Retourne l'historique des alertes
        
        Returns:
            List[Dict[str, Any]]: Historique des alertes
        """
        return self.alert_history.copy() 