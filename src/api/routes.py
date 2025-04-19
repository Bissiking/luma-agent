#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Routes d'API pour l'agent de monitoring LUMA
Centralise toutes les URL d'API utilisées par l'agent
"""

class ApiRoutes:
    """
    Centralisation des routes API utilisées par l'agent LUMA.
    
    Cette classe contient toutes les routes API nécessaires pour communiquer avec
    le serveur LUMA. Les routes utilisent des placeholders {uuid} et {id} qui sont
    remplacés par les valeurs réelles lors de l'appel.
    """
    
    # Routes basiques
    ROOT = ""
    BASE = "agent"
    
    # Routes pour l'agent
    AGENT = "/api/v1/agents/{uuid}"
    CHECKIN = "/api/v1/agents/{uuid}/checkin"
    CONFIG = "/api/v1/agent/configuration/{uuid}"
    CONFIG_EXAMPLE = "/api/v1/agents/configuration/example"
    
    # Routes pour les métriques
    METRICS = "/api/v1/monitoring/metrics"
    METRICS_GLOBAL = "/api/v1/agents/{uuid}/metrics/global"
    METRICS_BATCH = "/api/v1/monitoring/metrics/batch"
    
    # Routes pour les alertes
    ALERTS = "/api/v1/monitoring/alerts"
    ALERTS_STATUS = "/api/v1/agents/{uuid}/alerts/status"
    
    # Routes pour les mises à jour
    UPDATES = "/api/v1/agents/{uuid}/updates"
    UPDATE_STATUS = "/api/v1/agents/{uuid}/updates/status"
    UPDATE_DOWNLOAD = "/api/v1/agents/{uuid}/updates/download"
    
    # Routes pour les commandes
    COMMANDS = "/api/v1/agents/{uuid}/commands"
    COMMAND_STATUS = "/api/v1/agents/{uuid}/commands/{id}/status"
    COMMAND_RESULT = "/api/v1/agents/{uuid}/commands/{id}/result"
    
    # Routes pour les fichiers
    FILES = "/api/v1/agents/{uuid}/files"
    FILE_DOWNLOAD = "/api/v1/agents/{uuid}/files/{id}/download"
    FILE_UPLOAD = "/api/v1/agents/{uuid}/files/upload"
    
    # Routes pour la santé de l'agent
    HEALTH = "/api/v1/monitoring/agents/{uuid}/health"
    
    # Routes pour les informations système
    SYSTEM_INFO = "/api/v1/monitoring/agents/{uuid}/system"
    
    @staticmethod
    def get_all_routes() -> dict:
        """
        Retourne toutes les routes disponibles pour documentation.
        
        Returns:
            dict: Dictionnaire des routes disponibles
        """
        return {name: value for name, value in vars(ApiRoutes).items() 
                if not name.startswith('_') and isinstance(value, str)}

    @staticmethod
    def get_full_route(base_url: str, route: str, **params) -> str:
        """
        Construit une URL complète en joignant la route à l'URL de base
        et en remplaçant les paramètres dans la route
        
        Args:
            base_url: URL de base de l'API (ex: https://api.example.com/api)
            route: Route relative (ex: agent/{uuid}/metrics)
            **params: Paramètres à remplacer dans la route (ex: uuid="123")
            
        Returns:
            str: URL complète
        """
        # S'assurer que l'URL de base ne se termine pas par un slash
        base_url = base_url.rstrip('/')
        
        # Remplacer les paramètres dans la route
        for param, value in params.items():
            route = route.replace(f"{{{param}}}", str(value))
        
        # Joindre l'URL de base et la route
        return f"{base_url}/{route}" 