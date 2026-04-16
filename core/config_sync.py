# ============================================================
# Orion Agent — Synchronisation de configuration (Pull)
# Auteur : M. HEMERY
# ============================================================

from core.logger import log
from core.config import get_identity, load_config, save_config
from requests.exceptions import Timeout, ConnectionError
from core.http import get_http_session

def check_remote_config():
    """Vérifie périodiquement s’il existe une nouvelle configuration à appliquer depuis LUMA."""
    ident = get_identity()
    cfg = load_config()

    if not ident:
        log("⚠️ Aucune identité trouvée — impossible de vérifier la config distante.")
        return False

    url = cfg["api"]["base_url"].rstrip("/") + f"/pull-config/{ident['uuid']}"
    headers = {"X-Auth-Token": ident["token"]}

    log(f"[ConfigSync] 🌐 Vérification de configuration distante → {url}")

    try:
        timeout = cfg.get("api", {}).get("timeout", 5)
        r = get_http_session().get(url, headers=headers, timeout=timeout)

        log(f"[ConfigSync] ↩️ Réponse HTTP {r.status_code}")

        # === Cas standard : nouvelle configuration reçue ===
        if r.status_code == 200:
            data = r.json()
            new_conf = data.get("config", {})

            if new_conf:
                save_config(new_conf)
                log(f"⚙️ Configuration mise à jour ({len(new_conf)} paramètres appliqués).")
                return True
            else:
                log("✅ Réponse valide mais aucune modification détectée.")
                return False

        # === Aucun changement ===
        elif r.status_code == 204:
            log("✅ Aucun changement de configuration à appliquer.")
            return False

        # === Auth échouée ===
        elif r.status_code == 403:
            log("⛔ Authentification échouée (token invalide ou agent inconnu).")
            return False

        # === Erreur serveur ===
        else:
            log(f"⚠️ Erreur inattendue lors du pull-config (HTTP {r.status_code}).")
            return False

    except Timeout:
        log("⌛ Timeout réseau — le serveur n’a pas répondu dans le délai imparti (5s).")
        return False

    except ConnectionError:
        log("📡 Connexion impossible — vérifie la connectivité réseau de l’agent.")
        return False

    except Exception as e:
        log(f"💥 Erreur fatale durant le pull-config : {e}")
        return False
