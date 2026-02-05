# ============================================================
# Orion Agent — Docker metrics collection
# Auteur : M. HEMERY
# ============================================================

import subprocess
import json
import time
from core.modules.docker.detect import docker_available


def collect_docker():
    """
    Collecte les informations Docker.
    Retourne None si Docker est indisponible.
    """
    if not docker_available():
        return None

    try:
        # docker ps en JSON ligne par ligne
        output = subprocess.check_output(
            [
                "docker", "ps",
                "--no-trunc",
                "--format",
                "{{json .}}"
            ],
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode().splitlines()

        containers = []
        now = time.time()

        for line in output:
            c = json.loads(line)

            containers.append({
                "id": c.get("ID"),
                "name": c.get("Names"),
                "image": c.get("Image"),
                "status": c.get("Status"),
                "state": "running" if "Up" in c.get("Status", "") else "stopped",
                "ports": c.get("Ports"),
            })

        return {
            "count": len(containers),
            "containers": containers,
            "timestamp": int(now)
        }

    except Exception:
        return None
