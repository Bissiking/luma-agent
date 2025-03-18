import json
import logging
import time
import socket
import platform
import psutil
from typing import Dict, Any, Optional, List
import requests
from urllib.parse import urljoin

from .routes import ApiRoutes
from src.constants import VERSION, DEFAULT_CONFIG

try:
    import cpuinfo
except ImportError:
    cpuinfo = None

logger = logging.getLogger(__name__)


class ApiClient:
    """
    Client API pour communiquer avec le serveur LUMA Monitoring.
    Gère l'authentification et les requêtes vers les différents endpoints.
    """
    
    def __init__(self, base_url: str, agent_uuid: str, agent_token: str, timeout: int = 30, agent_version: str = "P-2.0.0-Grizzly"):
        """
        Initialise le client API
        
        Args:
            base_url: URL de base de l'API (ex: https://dev.mhemery.fr/api/monitoring)
            agent_uuid: UUID unique de l'agent
            agent_token: Token d'authentification de l'agent (Bearer Token)
            timeout: Timeout pour les requêtes HTTP (en secondes)
            agent_version: Version de l'agent
        """
        self.base_url = base_url.rstrip('/')
        self.agent_uuid = agent_uuid
        self.agent_token = agent_token
        self.timeout = timeout
        self.agent_version = agent_version
        self.session = requests.Session()
        
        # Définir les headers d'authentification par défaut (Bearer Token)
        self.session.headers.update({
            'Authorization': f'Bearer {self.agent_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API
        
        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Endpoint de l'API (sera ajouté à l'URL de base)
            data: Données à envoyer (pour POST, PUT, etc.)
            params: Paramètres de requête à ajouter à l'URL
            
        Returns:
            Dict[str, Any]: Réponse JSON de l'API
            
        Raises:
            Exception: Si la requête échoue
        """
        # Remplacer {uuid} dans l'endpoint par l'UUID de l'agent si présent
        if '{uuid}' in endpoint:
            endpoint = endpoint.replace('{uuid}', self.agent_uuid)
        
        # Remplacer {id} dans l'endpoint par l'UUID de l'agent si présent
        if '{id}' in endpoint:
            endpoint = endpoint.replace('{id}', self.agent_uuid)
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            start_time = time.time()
            
            kwargs = {
                'timeout': self.timeout
            }
            
            if data is not None:
                kwargs['json'] = data
            
            if params is not None:
                kwargs['params'] = params
            
            response = self.session.request(
                method=method,
                url=url,
                **kwargs
            )
            
            response_time = time.time() - start_time
            
            # Vérifier si la réponse est un succès (code 2xx)
            response.raise_for_status()
            
            # Parser la réponse JSON
            try:
                result = response.json()
            except ValueError:
                # Si la réponse n'est pas du JSON valide
                result = {
                    'success': False,
                    'message': 'Invalid JSON response',
                    'data': response.text
                }
            
            # Vérifier si l'API indique une erreur
            if not result.get('success', True):
                error_info = result.get('error', {})
                error_code = error_info.get('code', 'UNKNOWN')
                error_message = error_info.get('message', result.get('message', 'Unknown error'))
                raise Exception(f"API error ({error_code}): {error_message}")
            
            logger.debug(f"API request to {endpoint} completed in {response_time:.2f}s")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"API request to {endpoint} timed out after {self.timeout}s")
            raise Exception(f"API request timed out: {endpoint}")
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for API request to {endpoint}")
            raise Exception(f"API connection error: {endpoint}")
            
        except requests.exceptions.HTTPError as e:
            # Si le serveur a retourné une erreur HTTP
            logger.error(f"HTTP error for API request to {endpoint}: {e}")
            
            # Essayer de parser la réponse d'erreur
            try:
                error_data = response.json()
                error_message = error_data.get('message', str(e))
                error_code = error_data.get('error', {}).get('code', 'HTTP_ERROR')
            except ValueError:
                error_message = str(e)
                error_code = 'HTTP_ERROR'
            
            raise Exception(f"API HTTP error ({error_code}): {error_message}")
            
        except Exception as e:
            logger.error(f"Unknown error for API request to {endpoint}: {e}")
            raise Exception(f"API request failed: {str(e)}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """
        Collecte les informations système pour le check-in
        
        Returns:
            Dict[str, Any]: Informations système
        """
        try:
            # Obtenir les informations de base sur le système
            os_info = platform.system() + " " + platform.release()
            
            # Obtenir les informations CPU
            cpu_info = platform.processor()
            if not cpu_info and cpuinfo:
                try:
                    cpu_info = cpuinfo.get_cpu_info().get('brand_raw', 'Unknown CPU')
                except:
                    cpu_info = "Unknown CPU"
            
            # Obtenir la mémoire totale
            mem_info = psutil.virtual_memory()
            mem_total_gb = round(mem_info.total / (1024 ** 3), 2)
            
            # Obtenir les informations sur le noyau
            kernel_version = platform.release()
            
            # Obtenir l'architecture
            arch = platform.machine()
            
            return {
                "os": os_info,
                "kernel": kernel_version,
                "architecture": arch,
                "cpu": cpu_info,
                "memory_total_gb": mem_total_gb
            }
        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            return {
                "os": platform.system(),
                "kernel": "Unknown",
                "architecture": platform.machine(),
                "cpu": "Unknown",
                "memory_total_gb": 0
            }
    
    def _get_hostname(self) -> str:
        """
        Obtient le nom d'hôte de la machine
        
        Returns:
            str: Nom d'hôte
        """
        try:
            return socket.gethostname()
        except:
            return "unknown-host"
    
    def _get_ip_address(self) -> str:
        """
        Obtient l'adresse IP principale de la machine
        
        Returns:
            str: Adresse IP
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Se connecter à un DNS externe pour déterminer l'interface de routage par défaut
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_platform_info(self) -> Dict[str, Any]:
        """
        Obtient des informations sur la plateforme système
        
        Returns:
            Dict[str, Any]: Informations sur la plateforme
        """
        try:
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations de plateforme: {e}")
            return {
                "system": platform.system(),
                "error": str(e)
            }
            
    def _get_collector_status(self) -> Dict[str, bool]:
        """
        Retourne l'état des collecteurs
        
        Returns:
            Dict[str, bool]: État des collecteurs (activé/désactivé)
        """
        # Dans une implémentation réelle, cela proviendrait de la configuration
        return {
            "cpu": True,
            "memory": True,
            "disk": True,
            "network": True,
            "docker": False,
            "web_service": False
        }
    
    def checkin(self) -> Dict[str, Any]:
        """
        Enregistrement périodique de l'agent auprès du serveur LUMA
        
        Retourne les informations sur l'agent, y compris la configuration et
        les instructions du serveur.
        
        Returns:
            Dict[str, Any]: Réponse du serveur
        """
        try:
            endpoint = ApiRoutes.CHECKIN
            
            # Préparer les données pour l'enregistrement
            checkin_data = {
                "timestamp": int(time.time()),
                "status": "active",
                "agent_info": {
                    "version": VERSION,  # Utilise la version depuis constants.py
                    "hostname": self._get_hostname(),
                    "platform": self._get_platform_info(),
                    "collectors": self._get_collector_status()
                }
            }
            
            response = self._make_request(
                "POST",
                endpoint,
                data=checkin_data
            )
            
            # Traiter la réponse
            if response:
                logger.debug("Enregistrement réussi auprès du serveur LUMA")
                return response
            else:
                logger.warning("Aucune réponse reçue pour l'enregistrement")
                return {}
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement: {str(e)}")
            return {"error": str(e)}
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Récupère la configuration de l'agent depuis LUMA
        
        Cette méthode récupère la configuration complète de l'agent depuis LUMA.
        Si aucune configuration n'existe, l'agent essaie de la créer sur LUMA
        en utilisant le modèle de configuration par défaut.
        
        Returns:
            Dict[str, Any]: Configuration de l'agent ou None en cas d'erreur
        """
        try:
            logger.info("Récupération de la configuration depuis LUMA...")
            endpoint = ApiRoutes.CONFIG
            
            # Ajouter la version en paramètre
            params = {
                'version': VERSION
            }
            
            # Première tentative : récupération de la configuration
            response = self._make_request("GET", endpoint, params=params)
            
            # Si une configuration est trouvée, la retourner
            if response and 'data' in response and 'config' in response['data']:
                logger.info("Configuration trouvée sur LUMA")
                return response['data']['config']
            
            # Si aucune configuration n'est trouvée, essayer de la créer
            logger.warning("Aucune configuration trouvée sur LUMA, tentative de création...")
            
            # Créer une configuration par défaut avec les valeurs de l'agent
            default_config = DEFAULT_CONFIG.copy()
            
            # Ajouter les informations système de base
            default_config['agent']['version'] = VERSION
            default_config['agent']['hostname'] = self._get_hostname()
            default_config['agent']['platform'] = self._get_platform_info()
            
            # Préserver les informations d'API
            default_config['api']['base_url'] = self.base_url
            default_config['api']['uuid'] = self.agent_uuid
            default_config['api']['token'] = self.agent_token
            
            # Envoyer la configuration par défaut
            creation_response = self._make_request("POST", endpoint, data=default_config, params=params)
            
            if creation_response and 'data' in creation_response and 'config' in creation_response['data']:
                logger.info("Configuration créée avec succès sur LUMA")
                return creation_response['data']['config']
            
            logger.error("Impossible de créer une configuration sur LUMA")
            return None
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la configuration: {str(e)}")
            return None
    
    def _convert_metrics_format(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertit les métriques du format interne au format attendu par l'API
        
        Args:
            metrics: Dictionnaire contenant les métriques collectées
            
        Returns:
            Dict[str, Any]: Métriques au format attendu par l'API
        """
        # Nouveau format pour les métriques conforme à la demande
        result = {
            'metrics': []
        }
        
        # Convertir les métriques CPU
        if 'cpu_collector' in metrics:
            cpu_metrics = metrics['cpu_collector']
            
            # Utilisation CPU
            if 'percent' in cpu_metrics:
                result['metrics'].append({
                    'name': 'cpu_usage',
                    'value': cpu_metrics['percent'],
                    'unit': '%'
                })
            
            # Load averages si disponibles (Linux uniquement)
            if 'stats' in cpu_metrics and 'loadavg_1min' in cpu_metrics['stats']:
                result['metrics'].append({
                    'name': 'load_average_1m',
                    'value': cpu_metrics['stats']['loadavg_1min'],
                    'unit': ''
                })
                result['metrics'].append({
                    'name': 'load_average_5m',
                    'value': cpu_metrics['stats']['loadavg_5min'],
                    'unit': ''
                })
                result['metrics'].append({
                    'name': 'load_average_15m',
                    'value': cpu_metrics['stats']['loadavg_15min'],
                    'unit': ''
                })
            
        # Convertir les métriques mémoire
        if 'memory_collector' in metrics and 'virtual' in metrics['memory_collector']:
            mem_metrics = metrics['memory_collector']['virtual']
            
            result['metrics'].append({
                'name': 'memory_total',
                'value': mem_metrics.get('total', 0) / (1024 * 1024),  # Convertir en MB
                'unit': 'MB'
            })
            result['metrics'].append({
                'name': 'memory_used',
                'value': mem_metrics.get('used', 0) / (1024 * 1024),  # Convertir en MB
                'unit': 'MB'
            })
            result['metrics'].append({
                'name': 'memory_free',
                'value': mem_metrics.get('available', 0) / (1024 * 1024),  # Convertir en MB
                'unit': 'MB'
            })
            result['metrics'].append({
                'name': 'memory_usage',
                'value': mem_metrics.get('percent', 0),
                'unit': '%'
            })
            
        # Convertir les métriques disque
        if 'disk_collector' in metrics and 'usage' in metrics['disk_collector']:
            disk_metrics = metrics['disk_collector']['usage']
            
            # Pour chaque partition
            for mount_point, disk_data in disk_metrics.items():
                prefix = 'disk_' + mount_point.replace('/', '_').strip('_')
                if not prefix or prefix == 'disk_':
                    prefix = 'disk_root'
                
                result['metrics'].append({
                    'name': f"{prefix}_total",
                    'value': disk_data.get('total', 0) / (1024 * 1024),  # Convertir en MB
                    'unit': 'MB'
                })
                result['metrics'].append({
                    'name': f"{prefix}_used",
                    'value': disk_data.get('used', 0) / (1024 * 1024),  # Convertir en MB
                    'unit': 'MB'
                })
                result['metrics'].append({
                    'name': f"{prefix}_free",
                    'value': disk_data.get('free', 0) / (1024 * 1024),  # Convertir en MB
                    'unit': 'MB'
                })
                result['metrics'].append({
                    'name': f"{prefix}_usage",
                    'value': disk_data.get('percent', 0),
                    'unit': '%'
                })
                
        # Convertir les métriques réseau
        if 'network_collector' in metrics and 'io' in metrics['network_collector']:
            net_metrics = metrics['network_collector']['io']
            
            # Agréger toutes les interfaces
            total_bytes_sent = 0
            total_bytes_recv = 0
            total_packets_sent = 0
            total_packets_recv = 0
            
            for nic, nic_data in net_metrics.items():
                total_bytes_sent += nic_data.get('bytes_sent', 0)
                total_bytes_recv += nic_data.get('bytes_recv', 0)
                total_packets_sent += nic_data.get('packets_sent', 0)
                total_packets_recv += nic_data.get('packets_recv', 0)
            
            result['metrics'].append({
                'name': 'network_bytes_sent',
                'value': total_bytes_sent,
                'unit': 'bytes'
            })
            result['metrics'].append({
                'name': 'network_bytes_recv',
                'value': total_bytes_recv,
                'unit': 'bytes'
            })
            result['metrics'].append({
                'name': 'network_packets_sent',
                'value': total_packets_sent,
                'unit': 'packets'
            })
            result['metrics'].append({
                'name': 'network_packets_recv',
                'value': total_packets_recv,
                'unit': 'packets'
            })
            
            # Ajouter les taux si disponibles
            if 'rates' in metrics['network_collector']:
                rates = metrics['network_collector']['rates']
                for nic, rate_data in rates.items():
                    result['metrics'].append({
                        'name': f"network_{nic}_bytes_sent_per_sec",
                        'value': rate_data.get('bytes_sent_per_sec', 0),
                        'unit': 'bytes/s'
                    })
                    result['metrics'].append({
                        'name': f"network_{nic}_bytes_recv_per_sec",
                        'value': rate_data.get('bytes_recv_per_sec', 0),
                        'unit': 'bytes/s'
                    })
        
        # Ajouter les métriques des services web si présents
        if 'web_service_collector' in metrics and 'services' in metrics['web_service_collector']:
            web_services = metrics['web_service_collector']['services']
            
            # Vérifier si web_services est un dictionnaire ou une liste
            if isinstance(web_services, dict):
                # Si c'est un dictionnaire, itérer avec .items()
                for service_name, service_data in web_services.items():
                    if isinstance(service_data, dict) and 'response' in service_data and 'response_time' in service_data['response']:
                        result['metrics'].append({
                            'name': f"web_{service_name.lower().replace(' ', '_')}_response_time",
                            'value': service_data['response']['response_time'],
                            'unit': 'ms'
                        })
                        
                        if 'status_code' in service_data['response']:
                            result['metrics'].append({
                                'name': f"web_{service_name.lower().replace(' ', '_')}_status_code",
                                'value': service_data['response']['status_code'],
                                'unit': ''
                            })
            elif isinstance(web_services, list):
                # Si c'est une liste, itérer directement
                for service_data in web_services:
                    if isinstance(service_data, dict):
                        service_name = service_data.get('name', 'unknown')
                        if 'response' in service_data and 'response_time' in service_data['response']:
                            result['metrics'].append({
                                'name': f"web_{service_name.lower().replace(' ', '_')}_response_time",
                                'value': service_data['response']['response_time'],
                                'unit': 'ms'
                            })
                            
                            if 'status_code' in service_data['response']:
                                result['metrics'].append({
                                    'name': f"web_{service_name.lower().replace(' ', '_')}_status_code",
                                    'value': service_data['response']['status_code'],
                                    'unit': ''
                                })
        
        # Ajouter les métriques Docker si présentes
        if 'docker_collector' in metrics and 'containers' in metrics['docker_collector']:
            docker_metrics = metrics['docker_collector']['containers']
            
            result['metrics'].append({
                'name': 'docker_containers_running',
                'value': docker_metrics.get('running', 0),
                'unit': ''
            })
            result['metrics'].append({
                'name': 'docker_containers_total',
                'value': docker_metrics.get('total', 0),
                'unit': ''
            })
        
        return result
    
    def _determine_alert_level(self, alert: Dict[str, Any]) -> str:
        """
        Détermine le niveau d'alerte en fonction du type et du statut
        
        Args:
            alert: Informations sur l'alerte
            
        Returns:
            str: Niveau d'alerte (warning, critical, info)
        """
        status = alert.get('status', '')
        
        if status == 'resolved':
            return 'info'
        
        # Par défaut, considérer toutes les alertes comme des avertissements
        level = 'warning'
        
        # Déterminer le niveau en fonction du type et des valeurs
        alert_type = alert.get('type', '')
        
        if 'cpu' in alert_type or 'memory' in alert_type or 'disk' in alert_type:
            value = alert.get('value', 0)
            threshold = alert.get('threshold', 90)
            
            # Si la valeur est très élevée par rapport au seuil, la considérer comme critique
            if value >= threshold + 10:
                level = 'critical'
        
        # Cas spécial pour les services web
        if 'web_service' in alert_type:
            level = 'critical'
        
        return level
    
    def send_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envoie les métriques collectées au serveur central
        
        Args:
            metrics: Dictionnaire contenant les métriques à envoyer
            
        Returns:
            Dict[str, Any]: Réponse du serveur
        """
        endpoint = ApiRoutes.METRICS
        
        # Convertir les métriques au format attendu par l'API
        formatted_metrics = self._convert_metrics_format(metrics)
        
        return self._make_request("POST", endpoint, formatted_metrics)
    
    def send_metrics_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envoie un lot de métriques collectées au serveur central
        
        Args:
            batch_data: Dictionnaire contenant le lot de métriques à envoyer
            
        Returns:
            Dict[str, Any]: Réponse du serveur
        """
        endpoint = ApiRoutes.METRICS_GLOBAL
        
        # Formater chaque entrée du lot pour l'API global
        formatted_batch = {
            'agent_uuid': self.agent_uuid,
            'timestamp': batch_data.get('timestamp', int(time.time())),
            'collectors': {}
        }
        
        # Fusionner toutes les métriques par collecteur
        for entry in batch_data.get('metrics_batch', []):
            timestamp = entry.get('timestamp', int(time.time()))
            metrics_data = entry.get('data', {})
            
            # Pour chaque collecteur dans cette entrée
            for collector_name, collector_data in metrics_data.items():
                # Si ce collecteur n'existe pas encore dans notre résultat, l'initialiser
                if collector_name not in formatted_batch['collectors']:
                    formatted_batch['collectors'][collector_name] = {
                        'entries': []
                    }
                
                # Ajouter cette entrée avec son timestamp
                formatted_batch['collectors'][collector_name]['entries'].append({
                    'timestamp': timestamp,
                    'data': collector_data
                })
        
        return self._make_request("POST", endpoint, formatted_batch)
    
    def send_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Signale une alerte au serveur central
        
        Args:
            alert: Informations sur l'alerte
            
        Returns:
            Dict[str, Any]: Réponse du serveur
        """
        endpoint = ApiRoutes.ALERTS
        
        # Ajouter un timestamp à l'alerte si non présent
        timestamp = int(time.time())
        if 'timestamp' not in alert:
            alert['timestamp'] = timestamp
        
        # Déterminer le service concerné
        service_id = "system"
        if 'web_service' in alert.get('type', ''):
            service_name = alert.get('service_name', 'unknown').lower().replace(' ', '_')
            service_id = f"web_{service_name}"
        elif 'docker' in alert.get('type', ''):
            service_id = "docker"
        
        # Déterminer le niveau d'alerte
        level = self._determine_alert_level(alert)
        
        # Formater l'alerte selon l'API LUMA Monitoring
        formatted_alert = {
            'agent_id': self.agent_uuid,
            'service_id': service_id,
            'alert_type': alert.get('type', 'unknown'),
            'level': level,
            'title': alert.get('name', 'Unknown alert'),
            'message': alert.get('description', ''),
            'timestamp': timestamp,
            'data': {
                'value': alert.get('value', 0),
                'threshold': alert.get('threshold', 0),
                'duration': alert.get('duration', 0),
                'status': alert.get('status', 'triggered')
            }
        }
        
        return self._make_request("POST", endpoint, formatted_alert)
        
    def send_health_status(self) -> Dict[str, Any]:
        """
        Envoie un statut de santé au serveur pour confirmer que l'agent fonctionne correctement
        
        Returns:
            Dict[str, Any]: Réponse du serveur
        """
        endpoint = ApiRoutes.HEALTH
        
        # Données de base pour le health check
        data = {
            'status': 'operational',
            'timestamp': int(time.time()),
            'version': self.agent_version,
            'hostname': self._get_hostname(),
            'ip_address': self._get_ip_address(),
            'uptime': self._get_uptime()
        }
        
        return self._make_request("POST", endpoint, data)
        
    def _get_uptime(self) -> float:
        """
        Obtient le temps d'exécution du système en secondes
        
        Returns:
            float: Temps d'exécution du système en secondes
        """
        try:
            # Selon le système d'exploitation, différentes méthodes sont utilisées
            if hasattr(psutil, 'boot_time'):
                # Pour Linux et macOS
                return time.time() - psutil.boot_time()
            else:
                # Fallback générique
                return 0
        except:
            return 0 