# ============================================================
# Orion Agent — Gestion de la configuration
# Auteur : M. HEMERY
# ============================================================

import os
import json
from dotenv import load_dotenv

# Charger automatiquement le .env s'il existe
load_dotenv()

CONFIG_DIR = "config"
IDENTITY_FILE = os.path.join(CONFIG_DIR, "agent_identity.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "agent_config.json")

# ============================================================
# 📦 Fonction : get_identity()
# Récupère l'identité agent (uuid, token, api_key)
# ============================================================
def get_identity():
    """Retourne les infos d'identité de l'agent, ou None si non initialisé."""
    try:
        if not os.path.exists(IDENTITY_FILE):
            return None
        with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Config] ⚠️ Impossible de charger agent_identity.json : {e}")
        return None

# ============================================================
# ⚙️ Fonction : load_config()
# Récupère la configuration générale (API, intervalles)
# ============================================================
def load_config():
    """Charge la config générale. Fournit des valeurs par défaut si absente."""
    defaults = {
        "api": {
            "base_url": os.getenv("LUMA_API_URL", "https://mhemery.fr/api/orion/comm"),
        },
        "heartbeat_interval": 60,
        "sync_interval": 600,
    }

    try:
        if not os.path.exists(CONFIG_FILE):
            print("[Config] 📄 Fichier de config absent, utilisation des valeurs par défaut.")
            return defaults

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Merge config locale + env + defaults
        merged = defaults.copy()
        merged.update(data)
        if "api" in data:
            merged["api"].update(data["api"])
        return merged

    except Exception as e:
        print(f"[Config] ⚠️ Erreur lecture config : {e}")
        return defaults

# ============================================================
# 🧩 Fonction : save_identity() / save_config()
# Sauvegarde auto des fichiers après enrôlement
# ============================================================
def save_identity(data: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("[Config] 💾 agent_identity.json enregistré.")

def save_config(data: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("[Config] 💾 agent_config.json enregistré.")
