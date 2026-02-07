# ============================================================
# Orion Agent — Docker metrics collection (FULL)
# Auteur : M. HEMERY
# ============================================================

import time
import docker
from core.modules.docker.detect import docker_available


def collect_docker():
    """
    Collecte un maximum d'informations Docker via l'API.
    Snapshot unique, sans stream, safe pour l'agent.
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
            attrs = c.attrs
            state = attrs.get("State", {})
            host = attrs.get("HostConfig", {})
            config = attrs.get("Config", {})
            net = attrs.get("NetworkSettings", {})

            # --- STATS (snapshot, non stream) ---
            cpu_percent = None
            mem_usage = None
            mem_limit = None

            try:
                stats = c.stats(stream=False)

                cpu_delta = (
                    stats["cpu_stats"]["cpu_usage"]["total_usage"]
                    - stats["precpu_stats"]["cpu_usage"]["total_usage"]
                )
                system_delta = (
                    stats["cpu_stats"]["system_cpu_usage"]
                    - stats["precpu_stats"]["system_cpu_usage"]
                )
                if system_delta > 0:
                    cpu_percent = round(
                        (cpu_delta / system_delta)
                        * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
                        * 100,
                        2
                    )

                mem_usage = stats["memory_stats"]["usage"]
                mem_limit = stats["memory_stats"]["limit"]

            except Exception:
                pass  # stats non critiques

            data.append({
                # === IDENTITÉ =====================================
                "id": c.id[:12],
                "name": c.name,
                "image": c.image.tags[0] if c.image.tags else c.image.short_id,

                # === ÉTAT =========================================
                "state": c.status,
                "running": c.status == "running",
                "paused": state.get("Paused"),
                "restarting": state.get("Restarting"),
                "oom_killed": state.get("OOMKilled"),
                "exit_code": state.get("ExitCode"),
                "health": state.get("Health", {}).get("Status"),

                # === TEMPS ========================================
                "created": attrs.get("Created"),
                "started_at": state.get("StartedAt"),
                "finished_at": state.get("FinishedAt"),

                # === RESSOURCES (snapshot) ========================
                "cpu_percent": cpu_percent,
                "memory_usage": mem_usage,
                "memory_limit": mem_limit,

                # === RESTART / RUNTIME ============================
                "restart_policy": host.get("RestartPolicy", {}).get("Name"),
                "restart_count": state.get("RestartCount"),
                "runtime": attrs.get("Path"),
                "args": attrs.get("Args"),

                # === RÉSEAU =======================================
                "networks": {
                    name: {
                        "ip": v.get("IPAddress"),
                        "mac": v.get("MacAddress"),
                        "gateway": v.get("Gateway"),
                    }
                    for name, v in net.get("Networks", {}).items()
                },
                "ports": net.get("Ports"),

                # === VOLUMES ======================================
                "mounts": [
                    {
                        "type": m.get("Type"),
                        "source": m.get("Source"),
                        "target": m.get("Destination"),
                        "rw": m.get("RW"),
                    }
                    for m in attrs.get("Mounts", [])
                ],

                # === CONFIG =======================================
                "env": config.get("Env"),
                "cmd": config.get("Cmd"),
                "entrypoint": config.get("Entrypoint"),
                "working_dir": config.get("WorkingDir"),
                "user": config.get("User"),
                "labels": c.labels,

                # === META =========================================
                "orion_managed": "orion" in c.labels,
            })

        return {
            "count": len(data),
            "running": sum(1 for c in data if c["running"]),
            "containers": data,
            "timestamp": now,
        }

    except Exception:
        return None
