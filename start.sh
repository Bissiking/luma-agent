#!/bin/sh
# =============================
#  LUMA ORION AGENT – Setup
#  Auteur : M. HEMERY
# =============================

set -e

echo "[LUMA-Agent] 🔍 Préparation…"

# --- Détection distro ---
if [ -f /etc/alpine-release ]; then
    DISTRO="alpine"
elif command -v apt >/dev/null 2>&1; then
    DISTRO="debian"
else
    echo "[LUMA-Agent] ❌ Distribution non supportée"
    exit 1
fi

echo "[LUMA-Agent] 🧭 Distro détectée : $DISTRO"

# --- Dépendances système ---
if [ "$DISTRO" = "debian" ]; then
    if ! dpkg -s python3-venv >/dev/null 2>&1; then
        echo "[LUMA-Agent] 📦 Installation python3-venv…"
        apt update -y
        apt install -y python3 python3-venv python3-pip
    fi
elif [ "$DISTRO" = "alpine" ]; then
    echo "[LUMA-Agent] 📦 Installation Python (apk)…"
    apk add --no-cache python3 py3-pip py3-virtualenv
fi

# --- Venv ---
if [ ! -d "/luma-agent/venv" ]; then
    echo "[LUMA-Agent] 🧪 Création de l'environnement virtuel…"
    python3 -m venv /luma-agent/venv
fi

# --- Activation ---
echo "[LUMA-Agent] ⚙️ Activation du venv…"
. /luma-agent/venv/bin/activate

# --- Python deps ---
echo "[LUMA-Agent] 📦 Installation des dépendances Python…"
pip install --upgrade pip
pip install requests psutil
pip install -r /luma-agent/requirements.txt

# --- Lancement ---
echo "[LUMA-Agent] 🚀 Lancement de l'agent Orion…"
exec python /luma-agent/agent.py
