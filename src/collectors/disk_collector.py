import os
import psutil
from typing import Dict, Any, List, Optional

from .base_collector import BaseCollector


class DiskCollector(BaseCollector):
    """
    Collecteur de métriques de disque.
    Collecte des informations sur l'utilisation du disque, les partitions et les I/O.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Chemin à exclure (par défaut les partitions système)
        self.exclude_paths = self.config.get('exclude_paths', [])
        # Chemin à inclure (par défaut toutes les partitions)
        self.include_paths = self.config.get('include_paths', [])
        # Types de système de fichiers à exclure
        self.exclude_fs_types = self.config.get('exclude_fs_types', [
            'squashfs', 'devtmpfs', 'tmpfs', 'overlay', 'debugfs', 'tracefs'
        ])
    
    def collect(self) -> Dict[str, Any]:
        """
        Collecte et retourne toutes les métriques de disque
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant les métriques de disque
        """
        metrics = {
            'partitions': self._get_partitions(),
            'usage': self._get_disk_usage(),
            'io': self._get_disk_io()
        }
        
        # Ajouter les seuils si configurés
        if 'thresholds' in self.config:
            metrics['thresholds'] = self.config['thresholds']
        
        return metrics
    
    def _get_partitions(self) -> List[Dict[str, Any]]:
        """
        Obtient la liste des partitions de disque
        
        Returns:
            List[Dict[str, Any]]: Liste des partitions
        """
        partitions = []
        
        for partition in psutil.disk_partitions(all=True):
            # Convertir l'objet namedtuple en dictionnaire
            part_info = partition._asdict()
            
            # Vérifier si on doit inclure cette partition
            if self._should_include_partition(part_info):
                partitions.append(part_info)
        
        return partitions
    
    def _should_include_partition(self, partition: Dict[str, Any]) -> bool:
        """
        Vérifie si une partition doit être incluse dans les métriques
        
        Args:
            partition: Informations sur la partition
            
        Returns:
            bool: True si la partition doit être incluse
        """
        # Exclure les types de systèmes de fichiers non désirés
        if partition['fstype'] in self.exclude_fs_types:
            return False
        
        # Si des chemins spécifiques sont inclus, vérifier si cette partition est dans la liste
        if self.include_paths and partition['mountpoint'] not in self.include_paths:
            return False
        
        # Si des chemins spécifiques sont exclus, vérifier si cette partition est dans la liste
        if partition['mountpoint'] in self.exclude_paths:
            return False
        
        return True
    
    def _get_disk_usage(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtient l'utilisation du disque pour chaque partition
        
        Returns:
            Dict[str, Dict[str, Any]]: Utilisation du disque par partition
        """
        usage = {}
        
        for partition in self._get_partitions():
            try:
                # Vérifier si le point de montage est accessible
                if os.access(partition['mountpoint'], os.R_OK):
                    disk_usage = psutil.disk_usage(partition['mountpoint'])
                    usage[partition['mountpoint']] = disk_usage._asdict()
            except Exception:
                # Ignorer les erreurs pour les partitions inaccessibles
                pass
        
        return usage
    
    def _get_disk_io(self) -> Dict[str, Any]:
        """
        Obtient les statistiques d'I/O pour tous les disques
        
        Returns:
            Dict[str, Any]: Statistiques d'I/O par disque
        """
        try:
            io_counters = psutil.disk_io_counters(perdisk=True)
            
            # Convertir les objets namedtuple en dictionnaires
            io_dict = {}
            for disk, counters in io_counters.items():
                io_dict[disk] = counters._asdict()
            
            return io_dict
        except Exception:
            return {} 