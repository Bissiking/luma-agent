# Proposition de suivi et actions automatisées

Ce document décrit l'architecture proposée pour détecter des événements (ex. fichiers volumineux), générer des propositions de commandes, et gérer leur exécution validée par l'utilisateur.

## 1. Contexte
- Besoin : surveiller le système de fichiers, identifier les fichiers volumineux ou anciennes données, et proposer automatiquement des actions (déplacer, supprimer, archiver, etc.).
- Mode de fonctionnement : semi-automatique (propositions à valider) ou automatique (exécution directe).

## 2. Modules principaux

### 2.1 FileScanner
- Parcourt périodiquement les répertoires ciblés.
- Repère les fichiers dépassant un seuil configurable (ex. > 1 Go).
- Émet un événement `{ path, size, timestamp }` pour chaque fichier détecté.

### 2.2 ProposalManager (CommandFactory)
- Reçoit les événements de `FileScanner`.
- Applique des règles métier (ex. « si fichier > 5 Go et > 30 jours → proposer déplacement »).
- Génère une proposition de commande :
  ```json
  {
    "id": "uuid",
    "action": "move",
    "src": "/downloads/fichier.mp4",
    "dst": "/archive/",
    "label": "Déplacer fichier volumineux"
  }
  ```
- Sauvegarde temporaire en mémoire ou en base (statut `pending`).

### 2.3 API & Interface utilisateur
- **Endpoints REST** (FastAPI / Flask) :
  - `GET /proposals` : liste des propositions en attente.
  - `POST /proposals/{id}/confirm` : valider et exécuter.
  - `POST /proposals/{id}/reject` : ignorer.
- **Notifications temps réel** : WebSocket / SSE pour push des nouvelles propositions.

### 2.4 ExecutionEngine
- Exécute la commande validée :
  - Opérations système (shutil.move, os.remove, etc.).
  - Appels API externes (ex. qBittorrent) si nécessaire.
- Met à jour le statut en base (`done`, `failed`).

## 3. Schéma de stockage
- Table `proposals` :
  - `id` (UUID agent)
  - `payload` (JSON)
  - `status` (`pending`, `done`, `rejected`, `failed`)
  - `created_at`, `updated_at`
- Table `events` (optionnel) pour historiser tous les scans.

## 4. Historique & Audit
- Chaque action (proposition, validation, exécution) est loggée.
- Permet de rejouer ou d'analyser les décisions prises.

## 5. Évolutions possibles
- Moteur de règles avancé ou basé sur un DSL.
- Module d'alerting / notifications (email, Slack, etc.).
- Scoring/ML pour prioriser les commandes les plus pertinentes.

---
*Fin de la proposition de fonction.* 