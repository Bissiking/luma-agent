# ============================================================
# Orion Agent — Synchronisation (Heartbeat / Metrics)
# Auteur : M. HEMERY
# ============================================================

import requests
import socket
import platform
from core.logger import log
from core.config import get_identity, load_config

AGENT_VERSION = "OA-0.4.0-Rigel"  # 🧱 à incrémenter à chaque release Orion Agent
_OS_NAME = None


def get_local_ip():
    """Récupère l'adresse IP locale (utilisée pour le reporting Orion)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "0.0.0.0"
    finally:
        s.close()


def get_linux_distro():
    try:
        with open("/etc/os-release", "r") as f:
            data = {}
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    data[k] = v.strip('"')
            return data.get("PRETTY_NAME") or data.get("NAME", "Linux")
    except Exception:
        return "Linux (unknown)"

def get_os_name():
    global _OS_NAME

    if _OS_NAME:
        return _OS_NAME

    os_name = platform.system()
    if os_name == "Linux":
        os_name = get_linux_distro()

    _OS_NAME = os_name
    return os_name


def sync_with_luma(metrics=None):
    ident = get_identity()
    cfg = load_config()

    if not ident:
        log("❌ Aucune identité trouvée — agent non enregistré.")
        return False

    payload = {
        "uuid": ident["uuid"],
        "token": ident["token"],
        "metrics": metrics or {},
        "ip": get_local_ip(),
        "os": get_os_name(),             # ✅ source unique
        "arch": platform.machine(),      # x86_64 / arm64
        "version": AGENT_VERSION,
    }

    try:
        headers = {
            "User-Agent": "LUMA-Orion-Agent/1.0"
        }

        url = cfg["api"]["base_url"].rstrip("/") + "/sync"
        r = requests.post(url, json=payload, headers=headers, timeout=5)

        if r.status_code == 200:
            log(f"✅ Sync OK depuis {payload['ip']} — Agent v{AGENT_VERSION}")
            return True
        elif r.status_code == 403:
            log("⛔ Authentification échouée (token invalide).")
        else:
            log(f"⚠️ Erreur de synchronisation : {r.status_code}")
        return False

    except Exception as e:
        log(f"❌ Erreur réseau pendant sync : {e}")
        return False
