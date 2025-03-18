#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour gérer les mises à jour automatiques de l'agent
"""

import os
import sys
import logging
import subprocess
import tempfile
import shutil
import time
import json
import requests
from typing import Dict, Any, Optional, Tuple, List, Union
import urllib.request
from urllib.parse import urljoin

from src.utils.system_info import is_running_in_docker

logger = logging.getLogger(__name__)

class Updater:
    """
    Gestionnaire de mises à jour pour l'agent de monitoring
    """
    
    def __init__(self, config: Dict[str, Any], version: str, api_client=None):
        """
        Initialise le gestionnaire de mises à jour
        
        Args:
            config: Configuration de l'agent
            version: Version actuelle de l'agent
            api_client: Client API pour communiquer avec le serveur central
        """
        self.config = config or {}
        self.current_version = version
        self.api_client = api_client
        self.auto_update = self.config.get('auto_update', False)
        self.update_url = self.config.get('update_url', '')
        self.update_interval = self.config.get('update_interval', 86400)  # 24h par défaut
        self.last_check = 0
        self.in_docker = is_running_in_docker()
        
        # Obtenir le chemin de l'exécutable
        if getattr(sys, 'frozen', False):
            # Si l'application est "frozen" (compilée)
            self.executable_path = sys.executable
        else:
            # Sinon, c'est un script Python
            self.executable_path = os.path.abspath(sys.argv[0])
        
        self.executable_dir = os.path.dirname(self.executable_path)
        
        logger.info(f"Gestionnaire de mises à jour initialisé (version actuelle: {self.current_version})")
        if self.in_docker:
            logger.info("Agent exécuté dans un conteneur Docker")
            if self.auto_update:
                logger.warning("Auto-update activé mais l'agent s'exécute dans Docker. Les mises à jour doivent être gérées par l'image Docker.")
    
    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Vérifie si des mises à jour sont disponibles
        
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                - True si une mise à jour est disponible, False sinon
                - Nouvelle version si disponible, None sinon
                - URL de téléchargement si disponible, None sinon
        """
        if not self.auto_update:
            logger.debug("Auto-update désactivé, pas de vérification")
            return False, None, None
        
        if self.in_docker:
            logger.debug("Agent dans Docker, pas de vérification de mise à jour")
            return False, None, None
        
        current_time = time.time()
        if current_time - self.last_check < self.update_interval:
            logger.debug("Dernier check trop récent, pas de vérification")
            return False, None, None
        
        self.last_check = current_time
        
        try:
            # Vérifier les mises à jour via l'API si disponible
            if self.api_client:
                logger.info("Vérification des mises à jour via l'API")
                response = self.api_client._make_request("GET", "/agent/updates", {
                    'current_version': self.current_version
                })
                
                if response.get('update_available', False):
                    new_version = response.get('version')
                    download_url = response.get('download_url')
                    logger.info(f"Mise à jour disponible: {new_version}")
                    return True, new_version, download_url
            
            # Sinon, vérifier via l'URL de mise à jour directe
            elif self.update_url:
                logger.info(f"Vérification des mises à jour via {self.update_url}")
                response = requests.get(
                    urljoin(self.update_url, "latest"),
                    params={'current_version': self.current_version},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('update_available', False):
                        new_version = data.get('version')
                        download_url = data.get('download_url')
                        logger.info(f"Mise à jour disponible: {new_version}")
                        return True, new_version, download_url
            
            logger.info("Aucune mise à jour disponible")
            return False, None, None
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des mises à jour: {e}")
            return False, None, None
    
    def download_update(self, download_url: str) -> Optional[str]:
        """
        Télécharge la mise à jour
        
        Args:
            download_url: URL de téléchargement de la mise à jour
            
        Returns:
            Optional[str]: Chemin vers le fichier téléchargé, None en cas d'erreur
        """
        if not download_url:
            logger.error("URL de téléchargement non spécifiée")
            return None
        
        try:
            logger.info(f"Téléchargement de la mise à jour depuis {download_url}")
            
            # Créer un répertoire temporaire
            temp_dir = tempfile.mkdtemp()
            file_name = os.path.join(temp_dir, "agent_update.zip")
            
            # Télécharger le fichier
            urllib.request.urlretrieve(download_url, file_name)
            
            logger.info(f"Mise à jour téléchargée dans {file_name}")
            return file_name
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de la mise à jour: {e}")
            return None
    
    def apply_update(self, update_file: str) -> bool:
        """
        Applique la mise à jour téléchargée
        
        Args:
            update_file: Chemin vers le fichier de mise à jour
            
        Returns:
            bool: True si la mise à jour a été appliquée avec succès, False sinon
        """
        if not update_file or not os.path.exists(update_file):
            logger.error("Fichier de mise à jour non trouvé")
            return False
        
        try:
            logger.info(f"Application de la mise à jour depuis {update_file}")
            
            # Extraire l'archive dans un répertoire temporaire
            temp_dir = tempfile.mkdtemp()
            shutil.unpack_archive(update_file, temp_dir)
            
            # Script de mise à jour spécifique à la plateforme (Windows/Linux)
            platform_script = None
            if os.name == 'nt':  # Windows
                platform_script = os.path.join(temp_dir, "update.bat")
            else:  # Linux/Unix
                platform_script = os.path.join(temp_dir, "update.sh")
            
            if os.path.exists(platform_script):
                # Si un script de mise à jour spécifique existe, l'exécuter
                logger.info(f"Exécution du script de mise à jour {platform_script}")
                if os.name == 'nt':  # Windows
                    subprocess.Popen([platform_script, self.executable_dir], 
                                    shell=True, close_fds=True)
                else:  # Linux/Unix
                    os.chmod(platform_script, 0o755)  # Rendre le script exécutable
                    subprocess.Popen([platform_script, self.executable_dir], 
                                    shell=False, close_fds=True)
            else:
                # Sinon, essayer une mise à jour simple (remplacer l'exécutable)
                logger.info("Script de mise à jour spécifique non trouvé, tentative de mise à jour simple")
                
                # Trouver le nouvel exécutable
                new_executable = None
                for file in os.listdir(temp_dir):
                    if file.endswith('.exe') or (not file.endswith('.exe') and os.access(os.path.join(temp_dir, file), os.X_OK)):
                        new_executable = os.path.join(temp_dir, file)
                        break
                
                if new_executable:
                    # Renommer l'exécutable actuel en .old
                    old_path = self.executable_path + ".old"
                    if os.path.exists(old_path):
                        os.remove(old_path)
                    os.rename(self.executable_path, old_path)
                    
                    # Copier le nouvel exécutable
                    shutil.copy2(new_executable, self.executable_path)
                    logger.info(f"Mise à jour appliquée. Redémarrage nécessaire.")
                    return True
                else:
                    logger.error("Nouvel exécutable non trouvé dans l'archive de mise à jour")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'application de la mise à jour: {e}")
            return False
        finally:
            # Nettoyage
            try:
                if os.path.exists(update_file):
                    os.remove(update_file)
                if os.path.exists(os.path.dirname(update_file)):
                    shutil.rmtree(os.path.dirname(update_file))
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Erreur lors du nettoyage des fichiers temporaires: {e}")
    
    def check_and_update(self) -> bool:
        """
        Vérifie et applique les mises à jour si disponibles
        
        Returns:
            bool: True si l'agent a été mis à jour, False sinon
        """
        if not self.auto_update:
            return False
        
        if self.in_docker:
            return False
        
        try:
            # Vérifier si des mises à jour sont disponibles
            update_available, new_version, download_url = self.check_for_updates()
            
            if update_available and download_url:
                # Télécharger la mise à jour
                update_file = self.download_update(download_url)
                
                if update_file:
                    # Appliquer la mise à jour
                    if self.apply_update(update_file):
                        logger.info(f"Mise à jour vers la version {new_version} appliquée avec succès")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification et de l'application des mises à jour: {e}")
            return False 