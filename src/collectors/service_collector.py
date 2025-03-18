#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collecteur de services pour l'agent LUMA
Récupère l'état des services Windows/Linux sur le système
"""

import os
import platform
import logging
import time
import subprocess
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ServiceCollector:
    """
    Collecteur pour les services système (Windows/Linux)
    Récupère l'état des services et les informations associées
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialisation du collecteur de services
        
        Args:
            config: Configuration du collecteur
        """
        self.enabled = config.get('enabled', False)
        self.interval = config.get('interval', 300)
        self.system = platform.system().lower()
        
        # Liste des services à surveiller
        # Si aucun service n'est spécifié ou si "*" est présent, tous les services sont surveillés
        self.services = config.get('services', ['*'])
        
        # Nombre maximum de services à surveiller
        self.max_services = config.get('max_services', 50)
        
        # Les services à toujours inclure même si max_services est atteint
        self.priority_services = config.get('priority_services', [])
        
        # Exclusions
        self.excludes = config.get('excludes', [])
        
        # Type de services à collecter (Windows uniquement)
        self.service_types = config.get('types', ['system', 'user'])
        
        logger.info(f"Collecteur de services initialisé (OS: {self.system})")
        
        # Vérifier si le système est supporté
        if self.system not in ['windows', 'linux']:
            logger.warning(f"Le système {self.system} n'est pas pris en charge pour la collecte de services")
            self.enabled = False
    
    def collect(self) -> Dict[str, Any]:
        """
        Récupère les informations sur les services
        
        Returns:
            Dict[str, Any]: Informations sur les services
        """
        if not self.enabled:
            logger.debug("Collecteur de services désactivé")
            return {}
        
        start_time = time.time()
        logger.debug("Collecte des informations sur les services...")
        
        try:
            if self.system == 'windows':
                services_info = self._collect_windows_services()
            elif self.system == 'linux':
                services_info = self._collect_linux_services()
            else:
                services_info = {}
            
            elapsed = time.time() - start_time
            logger.debug(f"Collecte des services terminée en {elapsed:.2f}s ({len(services_info.get('services', {}))} services)")
            
            return services_info
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des services: {e}")
            return {
                "error": str(e),
                "count": 0,
                "running": 0,
                "stopped": 0,
                "services": {}
            }
    
    def _collect_windows_services(self) -> Dict[str, Any]:
        """
        Collecte les informations sur les services Windows
        
        Returns:
            Dict[str, Any]: Informations sur les services
        """
        try:
            import wmi
            w = wmi.WMI()
            
            services_data = {}
            running_count = 0
            stopped_count = 0
            total_count = 0
            
            # Récupérer tous les services du système
            all_services = w.Win32_Service()
            
            # Filtrer les services en fonction de la configuration
            filtered_services = []
            
            # Si "*" est présent, on prend tous les services
            if "*" in self.services:
                filtered_services = all_services
            else:
                # Sinon, on filtre selon les noms spécifiés
                for service in all_services:
                    if service.Name in self.services or service.DisplayName in self.services:
                        filtered_services.append(service)
            
            # Appliquer les exclusions
            filtered_services = [s for s in filtered_services if s.Name not in self.excludes and s.DisplayName not in self.excludes]
            
            # Limiter le nombre de services si nécessaire
            if len(filtered_services) > self.max_services:
                # D'abord ajouter les services prioritaires
                priority_services = [s for s in filtered_services if s.Name in self.priority_services or s.DisplayName in self.priority_services]
                other_services = [s for s in filtered_services if s.Name not in self.priority_services and s.DisplayName not in self.priority_services]
                
                # Puis compléter avec les autres services jusqu'à atteindre max_services
                remaining_slots = self.max_services - len(priority_services)
                if remaining_slots > 0:
                    filtered_services = priority_services + other_services[:remaining_slots]
                else:
                    filtered_services = priority_services[:self.max_services]
                
                logger.warning(f"Nombre de services limité à {self.max_services} (sur {len(all_services)} total)")
            
            # Traiter les services filtrés
            for service in filtered_services:
                total_count += 1
                
                # Récupérer l'état du service
                if service.State == "Running":
                    status = "running"
                    running_count += 1
                else:
                    status = "stopped"
                    stopped_count += 1
                
                # Récupérer d'autres informations
                services_data[service.Name] = {
                    "name": service.Name,
                    "display_name": service.DisplayName,
                    "status": status,
                    "pid": service.ProcessId if service.ProcessId else None,
                    "start_mode": service.StartMode,
                    "path": service.PathName,
                    "account": service.StartName,
                    "description": service.Description
                }
            
            return {
                "count": total_count,
                "running": running_count,
                "stopped": stopped_count,
                "services": services_data
            }
            
        except ImportError:
            logger.error("Module wmi non disponible, impossible de collecter les services Windows")
            # Essayer avec SC.exe comme fallback
            return self._collect_windows_services_sc()
    
    def _collect_windows_services_sc(self) -> Dict[str, Any]:
        """
        Collecte les informations sur les services Windows en utilisant sc.exe
        
        Returns:
            Dict[str, Any]: Informations sur les services
        """
        try:
            services_data = {}
            running_count = 0
            stopped_count = 0
            total_count = 0
            
            # Récupérer la liste des services
            proc = subprocess.run(["sc", "query", "state=all"], capture_output=True, text=True, check=True)
            output = proc.stdout
            
            # Analyser la sortie de sc.exe
            current_service = None
            service_info = {}
            
            for line in output.splitlines():
                line = line.strip()
                
                if line.startswith("SERVICE_NAME:"):
                    # Nouveau service trouvé
                    if current_service:
                        # Sauvegarder le service précédent
                        services_data[current_service] = service_info
                        total_count += 1
                        
                        if service_info.get("status") == "running":
                            running_count += 1
                        else:
                            stopped_count += 1
                    
                    # Initialiser le nouveau service
                    current_service = line.split(":", 1)[1].strip()
                    service_info = {"name": current_service}
                
                elif line.startswith("DISPLAY_NAME:"):
                    service_info["display_name"] = line.split(":", 1)[1].strip()
                
                elif line.startswith("STATE"):
                    if "RUNNING" in line:
                        service_info["status"] = "running"
                    else:
                        service_info["status"] = "stopped"
                
                elif line.startswith("PID"):
                    try:
                        pid = int(line.split(":", 1)[1].strip())
                        service_info["pid"] = pid
                    except:
                        service_info["pid"] = None
            
            # Ajouter le dernier service
            if current_service:
                services_data[current_service] = service_info
                total_count += 1
                
                if service_info.get("status") == "running":
                    running_count += 1
                else:
                    stopped_count += 1
            
            # Appliquer les filtres
            if "*" not in self.services:
                services_data = {name: info for name, info in services_data.items() 
                                if name in self.services or info.get("display_name") in self.services}
            
            # Appliquer les exclusions
            for exclude in self.excludes:
                if exclude in services_data:
                    del services_data[exclude]
            
            # Limiter le nombre de services si nécessaire
            if len(services_data) > self.max_services:
                # D'abord ajouter les services prioritaires
                priority_services = {name: info for name, info in services_data.items() 
                                    if name in self.priority_services or info.get("display_name") in self.priority_services}
                
                # Puis compléter avec les autres services jusqu'à atteindre max_services
                remaining_slots = self.max_services - len(priority_services)
                
                if remaining_slots > 0:
                    other_services = {name: info for name, info in services_data.items() 
                                    if name not in self.priority_services and info.get("display_name") not in self.priority_services}
                    
                    # Convertir en liste pour pouvoir découper
                    other_service_items = list(other_services.items())[:remaining_slots]
                    
                    # Recréer le dictionnaire final
                    services_data = {**priority_services, **dict(other_service_items)}
                else:
                    # Si pas de place restante, ne garder que les services prioritaires
                    services_data = priority_services
                
                logger.warning(f"Nombre de services limité à {self.max_services}")
            
            return {
                "count": len(services_data),
                "running": sum(1 for info in services_data.values() if info.get("status") == "running"),
                "stopped": sum(1 for info in services_data.values() if info.get("status") != "running"),
                "services": services_data
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des services Windows via sc.exe: {e}")
            return {
                "error": str(e),
                "count": 0,
                "running": 0,
                "stopped": 0,
                "services": {}
            }
    
    def _collect_linux_services(self) -> Dict[str, Any]:
        """
        Collecte les informations sur les services Linux (systemd/init)
        
        Returns:
            Dict[str, Any]: Informations sur les services
        """
        # Déterminer si c'est systemd ou un autre init system
        if os.path.exists("/bin/systemctl") or os.path.exists("/usr/bin/systemctl"):
            return self._collect_linux_services_systemd()
        else:
            return self._collect_linux_services_sysvinit()
    
    def _collect_linux_services_systemd(self) -> Dict[str, Any]:
        """
        Collecte les informations sur les services Linux via systemd
        
        Returns:
            Dict[str, Any]: Informations sur les services
        """
        try:
            services_data = {}
            running_count = 0
            stopped_count = 0
            total_count = 0
            
            # Récupérer tous les services (unités de type .service)
            proc = subprocess.run(["systemctl", "list-units", "--type=service", "--all", "--no-legend"], 
                                capture_output=True, text=True, check=True)
            output = proc.stdout
            
            # Analyser la sortie de systemctl
            for line in output.splitlines():
                parts = line.strip().split(None, 4)
                if len(parts) < 4:
                    continue
                
                service_name = parts[0]
                load_state = parts[1]
                active_state = parts[2]
                sub_state = parts[3]
                description = parts[4] if len(parts) > 4 else ""
                
                # Ignorer les services non chargés ou masqués
                if load_state not in ["loaded"]:
                    continue
                
                # Vérifier l'état du service
                if active_state == "active":
                    status = "running"
                    running_count += 1
                else:
                    status = "stopped"
                    stopped_count += 1
                
                # Nettoyage du nom du service
                if service_name.endswith(".service"):
                    service_name = service_name[:-8]  # Enlever le .service
                
                # Appliquer les filtres
                if "*" not in self.services and service_name not in self.services:
                    continue
                
                # Appliquer les exclusions
                if service_name in self.excludes:
                    continue
                
                # Récupérer le PID du service s'il est en cours d'exécution
                pid = None
                if status == "running":
                    try:
                        pid_proc = subprocess.run(["systemctl", "show", "--property=MainPID", service_name],
                                               capture_output=True, text=True, check=True)
                        pid_output = pid_proc.stdout.strip()
                        pid = int(pid_output.split("=")[1]) if "=" in pid_output else None
                        
                        # Si PID est 0, c'est qu'il n'y a pas de processus principal
                        if pid == 0:
                            pid = None
                    except:
                        pid = None
                
                # Récupérer des informations supplémentaires
                unit_file_proc = subprocess.run(["systemctl", "show", "--property=UnitFileState", service_name],
                                             capture_output=True, text=True, check=True)
                unit_file_state = unit_file_proc.stdout.strip().split("=")[1] if "=" in unit_file_proc.stdout else "unknown"
                
                services_data[service_name] = {
                    "name": service_name,
                    "display_name": service_name,
                    "status": status,
                    "pid": pid,
                    "start_mode": unit_file_state,
                    "description": description,
                    "active_state": active_state,
                    "sub_state": sub_state
                }
                
                total_count += 1
                
                # Limiter le nombre de services si nécessaire
                if total_count >= self.max_services and "*" in self.services:
                    logger.warning(f"Nombre de services limité à {self.max_services}")
                    break
            
            return {
                "count": total_count,
                "running": running_count,
                "stopped": stopped_count,
                "services": services_data
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des services Linux (systemd): {e}")
            return {
                "error": str(e),
                "count": 0,
                "running": 0,
                "stopped": 0,
                "services": {}
            }
    
    def _collect_linux_services_sysvinit(self) -> Dict[str, Any]:
        """
        Collecte les informations sur les services Linux via SysV init
        
        Returns:
            Dict[str, Any]: Informations sur les services
        """
        try:
            services_data = {}
            running_count = 0
            stopped_count = 0
            total_count = 0
            
            # Récupérer tous les scripts init
            init_dir = "/etc/init.d"
            
            if not os.path.exists(init_dir):
                logger.error(f"Répertoire {init_dir} introuvable, impossible de collecter les services SysV init")
                return {
                    "error": f"Répertoire {init_dir} introuvable",
                    "count": 0,
                    "running": 0,
                    "stopped": 0,
                    "services": {}
                }
            
            # Lister tous les scripts init
            init_scripts = []
            for filename in os.listdir(init_dir):
                filepath = os.path.join(init_dir, filename)
                if os.path.isfile(filepath) and os.access(filepath, os.X_OK):
                    init_scripts.append(filename)
            
            # Filtrer les scripts si nécessaire
            if "*" not in self.services:
                init_scripts = [s for s in init_scripts if s in self.services]
            
            # Appliquer les exclusions
            init_scripts = [s for s in init_scripts if s not in self.excludes]
            
            # Limiter le nombre de services si nécessaire
            if len(init_scripts) > self.max_services:
                # Prioriser les services spécifiés
                priority_scripts = [s for s in init_scripts if s in self.priority_services]
                other_scripts = [s for s in init_scripts if s not in self.priority_services]
                
                remaining_slots = self.max_services - len(priority_scripts)
                if remaining_slots > 0:
                    init_scripts = priority_scripts + other_scripts[:remaining_slots]
                else:
                    init_scripts = priority_scripts[:self.max_services]
                
                logger.warning(f"Nombre de services limité à {self.max_services}")
            
            # Vérifier l'état de chaque service
            for script in init_scripts:
                try:
                    # Vérifier si le service est en cours d'exécution
                    status_proc = subprocess.run([os.path.join(init_dir, script), "status"],
                                             capture_output=True, text=True)
                    
                    # La plupart des scripts retournent 0 pour "en cours d'exécution"
                    if status_proc.returncode == 0:
                        status = "running"
                        running_count += 1
                    else:
                        status = "stopped"
                        stopped_count += 1
                    
                    # Essayer de trouver le PID si le service est en cours d'exécution
                    pid = None
                    if status == "running":
                        # Essayer de trouver le PID dans la sortie (varie selon les distributions)
                        status_output = status_proc.stdout.lower()
                        if "pid" in status_output:
                            # Essayer d'extraire le PID des formats courants
                            import re
                            pid_match = re.search(r"pid[^0-9]*([0-9]+)", status_output)
                            if pid_match:
                                pid = int(pid_match.group(1))
                    
                    services_data[script] = {
                        "name": script,
                        "display_name": script,
                        "status": status,
                        "pid": pid,
                        "start_mode": "unknown"  # SysV init ne stocke pas cette information
                    }
                    
                    total_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la vérification du service {script}: {e}")
            
            return {
                "count": total_count,
                "running": running_count,
                "stopped": stopped_count,
                "services": services_data
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des services Linux (SysV init): {e}")
            return {
                "error": str(e),
                "count": 0,
                "running": 0,
                "stopped": 0,
                "services": {}
            } 