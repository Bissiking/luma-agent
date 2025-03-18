import os
import yaml
import json
import logging
import time
from typing import Dict, Any, Optional
from copy import deepcopy

from ..api.client import ApiClient

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Gestionnaire de configuration pour l'agent de monitoring.
    Gère la lecture de la configuration locale et la récupération de la configuration distante.
    """
    
    def __init__(self, config_file: str = None, use_remote_config: bool = True):
        """
        Initialise le gestionnaire de configuration
        
        Args:
            config_file: Chemin vers le fichier de configuration local (YAML)
            use_remote_config: Indique si la configuration distante doit être utilisée
        """
        self.config_file = config_file
        self.use_remote_config = use_remote_config
        self.config = {}
        self.default_config = self._get_default_config()
        self.last_remote_config_fetch = 0
        self.api_client = None
        
        # Charger la configuration locale si spécifiée
        if self.config_file:
            self.load_local_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration par défaut
        
        Returns:
            Dict[str, Any]: Configuration par défaut
        """
        return {
            'agent': {
                'version': 'P-2.0.0-Grizzly',
                'interval': 60,  # Intervalle de collecte des métriques (secondes)
                'log_level': 'INFO',
                'log_file': '/var/log/monitoring-agent.log',
                'use_remote_config': True,
                'remote_config_interval': 300  # Intervalle de récupération de la configuration distante (secondes)
            },
            'api': {
                'base_url': 'https://monitoring.example.com',
                'uuid': '',
                'token': '',
                'timeout': 30
            },
            'collectors': {
                'cpu_collector': {
                    'enabled': True,
                    'interval': 1  # Intervalle pour calculer l'utilisation CPU
                },
                'memory_collector': {
                    'enabled': True
                },
                'disk_collector': {
                    'enabled': True,
                    'exclude_paths': [],
                    'include_paths': [],
                    'exclude_fs_types': ['squashfs', 'devtmpfs', 'tmpfs']
                },
                'network_collector': {
                    'enabled': True,
                    'exclude_interfaces': [],
                    'include_interfaces': []
                },
                'docker_collector': {
                    'enabled': True,
                    'docker_socket': '/var/run/docker.sock'
                },
                'web_service_collector': {
                    'enabled': False,
                    'services': [],
                    'timeout': 10,
                    'verify_ssl': True
                }
            },
            'alerts': {
                'enabled': True,
                'cpu': {
                    'high_usage': {
                        'threshold': 90,
                        'duration': 300  # Durée en secondes pendant laquelle le seuil doit être dépassé
                    }
                },
                'memory': {
                    'high_usage': {
                        'threshold': 90,
                        'duration': 300
                    }
                },
                'disk': {
                    'high_usage': {
                        'threshold': 90,
                        'duration': 300
                    }
                }
            }
        }
    
    def load_local_config(self) -> bool:
        """
        Charge la configuration depuis un fichier YAML local
        
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        if not self.config_file or not os.path.exists(self.config_file):
            logger.warning(f"Fichier de configuration local non trouvé: {self.config_file}")
            return False
        
        try:
            with open(self.config_file, 'r') as f:
                local_config = yaml.safe_load(f)
            
            # Fusionner la configuration locale avec la configuration par défaut
            self.config = self._merge_configs(self.default_config, local_config)
            logger.info(f"Configuration locale chargée depuis {self.config_file}")
            
            # Mettre à jour l'utilisation de la configuration distante
            self.use_remote_config = self.config.get('agent', {}).get('use_remote_config', True)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration locale: {e}")
            # Utiliser la configuration par défaut en cas d'erreur
            self.config = deepcopy(self.default_config)
            return False
    
    def save_local_config(self, config_file: Optional[str] = None) -> bool:
        """
        Sauvegarde la configuration actuelle dans un fichier YAML local
        
        Args:
            config_file: Chemin vers le fichier de configuration à sauvegarder (si différent)
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            save_path = config_file or self.config_file
            if not save_path:
                logger.error("Aucun chemin de fichier spécifié pour sauvegarder la configuration")
                return False
            
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Configuration sauvegardée dans {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def fetch_remote_config(self) -> bool:
        """
        Récupère la configuration depuis l'API distante
        
        Returns:
            bool: True si la récupération a réussi, False sinon
        """
        if not self.use_remote_config:
            logger.info("Configuration distante désactivée")
            return False
        
        # Vérifier si l'API client est configuré
        if not self.api_client:
            try:
                api_config = self.config.get('api', {})
                if not api_config.get('uuid') or not api_config.get('token'):
                    logger.error("UUID ou token d'API non configuré")
                    return False
                
                self.api_client = ApiClient(
                    base_url=api_config.get('base_url', 'https://monitoring.example.com'),
                    agent_uuid=api_config.get('uuid', ''),
                    agent_token=api_config.get('token', ''),
                    timeout=api_config.get('timeout', 30)
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du client API: {e}")
                return False
        
        try:
            # Récupérer la configuration depuis l'API
            remote_config = self.api_client.get_configuration()
            
            if not remote_config:
                logger.warning("Configuration distante vide")
                return False
            
            # Fusionner la configuration distante avec la configuration actuelle
            self.config = self._merge_configs(self.config, remote_config)
            self.last_remote_config_fetch = time.time()
            
            logger.info("Configuration distante récupérée avec succès")
            
            # Sauvegarder la configuration fusionnée localement si spécifié
            if self.config.get('agent', {}).get('save_remote_config', False):
                self.save_local_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la configuration distante: {e}")
            return False
    
    def get_config(self, section: Optional[str] = None, key: Optional[str] = None) -> Any:
        """
        Retourne la configuration ou une section/clé spécifique
        
        Args:
            section: Nom de la section (optionnel)
            key: Nom de la clé dans la section (optionnel)
            
        Returns:
            Any: La configuration complète ou la section/valeur demandée
        """
        # Si la configuration distante est activée et que l'intervalle est dépassé, la récupérer
        remote_config_interval = self.config.get('agent', {}).get('remote_config_interval', 300)
        if (self.use_remote_config and 
            time.time() - self.last_remote_config_fetch > remote_config_interval):
            self.fetch_remote_config()
        
        # Retourner la configuration complète
        if section is None:
            return self.config
        
        # Retourner une section spécifique
        if key is None:
            return self.config.get(section, {})
        
        # Retourner une clé spécifique dans une section
        return self.config.get(section, {}).get(key)
    
    def update_config(self, new_config: Dict[str, Any], merge: bool = True) -> None:
        """
        Met à jour la configuration
        
        Args:
            new_config: Nouvelle configuration
            merge: Si True, fusionne la nouvelle configuration avec l'existante, sinon la remplace
        """
        if merge:
            self.config = self._merge_configs(self.config, new_config)
        else:
            self.config = deepcopy(new_config)
    
    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fusionne deux configurations (récursivement)
        
        Args:
            base_config: Configuration de base
            override_config: Configuration qui écrase la base
            
        Returns:
            Dict[str, Any]: Configuration fusionnée
        """
        result = deepcopy(base_config)
        
        for key, value in override_config.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Récursivement fusionner les sous-dictionnaires
                result[key] = self._merge_configs(result[key], value)
            else:
                # Écraser la valeur
                result[key] = deepcopy(value)
        
        return result 