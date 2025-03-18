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
    AGENT = "api/agent/{uuid}"
    CHECKIN = "api/agent/{uuid}/checkin"
    CONFIG = "api/agent/{uuid}/configuration"
    
    # Routes pour les métriques
    METRICS = "api/agent/{uuid}/metrics"
    METRICS_GLOBAL = "api/agent/{uuid}/metrics/global"
    
    # Routes pour les alertes
    ALERTS = "agent/{uuid}/alerts"
    ALERTS_STATUS = "agent/{uuid}/alerts/status"
    
    # Routes pour les mises à jour
    UPDATES = "api/agent/{uuid}/updates"
    UPDATE_STATUS = "api/agent/{uuid}/updates/status"
    UPDATE_DOWNLOAD = "api/agent/{uuid}/updates/download"
    
    # Routes pour les commandes
    COMMANDS = "api/agent/{uuid}/commands"
    COMMAND_STATUS = "api/agent/{uuid}/commands/{id}/status"
    COMMAND_RESULT = "api/agent/{uuid}/commands/{id}/result"
    
    # Routes pour les fichiers
    FILES = "api/agent/{uuid}/files"
    FILE_DOWNLOAD = "api/agent/{uuid}/files/{id}/download"
    FILE_UPLOAD = "api/agent/{uuid}/files/upload"
    
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