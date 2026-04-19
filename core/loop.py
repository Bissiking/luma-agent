import time

from core.alerts import process_pending_alerts
from core.config import load_config
from core.config_sync import check_remote_config
from core.logger import log
from core.metrics import collect_metrics
from core.services import check_services_watch
from core.sync import sync_with_luma

TICK_SLEEP = 60


def start_main_loop():
    log("Orion Agent - Boucle principale demarree.")

    last_ping = 0.0
    last_sync = 0.0
    last_config_check = 0.0

    while True:
        try:
            cfg = load_config()
            heartbeat_interval = cfg.get("heartbeat_interval", 60)
            sync_interval = cfg.get("sync_interval", 600)
            config_check_interval = cfg.get("config_check_interval", 900)

            now = time.time()

            should_full_sync = now - last_sync >= sync_interval
            should_heartbeat = now - last_ping >= heartbeat_interval

            try:
                metrics = collect_metrics(include_modules=True)
            except Exception as e:
                log(f"Echec de collecte des metriques : {e}")
                metrics = {
                    "core": {},
                    "modules": {},
                    "partial_failures": [f"core:{e}"],
                }

            services_metrics = metrics.get("core", {}).get("services")
            if services_metrics:
                try:
                    check_services_watch(services_metrics, cfg)
                except Exception as e:
                    log(f"Erreur surveillance services : {e}")

            if should_full_sync:
                try:
                    sync_with_luma(metrics, sync_kind="full")
                    last_sync = now
                    last_ping = now
                except Exception as e:
                    log(f"Erreur durant la sync complete : {e}")
            elif should_heartbeat:
                try:
                    heartbeat_metrics = {
                        "core": metrics.get("core", {}),
                        "modules": metrics.get("modules", {}),
                        "partial_failures": metrics.get("partial_failures", []),
                    }
                    sync_with_luma(heartbeat_metrics, sync_kind="heartbeat")
                    last_ping = now
                except Exception as e:
                    log(f"Erreur lors du ping Orion : {e}")

            if now - last_config_check >= config_check_interval:
                try:
                    check_remote_config()
                    last_config_check = now
                except Exception as e:
                    log(f"Erreur durant la verification de configuration : {e}")

            try:
                process_pending_alerts()
            except Exception as e:
                log(f"Erreur traitement alertes : {e}")

            time.sleep(TICK_SLEEP)

        except KeyboardInterrupt:
            log("Interruption manuelle detectee - arret propre de l'agent.")
            break
        except Exception as e:
            log(f"Crash dans la boucle principale : {e}")
            time.sleep(10)
