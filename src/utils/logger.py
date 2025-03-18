import os
import logging
import logging.handlers
from typing import Dict, Any, Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure le système de logging
    
    Args:
        log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Chemin vers le fichier de log (si None, pas de log dans un fichier)
        console: Si True, affiche également les logs dans la console
        max_file_size: Taille maximale du fichier de log avant rotation (en octets)
        backup_count: Nombre de fichiers de backup à conserver
        
    Returns:
        logging.Logger: Logger configuré
    """
    # Convertir le niveau de log en constante logging
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Créer le logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Format des logs
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Supprimer les handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Ajouter un handler pour la console si demandé
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
    
    # Ajouter un handler pour le fichier si spécifié
    if log_file:
        try:
            # Créer le répertoire si nécessaire
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Utiliser RotatingFileHandler pour la rotation des logs
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            file_handler.setFormatter(log_format)
            logger.addHandler(file_handler)
            
            logging.info(f"Logs will be written to {log_file}")
        except Exception as e:
            logging.error(f"Failed to set up file logging: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtient un logger nommé
    
    Args:
        name: Nom du logger
        
    Returns:
        logging.Logger: Logger nommé
    """
    return logging.getLogger(name) 