# Orion - Installation de l'Agent

Ce document decrit l'installation et le lancement de l'agent Orion sur une machine Linux.

## Prerequis

- Linux (Ubuntu/Debian recommande)
- Python 3.10+
- `git`
- acces reseau vers le serveur Orion

Verification rapide :

```bash
python3 --version
git --version
```

## Recuperation de l'agent

```bash
git clone https://github.com/Bissiking/luma-agent.git
cd luma-agent
```

## Lancement manuel

```bash
chmod +x start.sh
./start.sh
```

## Installation systemd

Le depot contient un installeur Linux et une unite `systemd`.

```bash
chmod +x linux/install_systemd.sh
sudo ./linux/install_systemd.sh
```

Par defaut, l'installation :

- copie l'agent dans `/opt/luma-agent`
- cree l'utilisateur systeme `luma-agent`
- cree un venv Python
- installe les dependances
- active `luma-orion-agent.service`

Commandes utiles :

```bash
sudo systemctl status luma-orion-agent.service
sudo systemctl restart luma-orion-agent.service
sudo journalctl -u luma-orion-agent.service -f
```

Variables d'environnement supportees par l'installeur :

- `SERVICE_NAME`
- `INSTALL_DIR`
- `SERVICE_USER`
- `SERVICE_GROUP`
- `PYTHON_BIN`

## Configuration Minecraft

Le module Minecraft est optionnel et se configure dans `config/agent_config.json` :

```json
{
  "modules": {
    "minecraft": {
      "enabled": true,
      "timeout": 3,
      "servers": [
        {
          "name": "Survie",
          "kind": "java",
          "host": "mc.example.net",
          "port": 25565
        }
      ]
    }
  }
}
```

La sync agent envoie maintenant un payload structure avec :

- `agent`
- `system`
- `metrics`
- `modules`
- `meta`

Le bloc `meta` contient notamment `sync_kind`, `collected_at` et `partial_failures`.
