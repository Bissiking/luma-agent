#!/bin/bash

# =============================
#  LUMA ORION AGENT – Setup
#  Auteur : M. HEMERY
# =============================

set -e

echo "[LUMA-Agent] 🔍 Préparation…"

# 1) Installer python3-venv si absent
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "[LUMA-Agent] 📦 Installation de python3-venv…"
    apt update -y
    apt install -y python3-venv
fi

# 2) Créer le venv si pas encore fait
if [ ! -d "/luma-agent/venv" ]; then
    echo "[LUMA-Agent] 🧪 Création de l'environnement virtuel…"
    python3 -m venv /luma-agent/venv
fi

# 3) Activer le venv
echo "[LUMA-Agent] ⚙️ Activation du venv…"
source /luma-agent/venv/bin/activate

# 4) Installer les dépendances nécessaires
echo "[LUMA-Agent] 📦 Installation des dépendances…"
pip install --upgrade pip
pip install requests psutil
pip install -r requirements.txt


# 5) Lancer l’agent automatiquement
echo "[LUMA-Agent] 🚀 Lancement de l'agent Orion…"
python /luma-agent/agent.py
