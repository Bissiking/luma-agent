import time
import psutil
from typing import Dict, Any, List, Optional

from .base_collector import BaseCollector


class NetworkCollector(BaseCollector):
    """
    Collecteur de métriques réseau.
    Collecte des informations sur les interfaces réseau et leur utilisation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Intervalle pour calculer les taux de transfert
        self.interval = self.config.get('interval', 1)
        # Interfaces à exclure
        self.exclude_interfaces = self.config.get('exclude_interfaces', [])
        # Interfaces à inclure (si vide, toutes sauf celles exclues)
        self.include_interfaces = self.config.get('include_interfaces', [])
        # Compteurs précédents pour calculer les taux
        self._previous_counters = None
        self._previous_time = None
    
    def collect(self) -> Dict[str, Any]:
        """
        Collecte et retourne toutes les métriques réseau
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant les métriques réseau
        """
        metrics = {
            'interfaces': self._get_network_interfaces(),
            'io': self._get_network_io(),
            'connections': self._get_connections()
        }
        
        # Ajouter les taux si disponibles
        rates = self._calculate_network_rates()
        if rates:
            metrics['rates'] = rates
        
        # Ajouter les seuils si configurés
        if 'thresholds' in self.config:
            metrics['thresholds'] = self.config['thresholds']
        
        return metrics
    
    def _get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtient les informations sur les interfaces réseau
        
        Returns:
            Dict[str, Dict[str, Any]]: Informations sur les interfaces réseau
        """
        interfaces = {}
        
        # Obtenir les adresses
        net_if_addrs = psutil.net_if_addrs()
        
        # Obtenir les statistiques
        net_if_stats = psutil.net_if_stats()
        
        # Combiner les informations
        for interface, addrs in net_if_addrs.items():
            # Vérifier si on doit inclure cette interface
            if not self._should_include_interface(interface):
                continue
                
            interfaces[interface] = {
                'addresses': [],
                'stats': {}
            }
            
            # Ajouter les adresses
            for addr in addrs:
                addr_info = addr._asdict()
                interfaces[interface]['addresses'].append(addr_info)
            
            # Ajouter les statistiques si disponibles
            if interface in net_if_stats:
                interfaces[interface]['stats'] = net_if_stats[interface]._asdict()
        
        return interfaces
    
    def _should_include_interface(self, interface: str) -> bool:
        """
        Vérifie si une interface réseau doit être incluse dans les métriques
        
        Args:
            interface: Nom de l'interface réseau
            
        Returns:
            bool: True si l'interface doit être incluse
        """
        # Si des interfaces spécifiques sont incluses, vérifier si celle-ci est dans la liste
        if self.include_interfaces and interface not in self.include_interfaces:
            return False
        
        # Si des interfaces spécifiques sont exclues, vérifier si celle-ci est dans la liste
        if interface in self.exclude_interfaces:
            return False
        
        return True
    
    def _get_network_io(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtient les statistiques d'I/O réseau pour chaque interface
        
        Returns:
            Dict[str, Dict[str, Any]]: Statistiques d'I/O par interface
        """
        try:
            io_counters = psutil.net_io_counters(pernic=True)
            
            # Mettre à jour les compteurs précédents pour les taux
            current_time = time.time()
            self._previous_counters = io_counters
            self._previous_time = current_time
            
            # Convertir les objets namedtuple en dictionnaires
            io_dict = {}
            for nic, counters in io_counters.items():
                # Vérifier si on doit inclure cette interface
                if self._should_include_interface(nic):
                    io_dict[nic] = counters._asdict()
            
            return io_dict
        except Exception:
            return {}
    
    def _calculate_network_rates(self) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Calcule les taux de transfert réseau en utilisant les compteurs précédents
        
        Returns:
            Optional[Dict[str, Dict[str, float]]]: Taux de transfert par interface ou None si pas disponible
        """
        # Si nous n'avons pas de mesures précédentes, nous ne pouvons pas calculer les taux
        if not self._previous_counters or not self._previous_time:
            return None
        
        # Obtenir les compteurs actuels
        try:
            current_counters = psutil.net_io_counters(pernic=True)
            current_time = time.time()
            
            # Calculer l'intervalle de temps
            time_delta = current_time - self._previous_time
            if time_delta <= 0:
                return None
            
            rates = {}
            for nic, counters in current_counters.items():
                # Vérifier si on doit inclure cette interface et si elle était dans les mesures précédentes
                if self._should_include_interface(nic) and nic in self._previous_counters:
                    prev_counters = self._previous_counters[nic]
                    
                    # Calculer les taux
                    rates[nic] = {
                        'bytes_sent_per_sec': (counters.bytes_sent - prev_counters.bytes_sent) / time_delta,
                        'bytes_recv_per_sec': (counters.bytes_recv - prev_counters.bytes_recv) / time_delta,
                        'packets_sent_per_sec': (counters.packets_sent - prev_counters.packets_sent) / time_delta,
                        'packets_recv_per_sec': (counters.packets_recv - prev_counters.packets_recv) / time_delta,
                        'errin_per_sec': (counters.errin - prev_counters.errin) / time_delta,
                        'errout_per_sec': (counters.errout - prev_counters.errout) / time_delta,
                        'dropin_per_sec': (counters.dropin - prev_counters.dropin) / time_delta,
                        'dropout_per_sec': (counters.dropout - prev_counters.dropout) / time_delta
                    }
            
            # Mettre à jour les compteurs précédents pour la prochaine mesure
            self._previous_counters = current_counters
            self._previous_time = current_time
            
            return rates
        except Exception:
            return None
    
    def _get_connections(self) -> List[Dict[str, Any]]:
        """
        Obtient la liste des connexions réseau actives
        
        Returns:
            List[Dict[str, Any]]: Liste des connexions réseau
        """
        try:
            connections = []
            for conn in psutil.net_connections(kind='all'):
                conn_info = conn._asdict()
                
                # Vérifier si cette connexion appartient à une interface incluse
                if 'laddr' in conn_info and conn_info['laddr']:
                    # On ne peut pas facilement mapper une connexion à une interface,
                    # mais nous pouvons toujours collecter toutes les connexions
                    connections.append(conn_info)
            
            return connections
        except Exception:
            return [] 