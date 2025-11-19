# ============================================================
# Orion Agent — Synchronisation (Heartbeat / Metrics)
# Auteur : M. HEMERY
# ============================================================

import requests
import socket
import platform
from core.logger import log
from core.config import get_identity, load_config

AGENT_VERSION = "OA-0.2.2-Rigel"  # 🧱 à incrémenter à chaque release Orion Agent

def get_local_ip():
    """Récupère l'adresse IP locale (utilisée pour le reporting Orion)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "0.0.0.0"


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
        "os": platform.system(),           # ex: Windows / Linux / Darwin
        "arch": platform.machine(),        # ex: AMD64 / x86_64 / arm64
        "version": AGENT_VERSION,          # 🆕 version logicielle de l’agent
    }

    try:
        HEADERS = {
            "User-Agent": "LUMA-Orion-Agent/1.0"
        }

        url = cfg["api"]["base_url"].rstrip("/") + "/sync"
        r = requests.post(url, json=payload, headers=HEADERS, timeout=5)

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