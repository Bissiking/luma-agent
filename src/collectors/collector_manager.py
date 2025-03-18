import importlib
import os
import logging
from typing import Dict, List, Any, Optional, Type

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class CollectorManager:
    """
    Gestionnaire de collecteurs qui charge dynamiquement et exécute les collecteurs de métriques.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le gestionnaire de collecteurs
        
        Args:
            config: Configuration globale pour tous les collecteurs
        """
        self.config = config or {}
        self.collectors: Dict[str, BaseCollector] = {}
        
    def discover_collectors(self, package_path: str = "src.collectors") -> List[str]:
        """
        Découvre automatiquement les collecteurs disponibles dans le package spécifié
        
        Args:
            package_path: Chemin du package contenant les collecteurs
            
        Returns:
            List[str]: Liste des noms de modules de collecteurs disponibles
        """
        collector_modules = []
        
        # Convertir le chemin du package en chemin de système de fichiers
        package_parts = package_path.split('.')
        package_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), *package_parts[1:])
        
        try:
            for file in os.listdir(package_dir):
                if (file.endswith('.py') and 
                    not file.startswith('__') and 
                    file != 'base_collector.py' and 
                    file != 'collector_manager.py'):
                    collector_modules.append(file[:-3])  # Enlever l'extension .py
        except Exception as e:
            logger.error(f"Erreur lors de la découverte des collecteurs: {e}")
        
        return collector_modules
    
    def load_collector(self, collector_name: str, module_path: str = "src.collectors") -> bool:
        """
        Charge un collecteur spécifique
        
        Args:
            collector_name: Nom du module collecteur (sans l'extension .py)
            module_path: Chemin du package où se trouve le collecteur
            
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        try:
            # Importer le module
            full_module_path = f"{module_path}.{collector_name}"
            module = importlib.import_module(full_module_path)
            
            # Trouver la classe de collecteur (qui hérite de BaseCollector)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseCollector) and 
                    attr is not BaseCollector):
                    
                    # Créer une instance avec la configuration spécifique au collecteur
                    collector_config = self.config.get(collector_name, {})
                    collector_instance = attr(config=collector_config)
                    
                    if collector_instance.validate_config():
                        self.collectors[collector_name] = collector_instance
                        logger.info(f"Collecteur '{collector_name}' chargé avec succès")
                        return True
                    else:
                        logger.warning(f"Configuration invalide pour le collecteur '{collector_name}'")
                        return False
            
            logger.warning(f"Aucune classe de collecteur trouvée dans le module '{collector_name}'")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du collecteur '{collector_name}': {e}")
            return False
    
    def load_all_collectors(self) -> None:
        """
        Charge tous les collecteurs disponibles
        """
        collector_modules = self.discover_collectors()
        for collector_name in collector_modules:
            self.load_collector(collector_name)
    
    def collect_all(self) -> Dict[str, Any]:
        """
        Exécute tous les collecteurs chargés et rassemble leurs données
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant toutes les métriques collectées
        """
        results = {}
        
        for collector_name, collector in self.collectors.items():
            try:
                logger.debug(f"Collecte des métriques avec {collector_name}")
                metrics = collector.collect()
                results[collector_name] = metrics
            except Exception as e:
                logger.error(f"Erreur lors de la collecte avec '{collector_name}': {e}")
                results[collector_name] = {"error": str(e)}
        
        return results
    
    def get_collector(self, collector_name: str) -> Optional[BaseCollector]:
        """
        Récupère un collecteur spécifique par son nom
        
        Args:
            collector_name: Nom du collecteur
            
        Returns:
            Optional[BaseCollector]: L'instance du collecteur ou None si non trouvé
        """
        return self.collectors.get(collector_name)
    
    def collect_specific(self, collector_name: str) -> Optional[Dict[str, Any]]:
        """
        Exécute un collecteur spécifique par son nom
        
        Args:
            collector_name: Nom du collecteur à exécuter
            
        Returns:
            Optional[Dict[str, Any]]: Métriques collectées ou None si le collecteur n'existe pas
        """
        collector = self.get_collector(collector_name)
        if collector:
            try:
                return collector.collect()
            except Exception as e:
                logger.error(f"Erreur lors de la collecte avec '{collector_name}': {e}")
                return {"error": str(e)}
        return None 