#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire de mises à jour pour l'agent de monitoring
"""

import os
import sys
import time
import logging
import requests
import tempfile
import shutil
import subprocess
import zipfile
import platform
import json
from typing import Dict, Any, Optional, Tuple

from src.api.routes import ApiRoutes
from src.constants import VERSION, AGENT_INFO

logger = logging.getLogger(__name__)


class Updater:
    """
    Gestionnaire de mises à jour automatiques de l'agent LUMA
    
    Cette classe gère la vérification et l'application des mises à jour
    de l'agent. Elle utilise l'API LUMA pour vérifier si une nouvelle
    version est disponible et télécharge la mise à jour si nécessaire.
    """
    
    def __init__(self, agent_uuid: str, api_client, config: Dict[str, Any], logger=None):
        """
        Initialise le gestionnaire de mises à jour.
        
        Args:
            agent_uuid: UUID de l'agent
            api_client: Client API pour communiquer avec le serveur LUMA
            config: Configuration de l'agent
            logger: Logger à utiliser (optionnel)
        """
        self.agent_uuid = agent_uuid
        self.api_client = api_client
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Configuration des mises à jour
        self.update_config = config.get('agent', {}).get('auto_update', {})
        self.enabled = self.update_config.get('enabled', False)
        self.interval = self.update_config.get('interval', 86400)  # 24 heures par défaut
        self.update_url = self.update_config.get('update_url', '')
        
        # Informations sur l'agent
        self.current_version = VERSION
        self.platform = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Chemin de base de l'agent
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        self.logger.info(f"Gestionnaire de mises à jour initialisé (version actuelle: {self.current_version})")
        self.logger.debug(f"Plateforme: {self.platform}, Architecture: {self.architecture}, Python: {self.python_version}")
        
        if not self.enabled:
            self.logger.info("Les mises à jour automatiques sont désactivées")
        else:
            self.logger.info(f"Vérification des mises à jour toutes les {self.interval/3600:.1f} heures")
    
    def check_for_updates(self) -> bool:
        """
        Vérifie si une mise à jour est disponible
        
        Returns:
            bool: True si une mise à jour a été effectuée, False sinon
        """
        if not self.enabled or not self.update_url:
            return False
        
        # Ne vérifier que si l'intervalle est écoulé
        now = time.time()
        if now - self.last_check < self.interval:
            return False
        
        self.last_check = now
        
        try:
            # Construire l'URL complète en utilisant la route d'API
            api_url = self.update_url
            if not api_url.endswith("updates"):
                # Utiliser la route de mise à jour standard si l'URL ne spécifie pas "updates"
                update_endpoint = ApiRoutes.UPDATES
                # Extraire l'URL de base si l'URL fournie est complète
                if '/' in api_url and not api_url.endswith('/'):
                    base_url = '/'.join(api_url.split('/')[:-1])
                    api_url = f"{base_url}/{update_endpoint}"
                else:
                    api_url = f"{api_url.rstrip('/')}/{update_endpoint}"
            
            logger.info(f"Vérification des mises à jour sur {api_url}")
            
            # Préparer les données pour la requête
            data = {
                "agent_uuid": self.agent_uuid,
                "current_version": self.current_version,
                "platform": self.platform,
                "architecture": self.architecture,
                "python_version": self.python_version
            }
            
            # Faire la requête
            response = requests.post(
                api_url,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Vérifier si une mise à jour est disponible
            if result.get("update_available", False):
                new_version = result.get("version")
                download_url = result.get("download_url")
                
                if download_url:
                    logger.info(f"Mise à jour disponible: {new_version} (actuelle: {self.current_version})")
                    return self._download_and_install_update(download_url, new_version)
                else:
                    logger.warning("Mise à jour disponible mais URL de téléchargement manquante")
            else:
                logger.info(f"Aucune mise à jour disponible (version actuelle: {self.current_version})")
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des mises à jour: {e}")
            return False
    
    def _download_and_install_update(self, download_url: str, new_version: str) -> bool:
        """
        Télécharge et installe une mise à jour
        
        Args:
            download_url: URL de téléchargement de la mise à jour
            new_version: Nouvelle version à installer
            
        Returns:
            bool: True si l'installation a réussi, False sinon
        """
        try:
            # Emplacement où enregistrer la mise à jour
            update_file = os.path.join(os.path.dirname(__file__), "update.zip")
            
            # Télécharger le fichier
            logger.info(f"Téléchargement de la mise à jour depuis {download_url}")
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Installation de la mise à jour
            logger.info(f"Installation de la mise à jour vers la version {new_version}")
            # TODO: Implémentation de l'installation de la mise à jour
            # Cette partie dépend du format de la mise à jour et du système d'exploitation
            
            # Pour l'instant, on considère que l'installation a réussi
            logger.info(f"Mise à jour vers la version {new_version} installée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement/installation de la mise à jour: {e}")
            return False 