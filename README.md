# P-2.*-Grizzly - Agent de Monitoring Système

## Description

P-2.*-Grizzly est un agent de monitoring système léger et modulaire, développé en Python. Il collecte des métriques système (CPU, mémoire, disque, réseau, etc.) et les envoie à un serveur central via une API REST.

L'agent est conçu avec une architecture flexible qui permet d'ajouter facilement de nouveaux collecteurs de métriques.

## Fonctionnalités

- **Collecte de métriques système** :
  - CPU (utilisation globale, par cœur, statistiques)
  - Mémoire (RAM et swap)
  - Disque (utilisation, partitions, I/O)
  - Réseau (interfaces, trafic, connexions)
  - Docker (si disponible)
  - Services web (vérification par requêtes HTTP)

- **Détection d'anomalies** basée sur des seuils configurables
- **Communication API REST** pour envoyer les données à un serveur central
- **Configuration flexible** via fichier YAML local ou API distante
- **Logging configurable** pour faciliter le débogage
- **Gestion d'erreurs robuste** (perte de connexion, échecs d'API)

## Prérequis

- Python 3.8 ou supérieur
- Les bibliothèques Python suivantes (installées automatiquement via `requirements.txt`) :
  - psutil
  - requests
  - pyyaml

## Installation

### Installation depuis le dépôt

```bash
# Cloner le dépôt
git clone https://github.com/username/p-2.0.0-grizzly.git
cd p-2.0.0-grizzly

# Installer les dépendances
pip install -r requirements.txt

# Créer le répertoire de logs
mkdir -p logs
```

### Installation via pip (à venir)

```bash
pip install p-2.0.0-grizzly
```

## Configuration

L'agent utilise un fichier de configuration au format YAML. Par défaut, le fichier `config.yaml` est utilisé, mais vous pouvez spécifier un autre fichier avec l'option `--config`.

### Configuration Minimaliste avec LUMA

Une nouvelle fonctionnalité majeure est maintenant disponible : **la configuration à distance via LUMA**.

Vous pouvez utiliser un fichier de configuration minimal qui contient uniquement les informations essentielles pour se connecter à LUMA, puis l'agent récupérera le reste de la configuration depuis le serveur LUMA.

Fichier minimal exemple (`config.minimal.yaml`) :

```yaml
# Configuration minimale pour l'agent de monitoring "P-2.0.0-Grizzly"
agent:
  version: "P-2.0.0-Grizzly"  # Version de l'agent
  remote_config: true         # Activer la configuration distante
  log_level: "info"           # Niveau de logs (debug, info, warning, error)
  log_file: "logs/agent.log"  # Fichier de logs

# Configuration de l'API (OBLIGATOIRE)
api:
  base_url: "https://mhemery.fr/api"  # URL de base de l'API
  uuid: "votre-uuid-unique"    # UUID unique de l'agent 
  token: "votre-token-secret"  # Token d'authentification (Bearer Token)
  timeout: 30                  # Timeout en secondes
```

Fonctionnement :
1. Au démarrage, l'agent charge la configuration minimale
2. Il se connecte à LUMA pour récupérer la configuration complète
3. La configuration récupérée est enregistrée dans `luma_config.yaml`
4. L'agent combine la configuration minimale et la configuration LUMA
5. Si LUMA n'est pas disponible, l'agent utilise la dernière configuration enregistrée

Cette approche vous permet de gérer centralement la configuration de tous vos agents, tout en maintenant la possibilité de fonctionner en mode déconnecté.

### Configuration Complète

Vous pouvez aussi utiliser une configuration complète si vous préférez gérer localement la configuration de l'agent.

### Configurer l'agent

1. Copiez le fichier de configuration exemple :
   ```bash
   cp config-exemple.yaml config.yaml
   ```

2. Modifiez le fichier `config.local.yaml` avec vos paramètres :
   - Configurez les informations d'API (URL, UUID, token)
   - Ajustez les intervalles de collecte
   - Activez/désactivez les collecteurs
   - Configurez les seuils d'alerte

### Paramètres principaux

- **agent** : Configuration générale de l'agent
  - `interval` : Intervalle de collecte des métriques (en secondes)
  - `log_level` : Niveau de logging (DEBUG, INFO, WARNING, ERROR)
  - `log_file` : Chemin vers le fichier de log

- **api** : Configuration de l'API
  - `base_url` : URL de base du serveur central
  - `uuid` : UUID unique de l'agent
  - `token` : Token d'authentification

- **collectors** : Configuration des collecteurs de métriques
  - Chaque collecteur peut être activé/désactivé et configuré individuellement

- **alerts** : Configuration des seuils d'alerte
  - Seuils pour CPU, mémoire, disque, etc.

## Utilisation

### Configuration par Ligne de Commande

Vous pouvez maintenant configurer l'agent directement via les arguments de ligne de commande, sans avoir à modifier un fichier de configuration. Cette approche est idéale pour les déploiements automatisés et les environnements conteneurisés.

```bash
python agent.py --api-url https://dev.mhemery.fr/api/monitoring \
                --api-uuid votre-uuid-unique \
                --api-token votre-token-secret \
                --log-level info \
                --interval 60
```

Si un fichier `config.yaml` existe, les arguments CLI auront la priorité sur les valeurs du fichier.

Avantages de cette approche :
- Déploiement facile sans avoir à créer/modifier des fichiers
- Idéal pour les environnements de conteneurs ou serverless
- Peut être utilisé avec des variables d'environnement via des scripts

### Mode normal (démon)

Pour exécuter l'agent en mode normal, en utilisant le fichier de configuration par défaut :

```bash
python agent.py
```

Avec un fichier de configuration spécifique :

```bash
python agent.py -c config.local.yaml
```

### Mode test

Pour exécuter l'agent une seule fois et afficher les résultats :

```bash
python agent.py -t
```

Pour obtenir les résultats au format JSON :

```bash
python agent.py -t -j
```

Pour écrire les résultats dans un fichier :

```bash
python agent.py -t -o metrics.json
```

### Options de ligne de commande

Options générales :
- `-c, --config` : Spécifier un fichier de configuration
- `-t, --test` : Exécuter en mode test (une seule fois)
- `-j, --json` : Afficher les résultats au format JSON (mode test)
- `-o, --output` : Écrire les résultats dans un fichier (mode test)

Options de configuration :
- `--api-url` : URL de base de l'API (ex: https://dev.mhemery.fr/api/monitoring)
- `--api-uuid` : UUID unique de l'agent
- `--api-token` : Token d'authentification pour l'API
- `--log-level` : Niveau de log (debug, info, warning, error)
- `--log-file` : Fichier de log (ex: logs/agent.log)
- `--interval` : Intervalle de collecte en secondes
- `--remote-config` : Activer la récupération de configuration depuis LUMA
- `--no-remote-config` : Désactiver la récupération de configuration depuis LUMA

Exemple complet :
```bash
python agent.py --api-url https://dev.mhemery.fr/api/monitoring \
                --api-uuid votre-uuid-unique \
                --api-token votre-token-secret \
                --log-level debug \
                --log-file logs/debug.log \
                --interval 30 \
                --remote-config \
                -t -j
```

## Architecture

L'agent est conçu avec une architecture modulaire pour faciliter la maintenance et l'extension :

- **Collecteurs de métriques** : Modules indépendants pour chaque type de métrique
- **API Client** : Communication avec le serveur central
- **Gestionnaire de configuration** : Gestion des configurations locales et distantes
- **Gestionnaire d'alertes** : Détection d'anomalies basée sur des seuils

### Ajouter un nouveau collecteur

Pour ajouter un nouveau collecteur de métriques :

1. Créer un nouveau fichier dans `src/collectors/`
2. Hériter de la classe `BaseCollector`
3. Implémenter la méthode `collect()`
4. Ajouter le collecteur à `src/collectors/__init__.py`

## Sécurité

- L'agent utilise l'authentification par UUID et token pour l'API
- Les communications sont effectuées en HTTPS (si configuré)
- Les fichiers de configuration doivent être protégés car ils contiennent des informations sensibles

## Dépannage

### Journaux (logs)

Les journaux sont écrits dans le fichier spécifié dans la configuration (`log_file`). Vous pouvez augmenter le niveau de détail en réglant `log_level` sur `DEBUG`.

### Problèmes courants

- **L'agent ne démarre pas** : Vérifiez les permissions, les dépendances et le fichier de configuration
- **Échecs de connexion API** : Vérifiez la connectivité réseau et les paramètres d'API
- **Métriques manquantes** : Vérifiez que le collecteur correspondant est activé

## Licence

[Licence MIT](LICENSE)

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des pull requests ou à ouvrir des issues sur GitHub.

## Configuration de l'agent

L'agent nécessite trois informations essentielles pour fonctionner :
- **URL de l'API** : URL de base de l'API LUMA
- **UUID de l'agent** : Identifiant unique de l'agent
- **Token d'authentification** : Token sécurisé pour l'authentification auprès de l'API

Ces informations peuvent être fournies de plusieurs façons, par ordre de priorité :

### 1. Variables d'environnement (recommandé)

Créez un fichier `.env` à la racine du projet, basé sur le modèle `.env.example` :

```
# Configuration de l'API LUMA
LUMA_API_URL=https://dev.api.mhemery.fr/api
LUMA_API_UUID=votre-uuid-unique
LUMA_API_TOKEN=votre-token-secret
```

Vous pouvez également définir ces variables directement dans votre système d'exploitation.

### 2. Arguments en ligne de commande

```bash
python agent.py --api-url https://dev.api.mhemery.fr/api --api-uuid votre-uuid-unique --api-token votre-token-secret
```

### 3. Fichier de configuration

Créez un fichier `config.yaml` à la racine du projet :

```yaml
api:
  base_url: "https://dev.api.mhemery.fr/api"
  uuid: "votre-uuid-unique"
  token: "votre-token-secret"
```

## Fonctionnement

Au démarrage, l'agent effectue les opérations suivantes :

1. Chargement de la configuration (variables d'environnement, arguments en ligne de commande, fichier config.yaml)
2. Connexion à l'API LUMA via l'endpoint `/api/v1/agents/:uuid/checkin`
3. Récupération de la configuration complète depuis le serveur
4. Configuration des collecteurs et des alertes
5. Démarrage des collecteurs selon les intervalles spécifiés
6. Envoi régulier des métriques au serveur
7. Surveillance des seuils d'alerte

## Alertes et Surveillance

L'agent surveille plusieurs métriques système et peut déclencher des alertes lorsque les seuils sont dépassés.

### Métriques surveillées

- **CPU** : Utilisation du processeur
- **Mémoire** : Utilisation de la RAM
- **Disque** : Espace disque disponible
- **Réseau** : Trafic réseau
- **Services** : État des services Windows/Linux
- **Docker** : État des conteneurs Docker

### Seuils d'alerte

Les seuils d'alerte sont configurés automatiquement via la réponse du check-in API. 

## Dépendances

- Python 3.6+
- psutil
- requests
- pyyaml
- python-dotenv

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/luma-agent.git
cd luma-agent

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
cp .env.example .env
# Modifier le fichier .env avec vos informations

# Lancer l'agent
python agent.py
``` 