# ============================================================
# Orion Agent — Docker detection
# Auteur : M. HEMERY
# ============================================================

import os

def docker_available():
    """
    Docker est considéré disponible si le socket Docker est présent.
    Compatible host + container.
    """
    return os.path.exists("/var/run/docker.sock")
