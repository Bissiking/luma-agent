# ============================================================
# Orion Agent — Boucle principale (Configurable Edition)
# Auteur : M. HEMERY
# ============================================================

import time
from core.sync import sync_with_luma
from core.metrics import collect_metrics
from core.alerts import process_pending_alerts
from core.config import load_config
from core.config_sync import check_remote_config
from core.logger import log

TICK_SLEEP = 60  # 1 tick = 60s

def start_main_loop():
    log("🚀 Orion Agent — Boucle principale démarrée (mode dynamique).")

    last_ping = 0
    last_sync = 0
    last_config_check = 0

    while True:
        try:
            # 🔄 Recharge la config à chaque tick (utile si pull-config vient d’enregistrer une nouvelle version)
            cfg = load_config()
            heartbeat_interval = cfg.get("heartbeat_interval", 60)
            sync_interval = cfg.get("sync_interval", 600)
            config_check_interval = cfg.get("config_check_interval", 900)

            now = time.time()

            # --- Collecte des métriques ---
            try:
                metrics = collect_metrics()
            except Exception as e:
                log(f"⚠️ Échec de collecte des métriques : {e}")
                metrics = {}

            # --- Ping Orion (heartbeat) ---
            if now - last_ping >= heartbeat_interval:
                try:
                    sync_with_luma(metrics)
                    last_ping = now
                except Exception as e:
                    log(f"⚠️ Erreur lors du ping Orion : {e}")

            # --- Sync complète ---
            if now - last_sync >= sync_interval:
                try:
                    sync_with_luma(metrics)
                    last_sync = now
                except Exception as e:
                    log(f"⚠️ Erreur durant la sync complète : {e}")

            # --- Vérification de configuration distante ---
            if now - last_config_check >= config_check_interval:
                try:
                    check_remote_config()
                    last_config_check = now
                except Exception as e:
                    log(f"⚠️ Erreur durant la vérification de configuration : {e}")

            # --- Traitement des alertes locales ---
            try:
                process_pending_alerts()
            except Exception as e:
                log(f"⚠️ Erreur traitement alertes : {e}")

            # --- Pause avant le prochain tick ---
            time.sleep(TICK_SLEEP)

        except KeyboardInterrupt:
            log("🧩 Interruption manuelle détectée — arrêt propre de l’agent.")
            break
        except Exception as e:
            log(f"💥 Crash dans la boucle principale : {e}")
            time.sleep(10)  # évite le spam en cas d’erreur répétée
