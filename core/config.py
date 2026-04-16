import copy
import json
import os

from dotenv import load_dotenv

from core.logger import log

load_dotenv()

CONFIG_DIR = "config"
IDENTITY_FILE = os.path.join(CONFIG_DIR, "agent_identity.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "agent_config.json")
INSTALL_INFO_FILE = os.path.join(CONFIG_DIR, "install_info.json")

_CONFIG_CACHE = None
_CONFIG_MTIME = None


def detect_base_url():
    """
    Priorites :
    1. Fichier .orion-env
    2. Variable env LUMA_API_URL
    3. Fallback : https://luma.mhemery.fr
    """
    env_file = os.path.join(os.path.dirname(__file__), "..", ".orion-env")

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

        log(f"[Config] Mode inconnu dans .orion-env : {mode}")

    if os.getenv("LUMA_API_URL"):
        return os.getenv("LUMA_API_URL")

    return "https://luma.mhemery.fr"


def get_default_config():
    base_url = detect_base_url().rstrip("/") + "/api/orion/comm"
    return {
        "api": {
            "base_url": base_url,
            "timeout": 5,
        },
        "heartbeat_interval": 60,
        "sync_interval": 600,
        "config_check_interval": 900,
        "modules": {
            "docker": False,
            "gpu": False,
            "proxmox": False,
            "minecraft": {
                "enabled": False,
                "timeout": 3.0,
                "servers": [],
            },
        },
        "services_watch": [],
        "ghosted_disks": [],
    }


def _deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def get_identity():
    try:
        if not os.path.exists(IDENTITY_FILE):
            return None
        with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"[Config] Impossible de charger agent_identity.json : {e}")
        return None


def load_config():
    global _CONFIG_CACHE, _CONFIG_MTIME

    defaults = get_default_config()

    try:
        if not os.path.exists(CONFIG_FILE):
            if _CONFIG_CACHE is None:
                log("[Config] Config absente -> valeurs par defaut.")
            _CONFIG_CACHE = defaults
            _CONFIG_MTIME = None
            return copy.deepcopy(_CONFIG_CACHE)

        current_mtime = os.path.getmtime(CONFIG_FILE)
        if _CONFIG_CACHE is not None and _CONFIG_MTIME == current_mtime:
            return copy.deepcopy(_CONFIG_CACHE)

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        _CONFIG_CACHE = _deep_merge(defaults, data)
        _CONFIG_MTIME = current_mtime
        return copy.deepcopy(_CONFIG_CACHE)

    except Exception as e:
        log(f"[Config] Erreur lecture config : {e}")
        return defaults


def save_identity(data: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log("[Config] agent_identity.json enregistre.")


def save_config(data: dict):
    global _CONFIG_CACHE, _CONFIG_MTIME

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    _CONFIG_CACHE = None
    _CONFIG_MTIME = None
    log("[Config] agent_config.json enregistre.")


def load_install_info():
    try:
        if not os.path.exists(INSTALL_INFO_FILE):
            return {}
        with open(INSTALL_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"[Config] Impossible de charger install_info.json : {e}")
        return {}


def save_install_info(data: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(INSTALL_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log("[Config] install_info.json enregistre.")
