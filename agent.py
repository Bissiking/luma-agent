# ============================================================
# Orion Agent — Point d’entrée principal (Rigel Rebuild Edition)
# Auteur : M. HEMERY
# ============================================================

import platform
import requests
from core.logger import log
from core.config import get_identity, save_identity, save_config
from core.loop import start_main_loop

BASE_URL = "https://mhemery.fr/api/orion/comm"

# ============================================================
# 🔐 Fonction : Demande de clé d’enrôlement
# ============================================================
def ask_register_key():
    print("\n🛰️ Orion Agent — Enrôlement initial")
    print("Aucune identité trouvée.")
    print("Veuillez entrer la clé d’enrôlement Orion (register key)")
    return input("→ Register key : ").strip()

# ============================================================
# 🧭 Fonction : Enrôlement manuel de l’agent Orion
# ============================================================
def register_with_luma():
    register_key = ask_register_key()
    payload = {
        "register_key": register_key,
        "hostname": platform.node(),
        "os": platform.system(),
        "arch": platform.machine(),
        "env": "manual",
    }

    try:
        log(f"🔗 Enrôlement auprès de LUMA ({BASE_URL}/register)...")
        r = requests.post(f"{BASE_URL}/register", json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()

        # Sauvegarde identité + config par défaut
        save_identity({
            "uuid": data["uuid"],
            "token": data["token"],
            "api_key": data["api_key"],
        })
        save_config(data.get("default_config", {}))

        log(f"✅ Agent enregistré avec succès : {data['uuid']}")
        return data

    except Exception as e:
        log(f"❌ Échec de l'enrôlement : {e}")
        return None


# ============================================================
# 🚀 Point d’entrée principal
# ============================================================
if __name__ == "__main__":
    print("🚀 Orion Agent — Démarrage du module principal...")

    identity = get_identity()
    if not identity:
        identity = register_with_luma()

    if not identity:
        log("⛔ Impossible de démarrer sans enrôlement valide.")
    else:
        log(f"🛰️ Agent opérationnel ({identity['uuid']}) — lancement de la boucle.")
        try:
            start_main_loop()
        except KeyboardInterrupt:
            log("🧩 Arrêt manuel détecté — extinction propre de l’agent.")
        except Exception as e:
            log(f"💥 Crash critique de l’agent Orion : {e}")
