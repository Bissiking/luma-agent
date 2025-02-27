import os
import sys
import psutil
import logging
import platform
from typing import Dict, Any
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """Configure logging for the application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = RotatingFileHandler(
        log_dir / f"{name}.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

async def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
        },
        'resources': {
            'cpu_percent': cpu_percent,
            'memory_total': memory.total,
            'memory_available': memory.available,
            'memory_percent': memory.percent,
            'disk_total': disk.total,
            'disk_free': disk.free,
            'disk_percent': disk.percent,
        },
        'process': {
            'pid': os.getpid(),
            'memory_usage': psutil.Process().memory_info().rss,
            'cpu_usage': psutil.Process().cpu_percent(),
        },
        'network': {
            'interfaces': list(psutil.net_if_addrs().keys()),
            'connections': len(psutil.net_connections()),
        },
        'container': is_running_in_container()
    }

def is_running_in_container() -> bool:
    """Check if the process is running in a container"""
    # Check for Docker
    if os.path.exists('/.dockerenv'):
        return True
    
    # Check for Kubernetes
    if os.path.exists('/var/run/secrets/kubernetes.io'):
        return True
    
    # Check cgroup on Linux
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return any(['docker' in line or 'kubepods' in line for line in f])
    except:
        pass
    
    return False

def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    return {
        'agent_name': os.getenv('AGENT_NAME', 'luma-agent'),
        'port': int(os.getenv('PORT', 8000)),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'env': os.getenv('ENV', 'development'),
        'luma_api_url': os.getenv('LUMA_API_URL'),
        'luma_api_key': os.getenv('LUMA_API_KEY'),
        'secret_key': os.getenv('SECRET_KEY'),
        'jwt_secret': os.getenv('JWT_SECRET'),
        'database_url': os.getenv('DATABASE_URL'),
        'discord_webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
    } 