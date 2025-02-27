import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from core.module_manager import ModuleManager
from core.web_server import WebServer
from core.http_client import HTTPClient
from core.utils import setup_logging, load_env_config, get_system_info

# Chargement de la configuration
load_dotenv()
config = load_env_config()
logger = setup_logging("luma-agent", config['log_level'])

# Création des instances principales
http_client = HTTPClient()
module_manager = ModuleManager()
web_server = WebServer()

# Création des répertoires nécessaires
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)
Path("modules").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

async def main():
    try:
        # Initialisation des modules
        logger.info("Starting LUMA Agent...")
        await module_manager.load_all_modules()

        # Démarrage du serveur web
        await web_server.start(
            host="0.0.0.0",
            port=config['port'],
            module_manager=module_manager,
            utils=__import__('core.utils', fromlist=['*']),
            http_client=http_client,
            config=config
        )

        logger.info(f"LUMA Agent running on http://0.0.0.0:{config['port']}")

        # Maintenir le serveur actif
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Nettoyage
        await module_manager.cleanup()
        await http_client.close()

if __name__ == "__main__":
    asyncio.run(main()) 