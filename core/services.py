# ============================================================
# Orion Agent — Surveillance des services configurés
# Auteur : M. HEMERY
# ============================================================

from core.alerts import push_alert
from core.alert_state import (
    is_alert_active,
    mark_alert_active,
    clear_alert
)
from core.logger import log


def check_services_watch(services_metrics, cfg):
    """
    Vérifie l'état des services surveillés.
    - services_metrics : metrics["services"]
    - cfg : configuration chargée
    """

    watched = cfg.get("services_watch", [])
    if not watched:
        return  # rien à surveiller

    groups = services_metrics.get("groups", {})
    if not groups:
        return

    for service_name in watched:
        group = groups.get(service_name)

        # DOWN si absent ou plus aucun process
        is_down = not group or group.get("count", 0) == 0
        alert_key = f"service:{service_name}"

        # 🔴 SERVICE DOWN
        if is_down:
            if not is_alert_active(alert_key):
                log(f"🚨 Service arrêté détecté : {service_name}")

                push_alert(
                    severity="critical",
                    alert_type="service",
                    message=f"Service arrêté : {service_name}",
                    metadata={
                        "service": service_name,
                        "status": "down"
                    }
                )

                mark_alert_active(alert_key)

        # 🟢 SERVICE UP (RECOVERY)
        else:
            if is_alert_active(alert_key):
                log(f"✅ Service rétabli : {service_name}")

                push_alert(
                    severity="info",
                    alert_type="service",
                    message=f"Service rétabli : {service_name}",
                    metadata={
                        "service": service_name,
                        "status": "up"
                    }
                )

                clear_alert(alert_key)
