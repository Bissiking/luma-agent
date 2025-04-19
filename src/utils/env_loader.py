#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour charger les variables d'environnement pour l'agent LUMA.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_env_config() -> Dict[str, Any]:
    """
    Charge les variables d'environnement pour la configuration de l'agent.
    Essaie d'abord de charger depuis un fichier .env, puis vérifie les variables d'environnement.
    
    Les variables d'environnement supportées sont:
    - LUMA_API_URL: URL de base de l'API
    - LUMA_API_UUID: UUID unique de l'agent
    - LUMA_API_TOKEN: Token d'authentification
    - LUMA_API_TIMEOUT: Timeout pour les requêtes API (optionnel)
    
    Returns:
        Dict[str, Any]: Configuration extraite des variables d'environnement
    """
    try:
        # Essayer de charger un fichier .env
        load_dotenv()
        
        # Configuration de base
        config = {
            'api': {
                'base_url': os.getenv('LUMA_API_URL', ''),
                'uuid': os.getenv('LUMA_API_UUID', ''),
                'token': os.getenv('LUMA_API_TOKEN', ''),
            }
        }
        
        # Timeout optionnel
        api_timeout = os.getenv('LUMA_API_TIMEOUT')
        if api_timeout:
            try:
                config['api']['timeout'] = int(api_timeout)
            except ValueError:
                logger.warning(f"Timeout API '{api_timeout}' non valide, utilisation de la valeur par défaut")
        
        # Paramètres optionnels de l'agent
        log_level = os.getenv('LUMA_LOG_LEVEL')
        if log_level:
            if 'agent' not in config:
                config['agent'] = {}
            config['agent']['log_level'] = log_level
            
        log_file = os.getenv('LUMA_LOG_FILE')
        if log_file:
            if 'agent' not in config:
                config['agent'] = {}
            config['agent']['log_file'] = log_file
            
        interval = os.getenv('LUMA_INTERVAL')
        if interval:
            try:
                if 'agent' not in config:
                    config['agent'] = {}
                config['agent']['interval'] = int(interval)
            except ValueError:
                logger.warning(f"Intervalle '{interval}' non valide, utilisation de la valeur par défaut")
        
        # Journaliser les informations de configuration (sans le token pour des raisons de sécurité)
        logger.debug(f"Configuration chargée depuis les variables d'environnement:")
        logger.debug(f"  API URL: {config['api']['base_url']}")
        logger.debug(f"  UUID: {config['api']['uuid']}")
        logger.debug(f"  Token: {'*' * 8 if config['api']['token'] else 'Non configuré'}")
        
        return config
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement des variables d'environnement: {e}")
        return {'api': {'base_url': '', 'uuid': '', 'token': ''}} 