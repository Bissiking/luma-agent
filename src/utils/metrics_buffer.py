#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion du tampon de métriques
Permet de stocker temporairement les métriques avant envoi à LUMA
"""

import os
import json
import time
import logging
import threading
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MetricsBuffer:
    """
    Gère le stockage temporaire des métriques dans un fichier JSON
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le tampon de métriques
        
        Args:
            config: Configuration du tampon
        """
        self.config = config
        
        # Chemin du fichier de stockage
        self.buffer_file = config.get('file_path', 'data/metrics_buffer.json')
        
        # Taille maximale du tampon (nombre d'entrées)
        self.max_size = config.get('max_size', 1000)
        
        # Durée de rétention maximale (en secondes)
        self.retention_period = config.get('retention_period', 86400)  # 24h par défaut
        
        # Intervalle entre les tentatives d'envoi (en secondes)
        self.flush_interval = config.get('flush_interval', 300)  # 5min par défaut
        
        # Verrou pour les accès concurrents
        self.lock = threading.Lock()
        
        # Dernière tentative d'envoi
        self.last_flush = 0
        
        # S'assurer que le répertoire existe
        os.makedirs(os.path.dirname(os.path.abspath(self.buffer_file)), exist_ok=True)
        
        # Charger le tampon existant ou créer un nouveau
        self._load_or_create_buffer()
        
        logger.info(f"Tampon de métriques initialisé (stockage: {self.buffer_file})")
        logger.info(f"Configuration: max_size={self.max_size}, retention={self.retention_period}s, flush_interval={self.flush_interval}s")
    
    def _load_or_create_buffer(self) -> None:
        """
        Charge le tampon existant ou crée un nouveau tampon vide
        """
        with self.lock:
            try:
                if os.path.exists(self.buffer_file) and os.path.getsize(self.buffer_file) > 0:
                    with open(self.buffer_file, 'r') as f:
                        self.buffer = json.load(f)
                        logger.info(f"Tampon de métriques chargé: {len(self.buffer.get('metrics', []))} entrées")
                else:
                    self.buffer = {
                        'metrics': [],
                        'last_update': int(time.time())
                    }
                    self._save_buffer()
                    logger.info("Nouveau tampon de métriques créé")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du tampon: {e}")
                # Créer un nouveau tampon en cas d'erreur
                self.buffer = {
                    'metrics': [],
                    'last_update': int(time.time())
                }
                self._save_buffer()
    
    def _save_buffer(self) -> None:
        """
        Sauvegarde le tampon dans le fichier
        """
        try:
            with open(self.buffer_file, 'w') as f:
                json.dump(self.buffer, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du tampon: {e}")
    
    def add_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Ajoute des métriques au tampon
        
        Args:
            metrics: Métriques à ajouter
        """
        with self.lock:
            # Ajouter les métriques avec un horodatage
            entry = {
                'timestamp': int(time.time()),
                'data': metrics
            }
            
            self.buffer['metrics'].append(entry)
            self.buffer['last_update'] = int(time.time())
            
            # Limiter la taille du tampon
            if len(self.buffer['metrics']) > self.max_size:
                # Supprimer les entrées les plus anciennes
                excess = len(self.buffer['metrics']) - self.max_size
                self.buffer['metrics'] = self.buffer['metrics'][excess:]
                logger.warning(f"Tampon plein, {excess} anciennes entrées supprimées")
            
            # Sauvegarder le tampon
            self._save_buffer()
            
            logger.debug(f"Métriques ajoutées au tampon, {len(self.buffer['metrics'])} entrées au total")
    
    def get_metrics_to_send(self, max_batch_size: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les métriques à envoyer
        
        Args:
            max_batch_size: Nombre maximum d'entrées à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des métriques à envoyer
        """
        with self.lock:
            # Limiter le nombre d'entrées
            return self.buffer['metrics'][:max_batch_size]
    
    def remove_sent_metrics(self, count: int) -> None:
        """
        Supprime les métriques envoyées avec succès
        
        Args:
            count: Nombre d'entrées à supprimer
        """
        with self.lock:
            if count > 0:
                self.buffer['metrics'] = self.buffer['metrics'][count:]
                self.buffer['last_update'] = int(time.time())
                self._save_buffer()
                logger.info(f"{count} métriques supprimées du tampon, {len(self.buffer['metrics'])} restantes")
    
    def clean_expired_metrics(self) -> int:
        """
        Supprime les métriques expirées (plus anciennes que la période de rétention)
        
        Returns:
            int: Nombre de métriques supprimées
        """
        with self.lock:
            now = int(time.time())
            expiration_threshold = now - self.retention_period
            
            original_count = len(self.buffer['metrics'])
            
            # Filtrer les métriques non expirées
            self.buffer['metrics'] = [
                entry for entry in self.buffer['metrics']
                if entry['timestamp'] >= expiration_threshold
            ]
            
            removed_count = original_count - len(self.buffer['metrics'])
            
            if removed_count > 0:
                self.buffer['last_update'] = now
                self._save_buffer()
                logger.info(f"{removed_count} métriques expirées supprimées du tampon")
            
            return removed_count
    
    def should_flush(self) -> bool:
        """
        Vérifie si le tampon doit être vidé
        
        Returns:
            bool: True si le tampon doit être vidé
        """
        now = time.time()
        return (now - self.last_flush >= self.flush_interval) and len(self.buffer['metrics']) > 0
    
    def set_last_flush(self) -> None:
        """
        Met à jour la date de la dernière tentative d'envoi
        """
        self.last_flush = time.time()
    
    def get_buffer_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur le tampon
        
        Returns:
            Dict[str, Any]: Statistiques sur le tampon
        """
        with self.lock:
            return {
                'size': len(self.buffer['metrics']),
                'max_size': self.max_size,
                'usage_percent': (len(self.buffer['metrics']) / self.max_size) * 100 if self.max_size > 0 else 0,
                'last_update': self.buffer['last_update'],
                'file_path': self.buffer_file
            } 