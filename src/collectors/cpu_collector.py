import psutil
import time
from typing import Dict, Any, List, Optional

from .base_collector import BaseCollector


class CPUCollector(BaseCollector):
    """
    Collecteur de métriques CPU.
    Collecte l'utilisation CPU globale, par cœur et les statistiques de charge.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.interval = self.config.get('interval', 1)  # Intervalle pour calculer l'utilisation CPU
    
    def collect(self) -> Dict[str, Any]:
        """
        Collecte et retourne toutes les métriques CPU
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant les métriques CPU
        """
        metrics = {
            'percent': self._get_cpu_percent(),
            'count': {
                'physical': psutil.cpu_count(logical=False),
                'logical': psutil.cpu_count(logical=True)
            },
            'per_cpu': self._get_per_cpu_percent(),
            'times': self._get_cpu_times(),
            'stats': self._get_cpu_stats(),
            'freq': self._get_cpu_freq()
        }
        
        # Ajouter les seuils si configurés
        if 'thresholds' in self.config:
            metrics['thresholds'] = self.config['thresholds']
        
        return metrics
    
    def _get_cpu_percent(self) -> float:
        """
        Obtient le pourcentage d'utilisation CPU global
        
        Returns:
            float: Pourcentage d'utilisation CPU
        """
        return psutil.cpu_percent(interval=self.interval)
    
    def _get_per_cpu_percent(self) -> List[float]:
        """
        Obtient le pourcentage d'utilisation par cœur CPU
        
        Returns:
            List[float]: Liste des pourcentages par cœur
        """
        return psutil.cpu_percent(interval=self.interval, percpu=True)
    
    def _get_cpu_times(self) -> Dict[str, Any]:
        """
        Obtient les statistiques détaillées de temps CPU
        
        Returns:
            Dict[str, Any]: Statistiques de temps CPU
        """
        cpu_times = psutil.cpu_times()._asdict()
        cpu_times_percent = psutil.cpu_times_percent()._asdict()
        
        return {
            'times': cpu_times,
            'percent': cpu_times_percent
        }
    
    def _get_cpu_stats(self) -> Dict[str, int]:
        """
        Obtient les statistiques CPU (ctx_switches, interrupts, etc.)
        
        Returns:
            Dict[str, int]: Statistiques CPU
        """
        try:
            return psutil.cpu_stats()._asdict()
        except Exception:
            return {}
    
    def _get_cpu_freq(self) -> Dict[str, Any]:
        """
        Obtient les informations de fréquence du CPU
        
        Returns:
            Dict[str, Any]: Informations de fréquence
        """
        try:
            freq = psutil.cpu_freq()
            if freq:
                return freq._asdict()
            return {}
        except Exception:
            return {} 