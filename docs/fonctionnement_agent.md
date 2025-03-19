# Guide de fonctionnement de l'agent Luma (P-2.0.0-Grizzly)

## Introduction

Luma Agent est un outil de monitoring système développé en Python (version P-2.0.0-Grizzly) conçu pour collecter des métriques système et les transmettre à un serveur central via une API REST. Ce document explique son fonctionnement, sa structure et comment l'utiliser.

## Architecture globale

L'agent est structuré de manière modulaire avec les composants principaux suivants:

- **Agent principal** (`agent.py` à la racine et `src/agent.py`) : Coordonne toutes les opérations
- **Collecteurs** (`src/collectors/`) : Modules responsables de la collecte des différentes métriques
- **Configuration** (`src/config/`) : Gestion de la configuration locale et distante
- **API** (`src/api/`) : Communication avec le serveur central
- **Utilitaires** (`src/utils/`) : Fonctions et classes utilitaires
- **Mise à jour** (`src/update/`) : Mécanismes de mise à jour de l'agent

## Fonctionnalités principales

L'agent est capable de:

1. **Collecter des métriques système**:
   - CPU (utilisation, température)
   - Mémoire (RAM utilisée, disponible)
   - Disque (espace utilisé, disponible sur plusieurs partitions)
   - Réseau (trafic entrant/sortant, état des connexions)
   - Docker (si disponible via `/var/run/docker.sock`)
   - Proxmox (fonctionnalités spécifiques)

2. **Surveiller des services web** via des requêtes HTTP

3. **S'authentifier** auprès d'une API avec UUID et token

4. **Envoyer des données** selon un intervalle configurable

5. **Détecter des anomalies** basées sur des seuils configurables

6. **Maintenir une empreinte système légère**

## Configuration

La configuration de l'agent peut être:

- **Locale** via un fichier YAML (`config.yaml`)
- **Distante** via l'API du serveur central

Un exemple de configuration est disponible dans `config-example.yaml`.

## Endpoints API

L'agent communique avec le serveur central via les endpoints:

- `POST /api/v1/monitoring/agent/checkin`: Signaler l'activité de l'agent
- `GET /api/v1/monitoring/agent/configuration`: Récupérer la configuration
- `POST /api/v1/monitoring/service/update`: Envoyer les données collectées
- `POST /api/v1/monitoring/alert/create`: Signaler une alerte

## Authentification

L'authentification utilise les headers HTTP:
- `X-Agent-UUID`: Identifiant unique de l'agent
- `X-Agent-Token`: Token d'authentification

## Installation et démarrage

1. Créer un environnement virtuel Python: `python -m venv .venv`
2. Activer l'environnement:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
3. Installer les dépendances: `pip install -r requirements.txt`
4. Copier `config-example.yaml` vers `config.yaml` et ajuster selon vos besoins
5. Lancer l'agent: `python agent.py`

## Développement

Pour étendre les fonctionnalités de l'agent:

1. **Ajouter un nouveau collecteur**: Créer une nouvelle classe dans `src/collectors/`
2. **Modifier la configuration**: Mettre à jour les constantes dans `src/constants.py`
3. **Ajouter des endpoints API**: Étendre les classes dans `src/api/`

## Support et compatibilité

L'agent est compatible avec Python 3.8+ et utilise des bibliothèques standards comme:
- `requests` pour les communications HTTP
- `psutil` pour accéder aux métriques système
- `pyyaml` pour la gestion de la configuration

## Version NodeJS

Une version équivalente de l'agent en NodeJS (N-2.0.0-Grizzly) est également disponible avec des fonctionnalités similaires mais adaptées à l'écosystème Node. 