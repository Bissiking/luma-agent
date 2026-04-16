import os
import platform
import subprocess
import time

from core.config import load_install_info


_CACHE = {
    "expires_at": 0.0,
    "value": None,
}


def _is_service_process():
    return bool(os.getenv("INVOCATION_ID") or os.getenv("ORION_SERVICE_MODE") == "systemd")


def _get_systemd_status(service_name: str):
    now = time.time()
    if _CACHE["value"] is not None and _CACHE["expires_at"] > now:
        return _CACHE["value"]

    value = {
        "active": None,
        "enabled": None,
        "error": None,
    }

    try:
        active = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        enabled = subprocess.run(
            ["systemctl", "is-enabled", service_name],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        value["active"] = active.stdout.strip() == "active"
        value["enabled"] = enabled.stdout.strip() == "enabled"
    except Exception as exc:
        value["error"] = str(exc)

    _CACHE["value"] = value
    _CACHE["expires_at"] = now + 60
    return value


def collect_installation_status():
    install_info = load_install_info()
    system = platform.system().lower()

    status = {
        "platform": system,
        "mode": install_info.get("mode", "manual"),
        "service_manager": install_info.get("service_manager"),
        "service_name": install_info.get("service_name"),
        "service_user": install_info.get("service_user"),
        "installed_at": install_info.get("installed_at"),
        "is_service_process": _is_service_process(),
    }

    if system == "linux" and status["service_manager"] == "systemd" and status["service_name"]:
        status.update(_get_systemd_status(status["service_name"]))

    return status
