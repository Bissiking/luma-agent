from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseCollector(ABC):
    """
    Classe de base abstraite pour tous les collecteurs de métriques.
    Chaque collecteur doit hériter de cette classe et implémenter les méthodes requises.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le collecteur avec une configuration optionnelle
        
        Args:
            config: Dictionnaire de configuration pour le collecteur
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """
        Méthode principale pour collecter les métriques.
        À implémenter par chaque classe héritière.
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant les métriques collectées
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Valide la configuration du collecteur.
        Peut être surchargée par les classes enfants pour une validation spécifique.
        
        Returns:
            bool: True si la configuration est valide, False sinon
        """
        return True
    
    def __str__(self) -> str:
        return f"{self.name} Collector" 