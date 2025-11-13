# ============================================================
# Orion Agent — Logger utilitaire (UTC Edition)
# Auteur : M. HEMERY
# ============================================================

import os
from datetime import datetime, timezone

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "agent.log")

def log(msg):
    """Affiche et enregistre un message horodaté en UTC."""
    timestamp = datetime.now(timezone.utc).strftime("[%Y-%m-%d %H:%M:%S UTC]")
    line = f"{timestamp} {msg}"
    print(line)

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[Logger] ⚠️ Impossible d’écrire dans {LOG_FILE} : {e}")
