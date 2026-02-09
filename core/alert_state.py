# ============================================================
# Orion Agent — Suivi local des alertes actives
# Auteur : M. HEMERY
# ============================================================

import json
import os
import time
from core.logger import log

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "active_alerts.json")
os.makedirs(DATA_DIR, exist_ok=True)


def load_alert_state():
    if not os.path.exists(STATE_FILE):
        save_alert_state({})
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"⚠️ Erreur lecture {STATE_FILE} : {e}")
        return {}


def save_alert_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"⚠️ Erreur sauvegarde {STATE_FILE} : {e}")


# ============================================================
# API ALERTES (BACKWARD FRIENDLY)
# ============================================================

def can_trigger_alert(key, severity="warning", cooldown=600):
    """
    Retourne True si :
    - alerte jamais envoyée
    - changement de sévérité
    - même sévérité mais cooldown dépassé
    """
    state = load_alert_state()
    now = time.time()

    entry = state.get(key)

    if not entry:
        state[key] = {
            "severity": severity,
            "last_sent": now
        }
        save_alert_state(state)
        return True

    if entry["severity"] != severity:
        entry["severity"] = severity
        entry["last_sent"] = now
        save_alert_state(state)
        return True

    if now - entry["last_sent"] >= cooldown:
        entry["last_sent"] = now
        save_alert_state(state)
        return True

    return False


def clear_alert(key):
    state = load_alert_state()
    if key in state:
        del state[key]
        save_alert_state(state)

def is_alert_active(key):
    """
    Retourne True si une alerte est actuellement active (quelque soit la sévérité)
    """
    state = load_alert_state()
    return key in state

def mark_alert_active(key, severity="warning"):
    """
    Compatibilité legacy.
    Marque une alerte comme active sans logique de cooldown.
    """
    state = load_alert_state()
    state[key] = {
        "severity": severity,
        "last_sent": time.time()
    }
    save_alert_state(state)
