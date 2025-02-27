import os
import yaml
import importlib.util
from typing import Dict, List, Optional, Type
from pathlib import Path
from core.base_module import BaseModule
from core.utils import get_logger

class ModuleManager:
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
        self.logger = get_logger("module_manager")
        self.modules_dir = Path("modules")
        self.modules_dir.mkdir(exist_ok=True)

    async def load_all_modules(self):
        """Load all modules from the modules directory"""
        self.logger.info("Loading all modules...")
        
        for module_dir in self.modules_dir.iterdir():
            if not module_dir.is_dir():
                continue
                
            try:
                await self.load_module(module_dir.name)
            except Exception as e:
                self.logger.error(f"Failed to load module {module_dir.name}: {e}")

    async def load_module(self, module_name: str) -> bool:
        """Load a specific module"""
        if module_name in self.modules:
            self.logger.warning(f"Module {module_name} is already loaded")
            return False

        module_path = self.modules_dir / module_name
        if not module_path.is_dir():
            self.logger.error(f"Module directory {module_name} not found")
            return False

        try:
            # Load module configuration
            config = self._load_module_config(module_path)
            if not config:
                return False

            # Import module class
            module_class = self._import_module_class(module_path)
            if not module_class:
                return False

            # Initialize module
            module_instance = module_class(self)
            await module_instance.initialize(config)
            
            self.modules[module_name] = module_instance
            self.logger.info(f"Module {module_name} loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error loading module {module_name}: {e}")
            return False

    async def unload_module(self, module_name: str) -> bool:
        """Unload a specific module"""
        if module_name not in self.modules:
            self.logger.warning(f"Module {module_name} is not loaded")
            return False

        try:
            module = self.modules[module_name]
            await module.cleanup()
            del self.modules[module_name]
            self.logger.info(f"Module {module_name} unloaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error unloading module {module_name}: {e}")
            return False

    def _load_module_config(self, module_path: Path) -> Optional[Dict]:
        """Load module configuration from yaml file"""
        config_path = module_path / "config.yaml"
        if not config_path.exists():
            self.logger.error(f"Configuration file not found for module at {module_path}")
            return None

        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading configuration for module at {module_path}: {e}")
            return None

    def _import_module_class(self, module_path: Path) -> Optional[Type[BaseModule]]:
        """Import module class from module directory"""
        try:
            # Import module
            spec = importlib.util.spec_from_file_location(
                "module", 
                module_path / "module.py"
            )
            if not spec or not spec.loader:
                raise ImportError("Failed to load module specification")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find the module class (subclass of BaseModule)
            for item in dir(module):
                obj = getattr(module, item)
                if (isinstance(obj, type) and 
                    issubclass(obj, BaseModule) and 
                    obj != BaseModule):
                    return obj

            raise ImportError("No BaseModule subclass found in module")

        except Exception as e:
            self.logger.error(f"Error importing module from {module_path}: {e}")
            return None

    def get_module(self, module_name: str) -> Optional[BaseModule]:
        """Get a loaded module by name"""
        return self.modules.get(module_name)

    def get_all_modules(self) -> List[BaseModule]:
        """Get all loaded modules"""
        return list(self.modules.values())

    def get_module_status(self) -> List[Dict]:
        """Get status of all modules"""
        return [module.get_status() for module in self.modules.values()] 