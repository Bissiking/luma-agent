# Orion — Installation de l’Agent
##### Ce document décrit l’installation et le lancement de l’agent **Orion** sur une machine Linux.
---
## Prérequis

- Linux (Ubuntu/Debian recommandé)
- Python **3.10+**
- `git`
- Accès réseau vers le serveur Orion (API)

Vérification rapide :
```bash
python3 --version
git --version
```

---

## Récupération de l’agent
```bash
git clone https://github.com/<org>/orion-agent.git
cd orion-agent
```
---
## Script de lancement (start.sh)
```bash
chmod +x start.sh
```
---
## Lancement de l’agent
```bash
./start.sh
```
