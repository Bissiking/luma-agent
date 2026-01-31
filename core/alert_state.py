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

# ============================================================
# Core persistence
# ============================================================

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


def save_alert_state(data):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log(f"⚠️ Erreur sauvegarde {STATE_FILE} : {e}")

# ============================================================
# API ÉTAT (pour services.py)
# ============================================================

def is_alert_active(key):
    state = load_alert_state()
    return key in state


def mark_alert_active(key):
    state = load_alert_state()
    state[key] = time.time()
    save_alert_state(state)


def clear_alert(key):
    state = load_alert_state()
    if key in state:
        del state[key]
        save_alert_state(state)

# ============================================================
# API COOLDOWN (pour CPU / RAM / DISK)
# ============================================================

def can_trigger_alert(key, cooldown=600):
    state = load_alert_state()
    now = time.time()
    last = state.get(key, 0)

    if now - last >= cooldown:
        state[key] = now
        save_alert_state(state)
        return True

    return False
