# ============================================================
# Orion Agent — Collecte et supervision des métriques système
# Auteur : M. HEMERY
# ============================================================

import psutil
import platform
import time
from core.config import load_config
from core.alerts import push_alert
from core.logger import log
from core.alert_state import can_trigger_alert, clear_alert

def collect_metrics():
    """
    Collecte les métriques système principales.
    Retourne un dictionnaire complet pour /sync.
    Déclenche aussi les alertes si les seuils sont dépassés.
    """
    cfg = load_config()

    # === 🧩 Données de base ===
    hostname = platform.node()
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    uptime = time.time() - psutil.boot_time()

    # === 💽 Disques multiples ===
    disks = []
    ghosted = cfg.get("ghosted_disks", [])  # disques ignorés
    for part in psutil.disk_partitions(all=False):
        if any(g.lower() in part.mountpoint.lower() for g in ghosted):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "mount": part.mountpoint,
                "fstype": part.fstype,
                "total": round(usage.total / (1024**3), 1),
                "used": round(usage.used / (1024**3), 1),
                "free": round(usage.free / (1024**3), 1),
                "percent": usage.percent
            })
        except PermissionError:
            continue

    # === ⚙️ Structure finale ===
    metrics = {
        "hostname": hostname,
        "cpu": cpu,
        "ram": ram,
        "disks": disks,
        "uptime": uptime,
    }

    # === 🚨 Gestion des alertes ===
    try:
        check_thresholds(cpu, ram, disks, cfg)
    except Exception as e:
        log(f"⚠️ Erreur vérification des seuils : {e}")

    return metrics


def check_thresholds(cpu, ram, disks, cfg):
    cpu_th = cfg.get("cpu_threshold", 85)
    ram_th = cfg.get("ram_threshold", 85)
    disk_th = cfg.get("disk_threshold", 90)

    # CPU
    if cpu >= cpu_th:
        sev = "critical" if cpu >= cpu_th + 10 else "warning"
        if can_trigger_alert("cpu"):
            push_alert(sev, "cpu", f"CPU élevé ({cpu:.1f}%)", {"value": cpu})
    else:
        clear_alert("cpu")

    # RAM
    if ram >= ram_th:
        sev = "critical" if ram >= ram_th + 10 else "warning"
        if can_trigger_alert("ram"):
            push_alert(sev, "ram", f"RAM élevée ({ram:.1f}%)", {"value": ram})
    else:
        clear_alert("ram")

    # DISK
    for d in disks:
        key = f"disk:{d['mount']}"
        if d["percent"] >= disk_th:
            sev = "critical" if d["percent"] >= disk_th + 5 else "warning"
            if can_trigger_alert(key):
                push_alert(
                    sev, "disk",
                    f"Disque {d['mount']} saturé ({d['percent']}%)",
                    {"mount": d["mount"], "value": d["percent"]}
                )
        else:
            clear_alert(key)