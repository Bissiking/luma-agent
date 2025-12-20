# ============================================================
# Orion Agent — Gestion de la configuration
# Auteur : M. HEMERY
# ============================================================

import os
import json
from dotenv import load_dotenv
from core.logger import log

load_dotenv()

CONFIG_DIR = "config"
IDENTITY_FILE = os.path.join(CONFIG_DIR, "agent_identity.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "agent_config.json")


# ============================================================
# 🌐 Détection automatique de l'URL de base
# ============================================================
def detect_base_url():
    """
    Priorités :
    1. Fichier .orion-env
    2. Variable env LUMA_API_URL
    3. Fallback : https://luma.mhemery.fr
    """
    env_file = os.path.join(os.path.dirname(__file__), "..", ".orion-env")

    # 1️⃣ Fichier .orion-env
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            mode = f.read().strip()

        if mode == "dev":
            return "https://dev.mhemery.fr"
        if mode == "local":
            return "http://localhost:3000"
        if mode == "prod":
            return "https://luma.mhemery.fr"

        if mode.startswith("custom="):
            return mode.replace("custom=", "").strip()

        log(f"[Config] ⚠️ Mode inconnu dans .orion-env : {mode}")

    # 2️⃣ Variable env
    if os.getenv("LUMA_API_URL"):
        return os.getenv("LUMA_API_URL")

    # 3️⃣ Fallback prod
    return "https://luma.mhemery.fr"


# ============================================================
# 📦 Fonction : get_identity()
# ============================================================
def get_identity():
    try:
        if not os.path.exists(IDENTITY_FILE):
            return None
        with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"[Config] ⚠️ Impossible de charger agent_identity.json : {e}")
        return None


# ============================================================
# ⚙️ Fonction : load_config()
# ============================================================
def load_config():
    base_url = detect_base_url().rstrip("/") + "/api/orion/comm"

    defaults = {
        "api": {"base_url": base_url},
        "heartbeat_interval": 60,
        "sync_interval": 600,
    }

    try:
        if not os.path.exists(CONFIG_FILE):
            log("[Config] 📄 Config absente → valeurs par défaut.")
            return defaults

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        merged = defaults.copy()
        merged.update(data)

        # merge propre pour "api"
        if "api" in data:
            merged["api"].update(data["api"])

        return merged

    except Exception as e:
        log(f"[Config] ⚠️ Erreur lecture config : {e}")
        return defaults


# ============================================================
# 🧩 Save config / identity
# ============================================================
def save_identity(data: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log("[Config] 💾 agent_identity.json enregistré.")

def save_config(data: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log("[Config] 💾 agent_config.json enregistré.")
