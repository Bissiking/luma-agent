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
from core.services_collect import collect_services


# ============================================================
# 🔌 Helper — Injection de modules optionnels
# ============================================================

def inject_module(metrics: dict, name: str, fn):
    log(f"🔌 Tentative injection module : {name}")

    try:
        data = fn()

        if data is None:
            log(f"⚠️ Module {name} n’a retourné aucune donnée")
            return

        metrics[name] = data
        log(f"✅ Module {name} injecté avec succès")

    except Exception as e:
        log(f"❌ Module {name} indisponible : {e}")

# ============================================================
# 🌐 Réseau CORE — Interfaces & trafic
# ============================================================

def collect_network_core():
    import socket

    interfaces = []

    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for name, addr_list in addrs.items():
        stat = stats.get(name)
        if not stat or not stat.isup:
            continue

        ip = None
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                ip = addr.address
                break

        if not ip:
            continue

        iface_type = (
            "loopback" if name.lower().startswith("lo")
            else "wifi" if name.lower().startswith(("wl", "wi"))
            else "ethernet"
        )

        interfaces.append({
            "name": name,
            "type": iface_type,
            "ip": ip
        })

    io = psutil.net_io_counters(pernic=False)

    return {
        "interfaces": interfaces,
        "traffic": {
            "in": io.bytes_recv,
            "out": io.bytes_sent
        }
    }


# ============================================================
# 📊 Collecte principale
# ============================================================

def collect_metrics():
    """
    Collecte les métriques système principales.
    Retourne un dictionnaire complet pour /sync.
    Déclenche aussi les alertes si les seuils sont dépassés.
    """
    cfg = load_config()
    modules = cfg.get("modules", {})

    # === 🧩 Données CORE ===
    hostname = platform.node()
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    uptime = time.time() - psutil.boot_time()
    # === 🌐 Réseau (CORE) ===
    network = collect_network_core()
    
    # === 💽 Disques multiples (CORE) ===
    disks = []
    ghosted = cfg.get("ghosted_disks", [])

    for part in psutil.disk_partitions(all=False):
        if any(g.lower() in part.mountpoint.lower() for g in ghosted):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "mount": part.mountpoint,
                "fstype": part.fstype,
                "total": round(usage.total / (1024 ** 3), 1),
                "used": round(usage.used / (1024 ** 3), 1),
                "free": round(usage.free / (1024 ** 3), 1),
                "percent": usage.percent
            })
        except PermissionError:
            continue

    # === 🧩 Services système (CORE) ===
    try:
        services = collect_services()
    except Exception as e:
        log(f"⚠️ Erreur collecte services : {e}")
        services = {}

    # === ⚙️ Structure CORE ===
    metrics = {
        "hostname": hostname,
        "cpu": cpu,
        "ram": ram,
        "disks": disks,
        "uptime": uptime,
        "services": services,
        "network": network,
    }

    # ========================================================
    # 🔌 MODULES OPTIONNELS
    # ========================================================

    # 🐳 Docker
    if modules.get("docker"):
        log("🐳 Vérification Docker…")
        from core.modules.docker.detect import docker_available

        if not docker_available():
            log("⚠️ Docker non disponible (binaire ou socket)")
        else:
            log("🐳 Docker disponible")

            try:
                from core.modules.docker.collect import collect_docker
                inject_module(metrics, "docker", collect_docker)
                log("🐳 Module docker injecté")
            except Exception as e:
                log(f"⚠️ Module docker KO : {e}")

    # 🖥️ GPU
    if modules.get("gpu"):
        try:
            from core.modules.gpu.collect import collect_gpu
            inject_module(metrics, "gpu", collect_gpu)
        except Exception as e:
            log(f"⚠️ Module gpu non chargé : {e}")

    # 🧠 Proxmox
    if modules.get("proxmox"):
        try:
            from core.modules.proxmox.collect import collect_proxmox
            inject_module(metrics, "proxmox", collect_proxmox)
        except Exception as e:
            log(f"⚠️ Module proxmox non chargé : {e}")

    # ========================================================
    # 🚨 Alertes CORE
    # ========================================================
    try:
        check_thresholds(cpu, ram, disks, cfg)
    except Exception as e:
        log(f"⚠️ Erreur vérification des seuils : {e}")

    return metrics


# ============================================================
# 🚨 Seuils & alertes CORE
# ============================================================

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
                    sev,
                    "disk",
                    f"Disque {d['mount']} saturé ({d['percent']}%)",
                    {"mount": d["mount"], "value": d["percent"]}
                )
        else:
            clear_alert(key)
