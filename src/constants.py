#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module contenant les constantes globales pour l'agent LUMA.
Centralise les paramètres qui peuvent changer entre les versions.
"""

# Version actuelle de l'agent
VERSION = "P-2.0.0-Grizzly"

# Configuration par défaut complète pour référence et utilisation dans l'API
DEFAULT_CONFIG = {
    'agent': {
        'version': VERSION,
        'log_level': 'info',
        'log_file': 'logs/agent.log',
        'interval': 60,
        'auto_update': {
            'enabled': True,
            'interval': 86400,  # 24h
            'update_url': ''
        }
    },
    'metrics_buffer': {
        'enabled': True,
        'file_path': 'data/metrics_buffer.json',
        'max_size': 1000,
        'retention_period': 86400,  # 24h
        'flush_interval': 300,  # 5min
        'batch_size': 50
    },
    'api': {
        'base_url': '',
        'uuid': '',
        'token': '',
        'timeout': 30
    },
    'collectors': {
        'cpu': {
            'enabled': True,
            'interval': 60
        },
        'memory': {
            'enabled': True,
            'interval': 60
        },
        'disk': {
            'enabled': True,
            'interval': 300,
            'partitions': ['*']
        },
        'network': {
            'enabled': True,
            'interval': 60,
            'interfaces': ['*']
        },
        'docker': {
            'enabled': True,
            'interval': 300,
            'containers': ['*']
        },
        'service': {
            'enabled': True,
            'interval': 300,
            'services': ['*'],
            'max_services': 50,
            'priority_services': [],
            'excludes': []
        },
        'web_service': {
            'enabled': False,
            'interval': 300,
            'services': [
                # exemple de service à surveiller
                # {
                #     'name': 'API Example',
                #     'url': 'https://example.com/api/health',
                #     'method': 'GET',
                #     'headers': {'Content-Type': 'application/json'},
                #     'timeout': 10,
                #     'expected_status': 200,
                #     'expected_content': 'ok'
                # }
            ]
        }
    },
    'alerts': {
        'cpu': {
            'enabled': True,
            'warning': 70,  # pourcentage
            'critical': 90,  # pourcentage
            'duration': 300,  # 5 minutes
            'recovery_threshold': 60,  # pourcentage
            'cooldown': 3600  # 1 heure
        },
        'memory': {
            'enabled': True,
            'warning': 75,  # pourcentage
            'critical': 85,  # pourcentage
            'duration': 300,  # 5 minutes
            'recovery_threshold': 65,  # pourcentage
            'cooldown': 3600  # 1 heure
        },
        'disk': {
            'enabled': True,
            'warning': 80,  # pourcentage
            'critical': 90,  # pourcentage
            'duration': 600,  # 10 minutes
            'partitions': ['*'],
            'recovery_threshold': 70,  # pourcentage
            'cooldown': 7200  # 2 heures
        },
        'services': {
            'enabled': True,
            'consecutive_failures': 3,
            'cooldown': 1800,  # 30 minutes
            'services': ["mysql", "apache2", "nginx"]
        }
    }
}

# Endpoints d'API requis pour la configuration
REQUIRED_API_INFO = {
    'base_url': '',
    'uuid': '',
    'token': '',
    'timeout': 30
}

# Informations sur l'agent
AGENT_INFO = {
    "name": "LUMA Monitoring Agent",
    "version": VERSION,
    "build_date": "2023-05-15",
    "protocol_version": "1.0",
    "update_channel": "stable",
    "min_python_version": "3.6.0"
}

# URLs d'API nécessaires à l'agent mais non définies dans routes.py
API_ENDPOINTS = {
    "config_example": "/docs/agent/config/example"
} 