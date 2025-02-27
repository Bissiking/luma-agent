# Structure du Projet LUMA Agent

## Scripts de Démarrage
- `start.ps1` - Script de démarrage pour Windows PowerShell (recommandé)
- `start.bat` - Script de démarrage pour Windows Command Prompt
- `start.sh` - Script de démarrage pour Linux/MacOS

## Fichiers Racine
- `main.py` - Point d'entrée principal de l'application
- `requirements.txt` - Liste des dépendances Python
- `.env.example` - Exemple de configuration (à copier vers .env)
- `README.md` - Documentation principale du projet
- `STRUCTURE.md` - Ce fichier (documentation de la structure)

## Core (core/)
Contient les composants principaux de l'agent :

- `base_module.py` - Classe de base pour tous les modules
  * Définit l'interface standard des modules
  * Gère le cycle de vie (chargement/déchargement)
  * Fournit des utilitaires communs (logging, notifications)

- `module_manager.py` - Gestionnaire de modules
  * Charge et décharge les modules
  * Gère les configurations des modules
  * Maintient l'état des modules

- `web_server.py` - Serveur web de l'agent
  * API REST pour la gestion des modules
  * Interface web de monitoring
  * Gestion des fichiers statiques

- `http_client.py` - Client HTTP unifié
  * Gère toutes les requêtes HTTP
  * Notifications Discord
  * Communication avec LUMA

- `utils.py` - Utilitaires généraux
  * Configuration du logging
  * Informations système
  * Fonctions helpers

## Modules (modules/)
Dossier contenant les modules installés. Chaque module a la structure suivante :
```
modules/
  └── nom_module/
      ├── module.py    - Code principal du module
      └── config.yaml  - Configuration du module
```

## Interface Web
- `templates/` - Templates HTML
  * `index.html` - Dashboard principal

- `static/` - Fichiers statiques
  * CSS, JavaScript, images, etc.

## Données (data/)
- Base de données SQLite
- Fichiers de configuration
- Données persistantes des modules

## Logs (logs/)
Fichiers de logs générés automatiquement :
- `luma-agent.log` - Log principal
- Logs spécifiques aux modules

## Dépendances Principales
- `aiohttp` - Serveur web et client HTTP
- `psutil` - Informations système
- `aiosqlite` - Base de données SQLite
- `python-dotenv` - Variables d'environnement
- `pyyaml` - Configuration des modules

## Structure des Modules
Exemple de structure d'un module :
```python
# modules/example/module.py
from core.base_module import BaseModule

class ExampleModule(BaseModule):
    async def on_load(self):
        self.logger.info("Module chargé")
        
    async def on_unload(self):
        self.logger.info("Module déchargé")
```

```yaml
# modules/example/config.yaml
name: example
version: 1.0.0
enabled: true
# Configuration spécifique au module
``` 