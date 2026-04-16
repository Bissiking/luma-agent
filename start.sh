#!/bin/sh

set -e

AGENT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VENV_DIR="$AGENT_DIR/venv"

echo "[LUMA-Agent] Preparation..."

if [ -f /etc/alpine-release ]; then
    DISTRO="alpine"
elif command -v apt >/dev/null 2>&1; then
    DISTRO="debian"
else
    echo "[LUMA-Agent] Distribution non supportee"
    exit 1
fi

echo "[LUMA-Agent] Distro detectee : $DISTRO"

if [ "$DISTRO" = "debian" ]; then
    if ! command -v python3 >/dev/null 2>&1; then
        apt update -y
        apt install -y python3 python3-venv python3-pip
    fi
elif [ "$DISTRO" = "alpine" ]; then
    apk add --no-cache python3 py3-pip py3-virtualenv
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "[LUMA-Agent] Creation du venv..."
    python3 -m venv "$VENV_DIR"
fi

echo "[LUMA-Agent] Installation des dependances Python..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$AGENT_DIR/requirements.txt"

echo "[LUMA-Agent] Lancement de l'agent Orion..."
exec "$VENV_DIR/bin/python" "$AGENT_DIR/agent.py"
