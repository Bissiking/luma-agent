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

# === ENV ====================================================
env_file = os.path.join(os.path.dirname(__file__), "..", ".orion-env")

# === Logger =================================================
logger = logging.getLogger("orion-agent")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s UTC] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === File handler (toujours actif) ==========================
file_handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=14,
    utc=True,
    encoding="utf-8"
)
file_handler.suffix = "%Y-%m-%d"
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# === Console handler (DEV only) =============================
if os.path.exists(env_file):
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

logger.propagate = False

def log(msg):
    logger.info(msg)
