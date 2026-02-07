# ============================================================
# Orion Agent — Docker metrics collection
# Auteur : M. HEMERY
# ============================================================

import time
import docker
from core.modules.docker.detect import docker_available


def collect_docker():
    """
    Collecte les informations Docker via l'API (socket).
    Retourne None si Docker est indisponible.
    """
    if not docker_available():
        return None

    try:
        client = docker.DockerClient(base_url="unix://var/run/docker.sock")

        containers = client.containers.list(all=True)
        now = int(time.time())

        data = []

        for c in containers:
            data.append({
                "id": c.id[:12],
                "name": c.name,
                "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                "state": c.status,
                "created": c.attrs.get("Created"),
                "labels": c.labels,
            })

        return {
            "count": len(data),
            "running": sum(1 for c in data if c["state"] == "running"),
            "containers": data,
            "timestamp": now
        }

    except Exception:
        return None
