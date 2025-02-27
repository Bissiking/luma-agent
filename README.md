# LUMA Agent

Agent autonome avec système de modules et interface web intégrée.

## Fonctionnalités

- 🔌 Système de modules extensible
- 🔄 Synchronisation avec LUMA (serveur central)
- 📊 Interface web de monitoring
- 🔔 Notifications Discord intégrées
- 📝 Logging avancé
- 🛠️ API pour le développement de modules
- 🔒 Gestion des configurations sécurisée
- 💻 Support multi-plateformes (Windows, Linux, MacOS)
- 🐳 Détection d'environnement container

## Prérequis

- Python 3.8 ou supérieur
- Accès Internet (pour les dépendances et notifications)

## Installation et Démarrage Rapide

### Windows (PowerShell - Recommandé)
```powershell
# Cloner le repository
git clone https://github.com/votre-repo/luma-agent.git
cd luma-agent

# Lancer l'agent (installation automatique)
.\start.ps1
```

### Windows (Batch - Alternative)
```batch
# Cloner le repository
git clone https://github.com/votre-repo/luma-agent.git
cd luma-agent

# Lancer l'agent (installation automatique)
start.bat
```

### Linux/MacOS
```bash
# Cloner le repository
git clone https://github.com/votre-repo/luma-agent.git
cd luma-agent

# Rendre le script exécutable
chmod +x start.sh

# Lancer l'agent (installation automatique)
./start.sh
```

Les scripts de démarrage vont automatiquement :
1. Vérifier la version de Python
2. Créer un environnement virtuel si nécessaire
3. Installer/mettre à jour les dépendances
4. Créer un fichier `.env` depuis `.env.example` si nécessaire
5. Lancer l'agent

## Configuration

Éditer le fichier `.env` avec vos paramètres :
```env
# Configuration de l'agent
AGENT_NAME=luma-agent
PORT=8000
LOG_LEVEL=INFO
ENV=development

# Configuration LUMA
LUMA_API_URL=http://votre-serveur-luma
LUMA_API_KEY=votre-clé-api

# Discord (optionnel)
DISCORD_WEBHOOK_URL=votre-webhook-discord
```

## Développement de modules

Pour créer un nouveau module :

1. Créer un dossier dans `modules/`
2. Implémenter la classe du module héritant de `BaseModule`
3. Créer un fichier `config.yaml` pour la configuration du module

Exemple de module :
```python
from core.base_module import BaseModule

class MyModule(BaseModule):
    async def on_load(self):
        self.logger.info("Module chargé")
        
    async def on_unload(self):
        self.logger.info("Module déchargé")
```

## API

L'agent expose une API REST sur le port configuré (8000 par défaut) :

- `GET /api/modules` - Liste des modules
- `GET /api/system` - Informations système
- `POST /api/modules/{name}/config` - Mise à jour de la configuration
- `GET /api/status` - État de l'agent

## Interface Web

L'interface web est accessible sur `http://localhost:8000` et permet de :

- Visualiser l'état des modules
- Configurer les modules
- Voir les logs en temps réel
- Monitorer les ressources système

## Dépendances

L'agent utilise un minimum de dépendances externes pour faciliter la maintenance :
- `aiohttp` - Serveur web et client HTTP
- `psutil` - Informations système
- `aiosqlite` - Base de données SQLite
- `python-dotenv` - Variables d'environnement
- `pyyaml` - Configuration des modules 