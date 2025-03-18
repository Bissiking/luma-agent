#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilitaires pour obtenir des informations système
"""

import os
import logging
import subprocess
from typing import Dict, Any, Optional, List, Tuple, Union

logger = logging.getLogger(__name__)

def is_running_in_docker() -> bool:
    """
    Détecte si l'agent s'exécute dans un conteneur Docker
    
    Returns:
        bool: True si l'agent s'exécute dans un conteneur Docker, False sinon
    """
    # Méthode 1: Vérifier l'existence de /.dockerenv
    if os.path.exists('/.dockerenv'):
        logger.debug("Docker détecté: fichier /.dockerenv trouvé")
        return True
    
    # Méthode 2: Vérifier les cgroups
    try:
        with open('/proc/1/cgroup', 'r') as f:
            content = f.read()
            if 'docker' in content or 'kubepods' in content:
                logger.debug("Docker détecté: cgroups contient docker/kubepods")
                return True
    except (IOError, FileNotFoundError):
        pass
    
    # Méthode 3: Vérifier via /proc/self/mountinfo
    try:
        with open('/proc/self/mountinfo', 'r') as f:
            content = f.read()
            if '/docker/' in content:
                logger.debug("Docker détecté: mountinfo contient /docker/")
                return True
    except (IOError, FileNotFoundError):
        pass
    
    # Méthode 4: Vérifier les limites dans /sys/fs/cgroup
    try:
        with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
            limit = int(f.read().strip())
            # Si la limite mémoire est différente de la valeur par défaut 
            # (qui est très grande pour les systèmes non-conteneurisés)
            if limit < 9223372036854771712:  # Valeur inférieure à la valeur par défaut
                logger.debug("Docker probable: limite mémoire définie")
                return True
    except (IOError, FileNotFoundError, ValueError):
        pass
    
    logger.debug("Docker non détecté")
    return False

def get_system_details() -> Dict[str, Any]:
    """
    Obtient des détails système supplémentaires
    
    Returns:
        Dict[str, Any]: Détails système
    """
    details = {
        "in_docker": is_running_in_docker()
    }
    
    return details 