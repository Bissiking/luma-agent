# Catalogue des commandes

Ce document centralise les commandes disponibles et pertinentes pour l'application, classées par domaine.

| Domaine           | Commande                                                | Paramètres                                      | Description                                                    |
|-------------------|---------------------------------------------------------|-------------------------------------------------|----------------------------------------------------------------|
| Monitoring        | `check_cpu_usage(threshold_warning, threshold_critical)` | `threshold_warning: float`, `threshold_critical: float` | Vérifie l'utilisation CPU et déclenche des alertes si dépassement |
|                   | `check_ram_usage(threshold_warning, threshold_critical)` | `threshold_warning: float`, `threshold_critical: float` | Vérifie l'utilisation RAM et déclenche des alertes si dépassement |
|                   | `check_disk_usage(path, threshold_warning, threshold_critical)` | `path: str`, `threshold_warning: float`, `threshold_critical: float` | Vérifie l'espace disque et déclenche des alertes si dépassement |
|                   | `analyze_disk_usage(path)`                              | `path: str`                                     | Analyse les plus gros fichiers/répertoires pour identifier la source du problème |
|                   | `cleanup_old_files(path, days, size_threshold)`         | `path: str`, `days: int`, `size_threshold: int` | Nettoie les fichiers anciens et volumineux                     |
|                   | `notify_alert(level, message, metric, value)`           | `level: str`, `message: str`, `metric: str`, `value: float` | Envoie une notification d'alerte (email, webhook, etc.)        |
|                   | `auto_scale_resources(metric, value)`                   | `metric: str`, `value: float`                   | Ajuste automatiquement les ressources (CPU/RAM) si possible    |
|                   | `get_resource_history(metric, hours)`                   | `metric: str`, `hours: int`                     | Récupère l'historique d'utilisation d'une ressource            |
| OS                | `create_file(path, content)`                            | `path: str`, `content: str`                     | Crée un fichier avec le contenu spécifié                       |
|                   | `delete_file(path)`                                     | `path: str`                                     | Supprime un fichier                                            |
|                   | `move_file(src, dst)`                                   | `src: str`, `dst: str`                          | Déplace ou renomme un fichier                                  |
|                   | `compress(path, archive_path)`                          | `path: str`, `archive_path: str`                | Compresse un répertoire ou un fichier                          |
|                   | `set_permissions(path, mode)`                           | `path: str`, `mode: str`                        | Modifie les permissions Unix                                    |
|                   | `list_directory(path)`                                  | `path: str`                                     | Liste le contenu d'un répertoire                               |
|                   | `get_disk_usage(path)`                                  | `path: str`                                     | Retourne l'utilisation disque pour un chemin                   |
| Docker            | `restart_container(container)`                          | `container: str`                                | Redémarre un conteneur Docker                                   |
|                   | `scale_container(service, replicas)`                    | `service: str`, `replicas: int`                 | Ajuste le nombre de réplicas d'un service Docker               |
|                   | `set_container_limits(container, cpu, memory)`          | `container: str`, `cpu: float`, `memory: str`   | Définit les ressources CPU et mémoire pour un conteneur        |
|                   | `remove_container(container, force=False)`              | `container: str`, `force: bool`                 | Supprime un conteneur Docker (option --force)                  |
| qBittorrent       | `pause_torrent(hash)`                                   | `hash: str`                                     | Met en pause un torrent                                        |
|                   | `resume_torrent(hash)`                                  | `hash: str`                                     | Relance un torrent                                             |
|                   | `remove_torrent(hash, delete_files=False)`              | `hash: str`, `delete_files: bool`               | Supprime un torrent et/ou ses fichiers                         |
|                   | `set_torrent_category(hash, category)`                  | `hash: str`, `category: str`                    | Assigne une catégorie à un torrent                             |
| Base de données   | `backup_database(db_name, dst_path)`                    | `db_name: str`, `dst_path: str`                 | Effectue une sauvegarde de la base de données                  |
|                   | `restore_database(db_name, src_path)`                   | `db_name: str`, `src_path: str`                 | Restaure la base de données à partir d'une sauvegarde          |
| Réseau / Services | `restart_service(service_name)`                         | `service_name: str`                             | Redémarre un service système                                   |
|                   | `check_port(host, port)`                                | `host: str`, `port: int`                        | Vérifie la disponibilité d'un port réseau                      |
