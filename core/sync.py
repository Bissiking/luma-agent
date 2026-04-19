import platform
import socket
import time

from core.config import get_identity, load_config
from core.http import get_http_session
from core.logger import log

AGENT_VERSION = "OA-0.6.2-Rigel"
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


def build_sync_payload(metrics=None, sync_kind="full"):
    ident = get_identity()
    if not ident:
        log("Aucune identite trouvee -> agent non enregistre.")
        return None

    cfg = load_config()
    metrics = metrics or {}
    core_metrics = metrics.get("core", {})
    modules = metrics.get("modules", {})
    partial_failures = metrics.get("partial_failures", [])

    local_ip = get_local_ip()
    os_name = get_os_name()
    arch = platform.machine()

    configured_modules = cfg.get("modules", {})
    capabilities = []
    for name, value in configured_modules.items():
        if isinstance(value, dict) and value.get("enabled"):
            capabilities.append(name)
        elif value is True:
            capabilities.append(name)
    capabilities = sorted(capabilities)

    return {
        "schema_version": SCHEMA_VERSION,
        "uuid": ident["uuid"],
        "token": ident["token"],
        "ip": local_ip,
        "os": os_name,
        "arch": arch,
        "version": AGENT_VERSION,
        "agent": {
            "uuid": ident["uuid"],
            "version": AGENT_VERSION,
            "capabilities": capabilities,
        },
        "system": {
            "host": {
                "hostname": core_metrics.get("hostname"),
                "ip": local_ip,
            },
            "platform": {
                "os": os_name,
                "arch": arch,
            },
            "installation": core_metrics.get("installation", {}),
        },
        "metrics": core_metrics,
        "modules": modules,
        "meta": {
            "sync_kind": sync_kind,
            "collected_at": int(time.time()),
            "partial_failures": partial_failures,
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
            log(f"Sync {sync_kind} OK depuis {payload['ip']} - Agent v{AGENT_VERSION}")
            return True
        if response.status_code == 403:
            log("Authentification echouee (token invalide).")
            return False

        log(f"Erreur de synchronisation {sync_kind} : {response.status_code}")
        return False

    except Exception as e:
        log(f"Erreur reseau pendant sync {sync_kind} : {e}")
        return False
