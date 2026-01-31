# ============================================================
# Orion Agent — Collecte des services système
# Auteur : M. HEMERY
# ============================================================

import psutil
import platform
import time
from collections import defaultdict

IGNORE = {
    "systemd", "kthreadd", "rcu_sched",
    "svchost.exe", "idle", "init"
}

MIN_UPTIME = 60  # secondes

def collect_services():
    system = platform.system().lower()

    if system == "linux":
        svc_type = "systemd"
    elif system == "windows":
        svc_type = "windows"
    elif system == "darwin":
        svc_type = "launchd"
    else:
        svc_type = "unknown"

    services = []
    groups = defaultdict(lambda: {
        "count": 0,
        "pids": [],
        "max_uptime": 0
    })

    now = time.time()

    for proc in psutil.process_iter(attrs=["pid", "name", "create_time"]):
        try:
            name = proc.info["name"]
            if not name:
                continue

            lname = name.lower()
            if lname in IGNORE:
                continue

            uptime = now - proc.info["create_time"]
            if uptime < MIN_UPTIME:
                continue

            uptime = int(uptime)
            pid = proc.info["pid"]

            services.append({
                "name": name,
                "pid": pid,
                "uptime": uptime,
                "status": "running"
            })

            g = groups[name]
            g["count"] += 1
            g["pids"].append(pid)
            g["max_uptime"] = max(g["max_uptime"], uptime)

        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue

    return {
        "type": svc_type,
        "services": services,
        "groups": dict(groups)
    }
