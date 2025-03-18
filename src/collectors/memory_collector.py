import psutil
from typing import Dict, Any, Optional

from .base_collector import BaseCollector


class MemoryCollector(BaseCollector):
    """
    Collecteur de métriques de mémoire.
    Collecte des informations sur la mémoire vive (RAM) et la mémoire virtuelle (swap).
    """
    
    def collect(self) -> Dict[str, Any]:
        """
        Collecte et retourne toutes les métriques de mémoire
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant les métriques de mémoire
        """
        metrics = {
            'virtual': self._get_virtual_memory(),
            'swap': self._get_swap_memory()
        }
        
        # Ajouter les seuils si configurés
        if 'thresholds' in self.config:
            metrics['thresholds'] = self.config['thresholds']
        
        return metrics
    
    def _get_virtual_memory(self) -> Dict[str, Any]:
        """
        Obtient les informations sur la mémoire virtuelle (RAM)
        
        Returns:
            Dict[str, Any]: Informations sur la mémoire virtuelle
        """
        mem = psutil.virtual_memory()
        
        # Convertir l'objet namedtuple en dictionnaire
        mem_dict = mem._asdict()
        
        # Calculer des métriques dérivées utiles
        mem_dict['used_percent'] = mem.percent
        mem_dict['available_percent'] = 100 - mem.percent
        
        return mem_dict
    
    def _get_swap_memory(self) -> Dict[str, Any]:
        """
        Obtient les informations sur la mémoire d'échange (swap)
        
        Returns:
            Dict[str, Any]: Informations sur la mémoire d'échange
        """
        try:
            swap = psutil.swap_memory()
            swap_dict = swap._asdict()
            
            # Calculer des métriques dérivées
            if swap.total > 0:
                swap_dict['used_percent'] = swap.percent
                swap_dict['available_percent'] = 100 - swap.percent
            else:
                swap_dict['used_percent'] = 0
                swap_dict['available_percent'] = 0
                
            return swap_dict
        except Exception:
            return {
                'total': 0,
                'used': 0,
                'free': 0,
                'percent': 0,
                'used_percent': 0,
                'available_percent': 0
            } 