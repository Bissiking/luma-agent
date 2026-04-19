import platform
import socket
import time
from datetime import datetime, timezone

from core.config import get_identity, load_config
from core.http import get_http_session
from core.logger import log

AGENT_VERSION = "OA-0.6.3-Rigel"
SCHEMA_VERSION = "2.0"

_OS_NAME = None
_LOCAL_IP_CACHE = {
    "value": None,
    "expires_at": 0.0,
}


def get_local_ip():
    if _LOCAL_IP_CACHE["value"] and _LOCAL_IP_CACHE["expires_at"] > time.time():
        return _LOCAL_IP_CACHE["value"]

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        _LOCAL_IP_CACHE["value"] = ip
        _LOCAL_IP_CACHE["expires_at"] = time.time() + 300
        return ip
    except Exception:
        return "0.0.0.0"
    finally:
        s.close()


def get_linux_distro():
    try:
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            data = {}
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    data[key] = value.strip('"')
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


def _iso_utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_sync_payload(metrics=None, sync_kind="full"):
    ident = get_identity()
    if not ident:
        log("Aucune identite trouvee -> agent non enregistre.")
        return None

    metrics = metrics or {}
    core_metrics = metrics.get("core", {})
    modules = metrics.get("modules", {})
    os_name = get_os_name()
    arch = platform.machine()

    return {
        "agent": {
            "uuid": ident["uuid"],
            "token": ident["token"],
            "version": AGENT_VERSION,
        },
        "system": {
            "hostname": core_metrics.get("hostname"),
            "os": os_name,
            "arch": arch,
        },
        "modules": modules,
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "payload_kind": f"sync_{sync_kind}",
            "sent_at": _iso_utc_now(),
        },
    }


def sync_with_luma(metrics=None, sync_kind="full"):
    cfg = load_config()
    payload = build_sync_payload(metrics=metrics, sync_kind=sync_kind)
    if payload is None:
        return False

    try:
        url = cfg["api"]["base_url"].rstrip("/") + "/sync"
        timeout = cfg.get("api", {}).get("timeout", 5)
        response = get_http_session().post(url, json=payload, timeout=timeout)

        if response.status_code == 200:
            log(f"Sync {sync_kind} OK pour {payload['system']['hostname']} - Agent v{AGENT_VERSION}")
            return True
        if response.status_code == 403:
            log("Authentification echouee (token invalide).")
            return False

        log(f"Erreur de synchronisation {sync_kind} : {response.status_code}")
        return False

    except Exception as e:
        log(f"Erreur reseau pendant sync {sync_kind} : {e}")
        return False
