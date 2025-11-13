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

# --- S'assure que le dossier data existe ---
os.makedirs(DATA_DIR, exist_ok=True)

def load_alert_state():
    """Charge le cache des alertes actives, crée le fichier si manquant."""
    if not os.path.exists(STATE_FILE):
        # Si le fichier n'existe pas, on crée un JSON vide
        save_alert_state({})
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"⚠️ Erreur lecture {STATE_FILE} : {e}")
        return {}


def save_alert_state(data):
    """Sauvegarde l’état local des alertes dans data/active_alerts.json"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log(f"⚠️ Erreur sauvegarde {STATE_FILE} : {e}")


def can_trigger_alert(key, cooldown=600):
    """
    Vérifie si une alerte peut être renvoyée (cooldown par défaut : 10 min)
    key = "cpu", "ram", "disk:C", etc.
    """
    state = load_alert_state()
    now = time.time()
    last = state.get(key, 0)

    if now - last >= cooldown:
        state[key] = now
        save_alert_state(state)
        return True
    return False


def clear_alert(key):
    """Supprime une alerte du cache (quand résolue)."""
    state = load_alert_state()
    if key in state:
        del state[key]
        save_alert_state(state)
