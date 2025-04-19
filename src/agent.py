#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agent de monitoring système "P-2.0.0-Grizzly"
Collecte des métriques système et les envoie à un serveur central via une API REST.
"""

import os
import sys
import time
import json
import argparse
import signal
import logging
import yaml
import subprocess
from typing import Dict, Any, List, Optional

# Importation des collecteurs
from src.collectors.cpu_collector import CPUCollector
from src.collectors.memory_collector import MemoryCollector
from src.collectors.disk_collector import DiskCollector
from src.collectors.network_collector import NetworkCollector
from src.collectors.docker_collector import DockerCollector
from src.collectors.web_service_collector import WebServiceCollector
from src.collectors.service_collector import ServiceCollector

# Importation des autres composants
from src.collectors import CollectorManager
from src.api.client import ApiClient
from src.config.config_manager import ConfigManager
from src.utils.alerting import AlertManager
from src.utils.logger import setup_logging, get_logger
from src.utils.system_info import is_running_in_docker, get_system_details
from src.utils.metrics_buffer import MetricsBuffer
from src.update.manager import Updater
from src.utils.env_loader import load_env_config  # Importer le module de variables d'environnement

# Importation des constantes
from src.constants import VERSION, DEFAULT_CONFIG


class MonitoringAgent:
    """
    Agent principal de monitoring.
    Gère la configuration, la collecte de métriques et l'envoi au serveur central.
    """
    
    def __init__(self, config_file: str):
        """
        Initialise l'agent de surveillance
        
        Args:
            config_file: Chemin vers le fichier de configuration
        """
        self.running = False
        self.config_file = config_file
        self.logger = None
        self.config = None
        self.api_client = None
        self.collectors = []
        self.last_metrics = {}
        self.alerts = {}
        self.metrics_buffer = None
        
    def setup(self):
        """
        Configure l'agent avec les paramètres du fichier de configuration
        """
        # Charger la configuration
        self.config = self._load_config()
        
        # Configurer le logger
        self._setup_logging()
        
        # Configurer les composants de l'agent
        self._load_collectors()
        self._setup_update_manager()
        self._setup_metrics_buffer()
        
        # Connexion initiale au serveur
        self._checkin()
        
        self.logger.info("Agent configuré avec succès")
        
        # Vérifier si l'agent s'exécute dans Docker
        self.in_docker = is_running_in_docker()
        if self.in_docker:
            self.logger.info("L'agent s'exécute dans un conteneur Docker")
        
        # Gestionnaire de collecteurs
        collectors_config = self.config['collectors']
        self.collector_manager = CollectorManager(config=collectors_config)
        
        # Client API
        api_config = self.config['api']
        if api_config.get('uuid') and api_config.get('token'):
            self.api_client = ApiClient(
                base_url=api_config.get('base_url', 'https://monitoring.example.com'),
                agent_uuid=api_config.get('uuid'),
                agent_token=api_config.get('token'),
                timeout=api_config.get('timeout', 30),
                agent_version=self.version
            )
        else:
            self.api_client = None
            self.logger.warning("UUID ou token d'API non configuré, l'agent fonctionnera en mode local uniquement")
        
        # Gestionnaire d'alertes
        alerts_config = self.config['alerts']
        self.alert_manager = AlertManager(config=alerts_config)
        
        # Configurer la gestion du signal pour l'arrêt propre
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _setup_logging(self) -> None:
        """
        Configure le système de logging
        """
        if not hasattr(self, 'config') or not self.config:
            print("AVERTISSEMENT: Configuration non disponible lors de l'initialisation du logger")
            log_level_str = 'INFO'
            log_file = 'logs/agent.log'
        else:
            log_level_str = self.config.get('agent', {}).get('log_level', 'INFO').upper()
            log_file = self.config.get('agent', {}).get('log_file')
        
        # Convertir le niveau de log
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        
        # Configurer le format des logs
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_date_format = '%Y-%m-%d %H:%M:%S'
        
        # Réinitialiser la configuration de logging
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configurer le logger
        if log_file:
            # Créer le répertoire de logs si nécessaire
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            logging.basicConfig(
                level=log_level,
                format=log_format,
                datefmt=log_date_format,
                filename=log_file,
                filemode='a'
            )
            # Ajouter un handler pour la console
            console = logging.StreamHandler()
            console.setLevel(log_level)
            formatter = logging.Formatter(log_format, datefmt=log_date_format)
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
        else:
            logging.basicConfig(
                level=log_level,
                format=log_format,
                datefmt=log_date_format
            )
        
        # Logger de l'agent
        self.logger = logging.getLogger(__name__)
        self.version = VERSION
        self.logger.info(f"Initialisation de l'agent {self.version}")
        
        # Afficher des informations sur la configuration
        if hasattr(self, 'config') and self.config:
            self.logger.info(f"Configuration chargée avec succès")
            if self.config.get('agent', {}).get('remote_config'):
                self.logger.info("Configuration distante activée")
            self.logger.debug(f"URL API: {self.config.get('api', {}).get('base_url')}")
            self.logger.debug(f"UUID: {self.config.get('api', {}).get('uuid')}")
            self.logger.debug(f"Intervalle: {self.config.get('agent', {}).get('interval', 60)} secondes")
    
    def _handle_signal(self, signum, frame) -> None:
        """
        Gère les signaux de terminaison
        """
        self.logger.info(f"Signal {signum} reçu, arrêt de l'agent...")
        self.running = False
    
    def _load_collectors(self) -> None:
        """
        Charge tous les collecteurs disponibles
        """
        if not hasattr(self, 'config') or not self.config:
            self.logger.error("Configuration non chargée, impossible de charger les collecteurs")
            return
        
        self.logger.info("Chargement des collecteurs...")
        self.collectors = {}
        
        # Importer dynamiquement les collecteurs
        collector_classes = {
            'cpu': CPUCollector,
            'memory': MemoryCollector,
            'disk': DiskCollector,
            'network': NetworkCollector,
            'docker': DockerCollector,
            'web_service': WebServiceCollector,
            'service': ServiceCollector
        }
        
        collectors_config = self.config.get('collectors', {})
        for collector_name, collector_class in collector_classes.items():
            collector_config = collectors_config.get(collector_name, {})
            
            # Vérifier si le collecteur est activé
            if collector_config.get('enabled', False):
                try:
                    self.logger.debug(f"Chargement du collecteur {collector_name}...")
                    self.collectors[f"{collector_name}_collector"] = collector_class(collector_config)
                    self.logger.debug(f"Collecteur {collector_name} chargé avec succès")
                except Exception as e:
                    self.logger.error(f"Erreur lors du chargement du collecteur {collector_name}: {e}")
        
        self.logger.info(f"Collecteurs chargés: {', '.join(self.collectors.keys())}")
    
    def _checkin(self) -> bool:
        """
        Signale que l'agent est actif au serveur central
        
        Returns:
            bool: True si le check-in a réussi, False sinon
        """
        if not self.api_client:
            self.logger.warning("Client API non configuré, check-in impossible")
            return False
        
        try:
            self.logger.info("Check-in avec le serveur central...")
            response = self.api_client.checkin()
            self.logger.info("Check-in réussi")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors du check-in: {e}")
            return False
    
    def collect_and_store_metrics(self) -> Dict[str, Any]:
        """
        Collecte les métriques et les stocke dans le tampon
        
        Returns:
            Dict[str, Any]: Métriques collectées
        """
        # Collecter les métriques
        metrics = self.collect_metrics()
        
        # Stocker les métriques dans le tampon si activé
        if self.metrics_buffer:
            self.metrics_buffer.add_metrics(metrics)
            
            # Nettoyer les métriques expirées
            self.metrics_buffer.clean_expired_metrics()
            
            # Vérifier s'il faut vider le tampon
            if self.metrics_buffer.should_flush():
                self.flush_metrics_buffer()
        
        return metrics
    
    def flush_metrics_buffer(self) -> bool:
        """
        Envoie les métriques stockées dans le tampon au serveur central
        
        Returns:
            bool: True si les métriques ont été envoyées avec succès
        """
        if not self.metrics_buffer:
            return False
        
        if not self.api_client:
            self.logger.warning("Impossible d'envoyer les métriques: client API non configuré")
            return False
        
        # Marquer le début de la tentative d'envoi
        self.metrics_buffer.set_last_flush()
        
        # Récupérer un lot de métriques à envoyer
        batch_size = self.config.get('metrics_buffer', {}).get('batch_size', 50)
        metrics_batch = self.metrics_buffer.get_metrics_to_send(batch_size)
        
        if not metrics_batch:
            return True  # Rien à envoyer
        
        try:
            self.logger.info(f"Envoi d'un lot de {len(metrics_batch)} métriques au serveur central...")
            
            # Préparation du lot pour l'API global
            batch_data = {
                'metrics_batch': metrics_batch,
                'agent_uuid': self.config['api']['uuid'],
                'timestamp': int(time.time())
            }
            
            # Envoyer le lot
            response = self.api_client.send_metrics_batch(batch_data)
            
            # Supprimer les métriques envoyées du tampon
            self.metrics_buffer.remove_sent_metrics(len(metrics_batch))
            
            self.logger.info(f"Lot de métriques envoyé avec succès")
            
            # Envoyer également un statut de santé
            try:
                health_response = self.api_client.send_health_status()
                self.logger.debug("Statut de santé envoyé avec succès")
            except Exception as e:
                self.logger.warning(f"Erreur lors de l'envoi du statut de santé: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du lot de métriques: {e}")
            return False
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collecte les métriques de tous les collecteurs activés
        
        Returns:
            Dict[str, Any]: Métriques collectées
        """
        start_time = time.time()
        self.logger.info("Collecte des métriques...")
        
        metrics = {}
        
        # Initialiser les collecteurs si nécessaire
        if not self.collectors:
            self._load_collectors()
        
        # Collecter les métriques de chaque collecteur
        for collector_name, collector in self.collectors.items():
            try:
                collector_start = time.time()
                collector_metrics = collector.collect()
                collector_time = time.time() - collector_start
                
                if collector_metrics:
                    metrics[collector_name] = collector_metrics
                    self.logger.debug(f"Collecteur {collector_name} exécuté en {collector_time:.3f}s")
                else:
                    self.logger.warning(f"Le collecteur {collector_name} n'a pas retourné de métriques")
            except Exception as e:
                self.logger.error(f"Erreur lors de la collecte des métriques {collector_name}: {e}")
                # Ajouter une métrique d'erreur pour ce collecteur
                if collector_name not in metrics:
                    metrics[collector_name] = {}
                metrics[collector_name]['error'] = str(e)
        
        total_time = time.time() - start_time
        self.logger.info(f"Collecte terminée en {total_time:.3f}s")
        
        # Sauvegarder les métriques pour les alertes
        self.last_metrics = metrics
        
        return metrics
    
    def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Envoie les métriques collectées au serveur central
        
        Args:
            metrics: Métriques à envoyer
            
        Returns:
            bool: True si les métriques ont été envoyées avec succès, False sinon
        """
        # Si le tampon est activé, ajouter les métriques et tenter d'envoyer un lot
        if self.metrics_buffer:
            self.metrics_buffer.add_metrics(metrics)
            return self.flush_metrics_buffer()
        
        # Sinon, utiliser l'envoi direct
        if not self.api_client:
            self.logger.warning("Impossible d'envoyer les métriques: client API non configuré")
            return False
        
        try:
            self.logger.info("Envoi des métriques au serveur central...")
            response = self.api_client.send_metrics(metrics)
            self.logger.info("Métriques envoyées avec succès")
            
            # Envoyer également un statut de santé
            try:
                health_response = self.api_client.send_health_status()
                self.logger.debug("Statut de santé envoyé avec succès")
            except Exception as e:
                self.logger.warning(f"Erreur lors de l'envoi du statut de santé: {e}")
            
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi des métriques: {e}")
            return False
    
    def check_and_send_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Vérifie si des alertes doivent être déclenchées et les envoie au serveur central
        
        Args:
            metrics: Métriques collectées
            
        Returns:
            List[Dict[str, Any]]: Liste des alertes déclenchées
        """
        if not self.api_client:
            self.logger.warning("Impossible d'envoyer les alertes: client API non configuré")
            return []
        
        # Vérifier les alertes
        alerts_config = self.config.get('alerts', {})
        if not alerts_config:
            return []
        
        alerts = []
        
        # Vérifier l'alerte CPU
        if alerts_config.get('high_cpu', {}).get('enabled', False):
            cpu_threshold = alerts_config['high_cpu'].get('threshold', 80)
            cpu_duration = alerts_config['high_cpu'].get('duration', 300)
            
            if 'cpu_collector' in metrics and 'percent' in metrics['cpu_collector']:
                cpu_usage = metrics['cpu_collector']['percent']
                
                if cpu_usage >= cpu_threshold:
                    alerts.append({
                        'type': 'high_cpu_usage',
                        'name': 'CPU Usage Alert',
                        'description': f"CPU usage is {cpu_usage}%, above threshold of {cpu_threshold}%",
                        'value': cpu_usage,
                        'threshold': cpu_threshold,
                        'duration': cpu_duration,
                        'status': 'triggered'
                    })
        
        # Vérifier l'alerte mémoire
        if alerts_config.get('high_memory', {}).get('enabled', False):
            mem_threshold = alerts_config['high_memory'].get('threshold', 90)
            mem_duration = alerts_config['high_memory'].get('duration', 300)
            
            if 'memory_collector' in metrics and 'virtual' in metrics['memory_collector']:
                mem_usage = metrics['memory_collector']['virtual'].get('percent', 0)
                
                if mem_usage >= mem_threshold:
                    alerts.append({
                        'type': 'high_memory_usage',
                        'name': 'Memory Usage Alert',
                        'description': f"Memory usage is {mem_usage}%, above threshold of {mem_threshold}%",
                        'value': mem_usage,
                        'threshold': mem_threshold,
                        'duration': mem_duration,
                        'status': 'triggered'
                    })
        
        # Vérifier l'alerte disque
        if alerts_config.get('high_disk', {}).get('enabled', False):
            disk_threshold = alerts_config['high_disk'].get('threshold', 85)
            disk_duration = alerts_config['high_disk'].get('duration', 600)
            disk_partitions = alerts_config['high_disk'].get('partitions', ['*'])
            
            if 'disk_collector' in metrics and 'usage' in metrics['disk_collector']:
                for mount_point, usage in metrics['disk_collector']['usage'].items():
                    # Vérifier si cette partition doit être surveillée
                    should_monitor = False
                    if '*' in disk_partitions:
                        should_monitor = True
                    elif mount_point in disk_partitions:
                        should_monitor = True
                    
                    if should_monitor and 'percent' in usage and usage['percent'] >= disk_threshold:
                        alerts.append({
                            'type': 'high_disk_usage',
                            'name': f"Disk Usage Alert: {mount_point}",
                            'description': f"Disk usage on {mount_point} is {usage['percent']}%, above threshold of {disk_threshold}%",
                            'value': usage['percent'],
                            'threshold': disk_threshold,
                            'duration': disk_duration,
                            'status': 'triggered',
                            'mount_point': mount_point
                        })
        
        # Envoyer les alertes
        if alerts:
            self.logger.info(f"Envoi de {len(alerts)} alertes au serveur central...")
            for alert in alerts:
                try:
                    self.api_client.send_alert(alert)
                except Exception as e:
                    self.logger.error(f"Erreur lors de l'envoi de l'alerte {alert['name']}: {e}")
        
        return alerts
    
    def run(self) -> None:
        """
        Exécute l'agent en mode continu
        """
        # Initialiser les signaux pour arrêter proprement l'agent
        self._setup_signals()
        
        self.running = True
        self.logger.info("Démarrage de l'agent en mode continu")
        
        # Intervalle de collecte (en secondes)
        interval = self.config['agent'].get('interval', 60)
        
        # Intervalle de check-in (en secondes, par défaut 5 minutes)
        checkin_interval = self.config['agent'].get('checkin_interval', 300)
        last_checkin = time.time()
        
        # Dernier check de mise à jour
        last_update_check = time.time()
        update_interval = 86400  # 24h par défaut
        if self.updater and self.updater.enabled:
            update_interval = self.updater.interval
        
        try:
            while self.running:
                start_time = time.time()
                
                try:
                    # Collecter et stocker les métriques
                    metrics = self.collect_and_store_metrics()
                    
                    # Vérifier les alertes
                    self.check_and_send_alerts(metrics)
                    
                    # Effectuer un check-in périodique
                    if time.time() - last_checkin >= checkin_interval:
                        self._checkin()
                        last_checkin = time.time()
                    
                    # Vérifier les mises à jour périodiquement
                    if self.updater and self.updater.enabled and time.time() - last_update_check >= update_interval:
                        self.logger.info("Vérification des mises à jour...")
                        if self.updater.check_for_updates():
                            self.logger.info("Redémarrage de l'agent après mise à jour...")
                            self.restart()
                            return
                        last_update_check = time.time()
                    
                except Exception as e:
                    self.logger.error(f"Erreur dans la boucle principale: {e}")
                
                # Attendre jusqu'à la prochaine période de collecte
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                
                if sleep_time > 0:
                    # Dormir par petites tranches pour pouvoir interrompre proprement
                    slices = int(sleep_time / 0.1)
                    for _ in range(slices):
                        if not self.running:
                            break
                        time.sleep(0.1)
                    
                    # Reste du temps
                    remaining = sleep_time - (slices * 0.1)
                    if remaining > 0 and self.running:
                        time.sleep(remaining)
                
        except KeyboardInterrupt:
            self.logger.info("Arrêt de l'agent (interruption clavier)")
            self.running = False
        
        except Exception as e:
            self.logger.error(f"Erreur fatale dans l'agent: {e}")
            self.running = False
        
        finally:
            self.logger.info("Agent arrêté")
    
    def run_once(self) -> Dict[str, Any]:
        """
        Exécute l'agent une seule fois (mode test)
        
        Returns:
            Dict[str, Any]: Métriques collectées
        """
        self.logger.info("Exécution de l'agent en mode test (une seule fois)")
        
        # Collecter et stocker les métriques
        metrics = self.collect_and_store_metrics()
        
        # Vérifier les alertes
        alerts = self.check_and_send_alerts(metrics)
        
        # Afficher l'état du tampon si activé
        if self.metrics_buffer:
            buffer_stats = self.metrics_buffer.get_buffer_stats()
            self.logger.info(f"État du tampon: {buffer_stats['size']}/{buffer_stats['max_size']} entrées ({buffer_stats['usage_percent']:.1f}%)")
        
        # Afficher un récapitulatif
        self.logger.info(f"Collecte des métriques terminée: {len(metrics)} collecteurs exécutés")
        if alerts:
            self.logger.info(f"Alertes déclenchées: {len(alerts)}")
        
        return metrics

    def restart(self):
        """
        Redémarre l'agent après une mise à jour
        """
        self.logger.info("Redémarrage de l'agent...")
        self.running = False
        
        # Attendre que toutes les opérations en cours se terminent
        time.sleep(1)
        
        try:
            # Essayer de trouver le chemin de l'exécutable Python actuel
            python_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            args = sys.argv[1:]
            
            self.logger.info(f"Exécution de: {python_exe} {script_path} {' '.join(args)}")
            
            # Démarrer un nouveau processus
            if os.name == 'nt':  # Windows
                subprocess.Popen([python_exe, script_path] + args)
            else:  # Unix
                os.execl(python_exe, python_exe, script_path, *args)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du redémarrage: {e}")
            raise

    def _load_config(self) -> Dict[str, Any]:
        """
        Charge la configuration de l'agent.
        
        La priorité est:
        1. Variables d'environnement
        2. Paramètres de la ligne de commande
        3. Fichier de configuration local
        
        Puis la configuration est récupérée depuis l'API via le check-in.
        
        Returns:
            Dict[str, Any]: Configuration de l'agent
        """
        # Récupérer les arguments CLI
        args = parse_args()
        
        # Configuration minimale pour l'API uniquement
        local_config = {
            'api': {
                'base_url': '',
                'uuid': '',
                'token': '',
                'timeout': 30
            }
        }
        
        # 1. Charger les variables d'environnement
        env_config = load_env_config()
        if env_config and 'api' in env_config:
            local_config['api'].update(env_config['api'])
            print("Configuration chargée depuis les variables d'environnement")
        
        # 2. Charger la configuration locale (fichier) si elle existe
        config_path = os.path.abspath(self.config_file)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config and 'api' in file_config:
                        print(f"Configuration API chargée depuis {config_path}")
                        local_config['api'].update(file_config['api'])
            except Exception as e:
                print(f"Erreur lors du chargement de la configuration depuis {config_path}: {e}")
        
        # 3. Appliquer les configurations depuis les arguments CLI (priorité sur le fichier et les variables d'environnement)
        if args.api_url:
            local_config['api']['base_url'] = args.api_url
        if args.api_uuid:
            local_config['api']['uuid'] = args.api_uuid
        if args.api_token:
            local_config['api']['token'] = args.api_token
        
        # Vérifier les informations essentielles de l'API
        if not local_config['api']['base_url']:
            print("ERREUR: URL de l'API non configurée")
            print("Veuillez configurer l'URL de l'API via LUMA_API_URL ou dans le fichier de configuration")
            sys.exit(1)
        
        if not local_config['api']['uuid']:
            print("ERREUR: UUID de l'agent non configuré")
            print("Veuillez configurer l'UUID via LUMA_API_UUID ou dans le fichier de configuration")
            sys.exit(1)
        
        if not local_config['api']['token']:
            print("ERREUR: Token d'API non configuré")
            print("Veuillez configurer le token via LUMA_API_TOKEN ou dans le fichier de configuration")
            sys.exit(1)
        
        # Initialiser l'API client avec les informations de base
        self.api_client = ApiClient(
            base_url=local_config['api']['base_url'],
            agent_uuid=local_config['api']['uuid'],
            agent_token=local_config['api']['token'],
            timeout=local_config['api'].get('timeout', 30),
            agent_version=VERSION
        )
        
        # Récupérer la configuration depuis LUMA via check-in
        try:
            print("Récupération de la configuration via check-in LUMA...")
            checkin_response = self.api_client.checkin()
            
            if not checkin_response:
                print("ERREUR: Échec du check-in avec LUMA")
                print("L'agent nécessite une connexion avec le serveur LUMA pour fonctionner.")
                sys.exit(1)
            
            remote_config = checkin_response.get('config', {})
            next_check_in = checkin_response.get('next_check_in', 60)
            
            if not remote_config:
                print("ERREUR: Aucune configuration récupérée depuis LUMA")
                print("L'agent nécessite une configuration distante pour fonctionner.")
                sys.exit(1)
            
            print("Configuration récupérée avec succès depuis LUMA")
            
            # Sauvegarder la configuration récupérée
            saved_config_path = os.path.join(os.path.dirname(config_path), "luma_config.yaml")
            try:
                os.makedirs(os.path.dirname(saved_config_path), exist_ok=True)
                with open(saved_config_path, 'w') as f:
                    yaml.dump(remote_config, f, default_flow_style=False)
                    print(f"Configuration LUMA sauvegardée dans {saved_config_path}")
            except Exception as e:
                print(f"Erreur lors de la sauvegarde de la configuration LUMA: {e}")
            
            # Configuration finale = configuration LUMA + paramètres API locaux
            final_config = remote_config.copy()
            
            # S'assurer que les valeurs API locales sont préservées
            if 'api' not in final_config:
                final_config['api'] = {}
            final_config['api']['base_url'] = local_config['api']['base_url']
            final_config['api']['uuid'] = local_config['api']['uuid']
            final_config['api']['token'] = local_config['api']['token']
            
            # Appliquer certains paramètres de ligne de commande si présents
            if args.log_level:
                if 'agent' not in final_config:
                    final_config['agent'] = {}
                final_config['agent']['log_level'] = args.log_level
            
            if args.log_file:
                if 'agent' not in final_config:
                    final_config['agent'] = {}
                final_config['agent']['log_file'] = args.log_file
            
            if args.interval:
                if 'agent' not in final_config:
                    final_config['agent'] = {}
                final_config['agent']['interval'] = args.interval
            
            # S'assurer que la version est correcte
            if 'agent' in final_config:
                final_config['agent']['version'] = VERSION
                
            # Stocker le prochain check-in
            self.next_check_in = next_check_in
            
            print("Configuration finale préparée avec succès")
            return final_config
            
        except Exception as e:
            print(f"ERREUR lors de la récupération de la configuration depuis LUMA: {e}")
            print("L'agent nécessite une configuration distante pour fonctionner.")
            sys.exit(1)

    def _setup_update_manager(self):
        """
        Configure le gestionnaire de mises à jour automatiques
        """
        update_config = self.config.get('agent', {}).get('auto_update', {})
        # Si la configuration est un booléen, utiliser les valeurs par défaut
        if isinstance(update_config, bool):
            update_enabled = update_config
            update_interval = 86400  # 24h par défaut
            update_url = self.config['api']['base_url'].rstrip('/') + "/updates"
        else:
            update_enabled = update_config.get('enabled', False)
            update_interval = update_config.get('interval', 86400)
            update_url = update_config.get('update_url')
        
        if update_enabled and update_url:
            self.logger.info(f"Configuration de la mise à jour automatique avec l'URL: {update_url}")
            self.updater = Updater(
                enabled=update_enabled,
                interval=update_interval,
                update_url=update_url,
                current_version=self.version,
                agent_uuid=self.config['api']['uuid']
            )
        else:
            self.logger.info("Mise à jour automatique désactivée")
            self.updater = None

    def _setup_metrics_buffer(self):
        """
        Configure le tampon de métriques
        """
        metrics_buffer_config = self.config.get('metrics_buffer', {})
        if not metrics_buffer_config:
            # Configuration par défaut
            metrics_buffer_config = {
                'enabled': True,
                'file_path': 'data/metrics_buffer.json',
                'max_size': 1000,
                'retention_period': 86400,  # 24h
                'flush_interval': 300,  # 5min
                'batch_size': 50
            }
        
        if metrics_buffer_config.get('enabled', True):
            self.logger.info("Initialisation du tampon de métriques...")
            self.metrics_buffer = MetricsBuffer(metrics_buffer_config)
            self.logger.info("Tampon de métriques initialisé")
        else:
            self.logger.info("Tampon de métriques désactivé")
            self.metrics_buffer = None

    def _setup_signals(self) -> None:
        """
        Configurer les gestionnaires de signaux pour l'arrêt gracieux
        """
        # Configurer la gestion du signal pour l'arrêt propre
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        if self.logger:
            self.logger.debug("Gestionnaires de signaux configurés")


def parse_args():
    """
    Parse les arguments de ligne de commande
    
    Returns:
        argparse.Namespace: Arguments parsés
    """
    parser = argparse.ArgumentParser(description="Agent de monitoring système P-2.0.0-Grizzly")
    
    parser.add_argument('-c', '--config', dest='config_file', default='config.yaml',
                        help='Chemin vers le fichier de configuration (défaut: config.yaml)')
    
    parser.add_argument('-t', '--test', action='store_true',
                        help='Mode test: collecte les métriques une seule fois et les affiche')
    
    parser.add_argument('-j', '--json', action='store_true',
                        help='En mode test, affiche les métriques au format JSON')
    
    parser.add_argument('-o', '--output', dest='output_file',
                        help='En mode test, écrit les métriques dans un fichier')
    
    parser.add_argument('--buffer-status', action='store_true',
                        help='Affiche l\'état du tampon de métriques et quitte')
    
    parser.add_argument('--flush-buffer', action='store_true',
                        help='Force l\'envoi des métriques stockées dans le tampon et quitte')
    
    # Arguments pour la configuration par ligne de commande
    config_group = parser.add_argument_group('Configuration par ligne de commande')
    
    config_group.add_argument('--api-url', dest='api_url',
                        help='URL de base de l\'API (ex: https://dev.mhemery.fr/api/monitoring)')
    
    config_group.add_argument('--api-uuid', dest='api_uuid',
                        help='UUID unique de l\'agent')
    
    config_group.add_argument('--api-token', dest='api_token',
                        help='Token d\'authentification pour l\'API (Bearer Token)')
    
    config_group.add_argument('--log-level', dest='log_level', 
                        choices=['debug', 'info', 'warning', 'error'],
                        help='Niveau de log (debug, info, warning, error)')
    
    config_group.add_argument('--log-file', dest='log_file',
                        help='Fichier de log (ex: logs/agent.log)')
    
    config_group.add_argument('--interval', dest='interval', type=int,
                        help='Intervalle de collecte en secondes')
    
    config_group.add_argument('--remote-config', dest='remote_config', 
                        action='store_true', default=None,
                        help='Activer la récupération de configuration depuis LUMA')
    
    config_group.add_argument('--no-remote-config', dest='remote_config', 
                        action='store_false',
                        help='Désactiver la récupération de configuration depuis LUMA')
    
    return parser.parse_args()


def main():
    """
    Point d'entrée principal du programme
    """
    args = parse_args()
    
    # Créer l'agent
    agent = MonitoringAgent(config_file=args.config_file)
    
    agent.setup()
    
    # Actions spéciales
    if args.buffer_status:
        if agent.metrics_buffer:
            stats = agent.metrics_buffer.get_buffer_stats()
            print("\n===== ÉTAT DU TAMPON DE MÉTRIQUES =====\n")
            print(f"Fichier: {stats['file_path']}")
            print(f"Taille: {stats['size']} entrées sur {stats['max_size']} ({stats['usage_percent']:.1f}%)")
            print(f"Dernière mise à jour: {time.ctime(stats['last_update'])}")
            
            # Afficher un échantillon si le tampon n'est pas vide
            if stats['size'] > 0:
                sample = agent.metrics_buffer.get_metrics_to_send(1)
                if sample:
                    print("\nExemple d'entrée:")
                    print(json.dumps(sample[0], indent=2))
        else:
            print("Le tampon de métriques n'est pas activé")
        return
    
    if args.flush_buffer:
        if agent.metrics_buffer:
            if agent.flush_metrics_buffer():
                print("Tampon de métriques vidé avec succès")
            else:
                print("Échec de la vidage du tampon de métriques")
        else:
            print("Le tampon de métriques n'est pas activé")
        return
    
    if args.test:
        # Mode test: exécution unique
        metrics = agent.run_once()
        
        if args.json or args.output_file:
            # Conversion en JSON pour l'affichage ou l'écriture
            metrics_json = json.dumps(metrics, indent=4)
            
            if args.output_file:
                # Écrire dans un fichier
                with open(args.output_file, 'w') as f:
                    f.write(metrics_json)
                print(f"Métriques écrites dans {args.output_file}")
            else:
                # Afficher sur la sortie standard
                print(metrics_json)
        else:
            # Affichage formaté des métriques
            print("\n===== MÉTRIQUES COLLECTÉES =====\n")
            for collector, data in metrics.items():
                if collector == '_alerts':
                    continue
                print(f"== {collector} ==")
                print(json.dumps(data, indent=2))
                print()
            
            # Affichage des alertes
            alerts = metrics.get('_alerts', [])
            if alerts:
                print("\n===== ALERTES DÉTECTÉES =====\n")
                for alert in alerts:
                    print(f"- {alert.get('name')}: {alert.get('description')}")
    else:
        # Mode normal: exécution continue
        agent.run()


if __name__ == "__main__":
    main() 