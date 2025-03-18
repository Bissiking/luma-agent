#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Routes d'API pour l'agent de monitoring LUMA
Centralise toutes les URL d'API utilisées par l'agent
"""

class ApiRoutes:
    """
    Classe contenant toutes les routes d'API pour l'agent de monitoring
    Les routes sont relatives et seront jointes à l'URL de base
    """
    
    # Routes pour les métriques
    METRICS = "agent/{uuid}/metrics"
    METRICS_GLOBAL = "agent/{uuid}/metrics/global"
    
    # Routes pour la configuration
    CONFIGURATION = "agent/{uuid}/configuration"
    CONFIGURATION_BY_ID = "monitoring/agent/{id}/configuration"
    
    # Routes pour les check-ins et la santé
    CHECKIN = "agent/{uuid}/checkin"
    HEALTH = "agent/{uuid}/health"
    
    # Routes pour les alertes
    ALERTS = "agent/{uuid}/alerts"
    
    # Routes pour les mises à jour
    UPDATES = "agent/updates"
    
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