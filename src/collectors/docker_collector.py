import os
import json
import socket
import time
from typing import Dict, Any, List, Optional

from .base_collector import BaseCollector


class DockerCollector(BaseCollector):
    """
    Collecteur de métriques Docker.
    Collecte des informations sur les conteneurs Docker en cours d'exécution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.docker_socket = self.config.get('docker_socket', '/var/run/docker.sock')
        self.docker_available = False
        self.check_docker_availability()
    
    def check_docker_availability(self) -> bool:
        """
        Vérifie si Docker est disponible sur le système
        
        Returns:
            bool: True si Docker est disponible
        """
        try:
            # Vérifier si le socket Docker existe
            if not os.path.exists(self.docker_socket):
                return False
            
            # Essayer de se connecter au socket Docker
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(3)
            client.connect(self.docker_socket)
            client.close()
            
            self.docker_available = True
            return True
        except Exception:
            self.docker_available = False
            return False
    
    def collect(self) -> Dict[str, Any]:
        """
        Collecte et retourne toutes les métriques Docker
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant les métriques Docker
        """
        # Si Docker n'est pas disponible, retourner un résultat vide ou indiquer l'indisponibilité
        if not self.docker_available and not self.check_docker_availability():
            return {
                'available': False,
                'error': 'Docker n\'est pas disponible sur ce système'
            }
        
        metrics = {
            'available': True,
            'version': self._get_docker_version(),
            'containers': self._get_containers(),
            'images': self._get_images_count(),
            'stats': self._get_container_stats()
        }
        
        # Ajouter les seuils si configurés
        if 'thresholds' in self.config:
            metrics['thresholds'] = self.config['thresholds']
        
        return metrics
    
    def _send_docker_request(self, method: str, path: str) -> Dict[str, Any]:
        """
        Envoie une requête HTTP à l'API Docker via le socket Unix
        
        Args:
            method: Méthode HTTP (GET, POST, etc.)
            path: Chemin de l'API Docker
            
        Returns:
            Dict[str, Any]: Réponse JSON de l'API Docker
        """
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(5)
            client.connect(self.docker_socket)
            
            # Préparer la requête HTTP
            request = f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode('utf-8')
            client.send(request)
            
            # Recevoir la réponse
            response = b""
            while True:
                data = client.recv(4096)
                if not data:
                    break
                response += data
            
            client.close()
            
            # Extraire le corps JSON de la réponse HTTP
            body = response.split(b'\r\n\r\n', 1)[1]
            
            # Gérer les cas où la réponse n'est pas du JSON
            if not body:
                return {}
            
            return json.loads(body)
        except Exception as e:
            return {"error": str(e)}
    
    def _get_docker_version(self) -> Dict[str, Any]:
        """
        Obtient la version de Docker
        
        Returns:
            Dict[str, Any]: Informations sur la version de Docker
        """
        return self._send_docker_request("GET", "/version")
    
    def _get_containers(self) -> List[Dict[str, Any]]:
        """
        Obtient la liste des conteneurs Docker
        
        Returns:
            List[Dict[str, Any]]: Liste des conteneurs
        """
        # Requête pour obtenir tous les conteneurs (y compris ceux qui ne sont pas en cours d'exécution)
        result = self._send_docker_request("GET", "/containers/json?all=true")
        
        if isinstance(result, list):
            return result
        return []
    
    def _get_images_count(self) -> int:
        """
        Obtient le nombre d'images Docker
        
        Returns:
            int: Nombre d'images
        """
        result = self._send_docker_request("GET", "/images/json")
        
        if isinstance(result, list):
            return len(result)
        return 0
    
    def _get_container_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtient les statistiques des conteneurs Docker en cours d'exécution
        
        Returns:
            Dict[str, Dict[str, Any]]: Statistiques par conteneur
        """
        stats = {}
        containers = self._get_containers()
        
        for container in containers:
            try:
                # Vérifier si le conteneur est en cours d'exécution
                if container.get('State') == 'running':
                    container_id = container.get('Id', '')
                    if container_id:
                        # Obtenir les statistiques pour ce conteneur (sans streaming)
                        container_stats = self._send_docker_request("GET", f"/containers/{container_id}/stats?stream=false")
                        stats[container_id] = container_stats
            except Exception:
                pass
        
        return stats 