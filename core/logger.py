# core/logger.py
# ============================================================
# Orion Agent — Logger journalier (UTC, Docker-safe)
# Auteur : M. HEMERY
# ============================================================

import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "agent.log")

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("orion-agent")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s UTC] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",      # rotation quotidienne
    interval=1,
    backupCount=14,       # rétention 14 jours
    utc=True,             # IMPORTANT
    encoding="utf-8"
)

handler.suffix = "%Y-%m-%d"   # nommage par jour
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.propagate = False

def log(msg):
    logger.info(msg)
