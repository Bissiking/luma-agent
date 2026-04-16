#!/bin/sh

set -eu

SERVICE_NAME="${SERVICE_NAME:-luma-orion-agent}"
INSTALL_DIR="${INSTALL_DIR:-/opt/luma-agent}"
SERVICE_USER="${SERVICE_USER:-luma-agent}"
SERVICE_GROUP="${SERVICE_GROUP:-$SERVICE_USER}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
UNIT_TEMPLATE="$REPO_ROOT/linux/systemd/luma-orion-agent.service"
UNIT_TARGET="/etc/systemd/system/$SERVICE_NAME.service"

if [ "$(id -u)" -ne 0 ]; then
    echo "Ce script doit etre execute en root."
    exit 1
fi

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
    useradd --system --create-home --home-dir "$INSTALL_DIR" --shell /usr/sbin/nologin "$SERVICE_USER"
fi

mkdir -p "$INSTALL_DIR"
cp -R "$REPO_ROOT"/. "$INSTALL_DIR"/
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"

if [ ! -d "$INSTALL_DIR/venv" ]; then
    "$PYTHON_BIN" -m venv "$INSTALL_DIR/venv"
fi

"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

(
    cd "$INSTALL_DIR"
    "$INSTALL_DIR/venv/bin/python" -c "from datetime import datetime, timezone; from core.config import save_install_info; save_install_info({'mode': 'service', 'service_manager': 'systemd', 'service_name': '$SERVICE_NAME.service', 'service_user': '$SERVICE_USER', 'installed_at': datetime.now(timezone.utc).isoformat()})"
)

sed \
    -e "s|/opt/luma-agent|$INSTALL_DIR|g" \
    -e "s|User=luma-agent|User=$SERVICE_USER|g" \
    -e "s|Group=luma-agent|Group=$SERVICE_GROUP|g" \
    "$UNIT_TEMPLATE" > "$UNIT_TARGET"

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME.service"

echo "Service installe : $SERVICE_NAME.service"
