import time
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from .base_collector import BaseCollector


class WebServiceCollector(BaseCollector):
    """
    Collecteur pour les services web.
    Vérifie l'état de services web via des requêtes HTTP/HTTPS.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Configuration des services à surveiller (liste d'URLs)
        self.services = self.config.get('services', [])
        # Timeout pour les requêtes HTTP
        self.timeout = self.config.get('timeout', 10)
        # Headers HTTP à inclure dans les requêtes
        self.headers = self.config.get('headers', {})
        # Suivre les redirections
        self.allow_redirects = self.config.get('allow_redirects', True)
        # Vérifier les certificats SSL
        self.verify_ssl = self.config.get('verify_ssl', True)
    
    def collect(self) -> Dict[str, Any]:
        """
        Collecte et retourne les données sur l'état des services web
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant les résultats des vérifications
        """
        # Si aucun service n'est configuré, retourner un résultat vide
        if not self.services:
            return {
                'services': [],
                'error': 'Aucun service web configuré pour la surveillance'
            }
        
        # Vérifier chaque service
        results = {
            'services': [self._check_service(service) for service in self.services]
        }
        
        # Ajouter les seuils si configurés
        if 'thresholds' in self.config:
            results['thresholds'] = self.config['thresholds']
        
        return results
    
    def _check_service(self, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie l'état d'un service web spécifique
        
        Args:
            service_config: Configuration du service à vérifier
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        url = service_config.get('url')
        if not url:
            return {
                'status': 'error',
                'error': 'URL manquante dans la configuration du service'
            }
        
        # Options spécifiques à ce service
        method = service_config.get('method', 'GET')
        timeout = service_config.get('timeout', self.timeout)
        headers = {**self.headers, **service_config.get('headers', {})}
        verify_ssl = service_config.get('verify_ssl', self.verify_ssl)
        allow_redirects = service_config.get('allow_redirects', self.allow_redirects)
        expected_status = service_config.get('expected_status', [200])
        expected_content = service_config.get('expected_content')
        
        # Créer un résultat de base avec les informations du service
        result = {
            'url': url,
            'method': method,
            'name': service_config.get('name', url),
            'status': 'unknown',
            'timestamp': time.time()
        }
        
        try:
            # Mesurer le temps de réponse
            start_time = time.time()
            
            # Effectuer la requête HTTP
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                verify=verify_ssl,
                allow_redirects=allow_redirects
            )
            
            # Calculer le temps de réponse
            response_time = time.time() - start_time
            
            # Vérifier si le statut est celui attendu
            status_ok = response.status_code in expected_status if isinstance(expected_status, list) else response.status_code == expected_status
            
            # Vérifier si le contenu est celui attendu (si spécifié)
            content_ok = True
            if expected_content is not None:
                content_ok = expected_content in response.text
            
            # Déterminer le statut global
            if status_ok and content_ok:
                result['status'] = 'ok'
            else:
                result['status'] = 'error'
                if not status_ok:
                    result['error'] = f"Statut HTTP inattendu: {response.status_code}"
                elif not content_ok:
                    result['error'] = "Contenu attendu non trouvé dans la réponse"
            
            # Ajouter des détails sur la réponse
            result['response'] = {
                'status_code': response.status_code,
                'response_time': response_time,
                'headers': dict(response.headers),
                'content_length': len(response.content),
                'content_ok': content_ok
            }
            
        except requests.exceptions.Timeout:
            result['status'] = 'error'
            result['error'] = f"Timeout après {timeout} secondes"
        except requests.exceptions.SSLError:
            result['status'] = 'error'
            result['error'] = "Erreur SSL lors de la connexion"
        except requests.exceptions.ConnectionError:
            result['status'] = 'error'
            result['error'] = "Impossible de se connecter au service"
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result 