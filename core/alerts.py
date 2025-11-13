# ============================================================
# Orion Agent — Gestion et émission d’alertes
# Auteur : M. HEMERY
# ============================================================

import requests
import json
from core.logger import log
from core.config import get_identity, load_config

# ============================================================
# 🚨 Envoi d'une alerte à LUMA Orion
# ============================================================
def push_alert(severity, alert_type, message, metadata=None):
    """
    Envoie une alerte au serveur LUMA Orion.
    - severity: 'info' | 'warning' | 'critical'
    - alert_type: 'cpu', 'ram', 'disk', etc.
    - message: texte descriptif de l’alerte
    - metadata: dict optionnel (infos techniques)
    """
    ident = get_identity()
    cfg = load_config()

    if not ident:
        log("⚠️ Impossible d’envoyer une alerte : identité manquante.")
        return False

    payload = {
        "uuid": ident["uuid"],
        "token": ident["token"],   # ✅ sécurité Orion (plus api_key)
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
        "metadata": metadata or {},
    }

    try:
        url = cfg["api"]["base_url"].rstrip("/") + "/alert"
        r = requests.post(url, json=payload, timeout=5)

        if r.status_code == 200:
            log(f"🚨 Alerte Orion envoyée ({severity}) — {alert_type}: {message}")
            return True
        else:
            log(f"⚠️ Erreur lors de l’envoi d’alerte ({r.status_code}) : {r.text}")
            queue_local_alert(payload)  # enregistre localement si besoin
            return False

    except Exception as e:
        log(f"❌ Alerte échouée ({alert_type}) : {e}")
        queue_local_alert(payload)
        return False


# ============================================================
# 🧠 Stockage local temporaire (en cas d’offline)
# ============================================================
def queue_local_alert(payload):
    """
    Sauvegarde l’alerte localement si la connexion à LUMA échoue.
    """
    try:
        with open("local_alerts.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        log("📦 Alerte ajoutée à la file locale (offline).")
    except Exception as e:
        log(f"⚠️ Impossible d’enregistrer l’alerte locale : {e}")


# ============================================================
# 🚀 Traitement différé des alertes locales
# ============================================================
def process_pending_alerts():
    """
    Réenvoie les alertes locales si la connexion à LUMA est rétablie.
    """
    try:
        with open("local_alerts.json", "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            return

        log(f"📤 Envoi différé de {len(lines)} alerte(s) locale(s)...")

        sent = 0
        for line in lines:
            try:
                payload = json.loads(line)
                push_alert(
                    payload.get("severity"),
                    payload.get("alert_type"),
                    payload.get("message"),
                    payload.get("metadata"),
                )
                sent += 1
            except Exception:
                pass

        # purge après envoi
        open("local_alerts.json", "w").close()
        log(f"✅ {sent} alerte(s) locale(s) renvoyée(s).")
    except FileNotFoundError:
        pass
    except Exception as e:
        log(f"⚠️ Erreur traitement des alertes locales : {e}")
