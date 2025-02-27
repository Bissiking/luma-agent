import json
from aiohttp import web
from typing import Any, Callable, Dict, Optional
from pathlib import Path
import os
from dotenv import load_dotenv, set_key

class WebServer:
    def __init__(self):
        self.app = web.Application()
        self.routes = web.RouteTableDef()
        
        # Ajouter le middleware de gestion d'erreurs
        @web.middleware
        async def error_middleware(request, handler):
            try:
                return await handler(request)
            except web.HTTPException as ex:
                return web.json_response({
                    'error': ex.reason
                }, status=ex.status)
            except Exception as ex:
                return web.json_response({
                    'error': str(ex)
                }, status=500)

        # Configurer l'application avec le middleware
        self.app = web.Application(middlewares=[error_middleware])
        self._setup_routes()

    def _setup_routes(self):
        """Configure les routes de base"""
        
        @self.routes.get('/')
        async def index(request):
            """Page d'accueil"""
            return await self.render_template('index.html', {
                'title': 'LUMA Agent Dashboard'
            })

        @self.routes.get('/config')
        async def config_page(request):
            """Page de configuration"""
            return await self.render_template('config.html', {
                'title': 'Configuration LUMA Agent',
                'config': self.get_current_config()
            })

        @self.routes.get('/api/config')
        async def get_config(request):
            """Récupère la configuration actuelle"""
            return web.json_response(self.get_current_config())

        @self.routes.post('/api/config')
        async def update_config(request):
            """Met à jour la configuration"""
            try:
                data = await request.json()
                self.update_env_file(data)
                return web.json_response({
                    'status': 'success',
                    'message': 'Configuration mise à jour avec succès'
                })
            except Exception as e:
                return web.json_response({
                    'status': 'error',
                    'message': str(e)
                }, status=500)

        @self.routes.get('/api/system')
        async def get_system(request):
            """Informations système"""
            system_info = await request.app['utils'].get_system_info()
            return web.json_response(system_info)

        @self.routes.get('/api/modules')
        async def get_modules(request):
            """Liste des modules"""
            modules = request.app['module_manager'].get_module_status()
            return web.json_response(modules)

        @self.routes.post('/api/modules/{name}/toggle')
        async def toggle_module(request):
            """Active/désactive un module"""
            name = request.match_info['name']
            module = request.app['module_manager'].get_module(name)
            
            if not module:
                raise web.HTTPNotFound(text=f"Module {name} not found")
            
            module.enabled = not module.enabled
            return web.json_response({
                'status': 'success',
                'enabled': module.enabled
            })

        @self.routes.post('/api/modules/{name}/config')
        async def update_module_config(request):
            """Met à jour la configuration d'un module"""
            name = request.match_info['name']
            module = request.app['module_manager'].get_module(name)
            
            if not module:
                raise web.HTTPNotFound(text=f"Module {name} not found")
            
            data = await request.json()
            await module.initialize(data)
            return web.json_response({'status': 'success'})

        # Servir les fichiers statiques
        @self.routes.get('/static/{filename}')
        async def static_files(request):
            filename = request.match_info['filename']
            static_path = Path('static') / filename
            if not static_path.exists():
                raise web.HTTPNotFound()
            return web.FileResponse(static_path)

        self.app.add_routes(self.routes)

    def get_current_config(self) -> Dict[str, str]:
        """Récupère la configuration actuelle depuis le fichier .env"""
        load_dotenv()  # Recharge le fichier .env
        config = {}
        # Liste des variables de configuration à exposer
        env_vars = [
            'LUMA_TOKEN',
            'LUMA_API_URL',
            'DISCORD_WEBHOOK_URL',
            'LOG_LEVEL',
            'WEB_HOST',
            'WEB_PORT'
        ]
        for var in env_vars:
            config[var] = os.getenv(var, '')
        return config

    def update_env_file(self, config: Dict[str, str]):
        """Met à jour le fichier .env avec les nouvelles valeurs"""
        env_path = Path('.env')
        
        # Crée le fichier .env s'il n'existe pas
        if not env_path.exists():
            env_path.touch()
        
        # Met à jour chaque variable dans le fichier .env
        for key, value in config.items():
            if value is not None:  # Ne met à jour que les valeurs non nulles
                set_key('.env', key, value)

    async def render_template(self, template_name: str, context: Dict[str, Any]) -> web.Response:
        """Rendu simple des templates"""
        template_path = Path('templates') / template_name
        if not template_path.exists():
            raise web.HTTPNotFound(text=f"Template {template_name} not found")

        with open(template_path, 'r') as f:
            content = f.read()

        # Remplacement simple des variables
        for key, value in context.items():
            content = content.replace('{{' + key + '}}', str(value))

        return web.Response(
            text=content,
            content_type='text/html'
        )

    def add_route(self, method: str, path: str, handler: Callable):
        """Ajoute une route personnalisée"""
        self.routes.route(method, path)(handler)

    async def start(self, host: str, port: int, **context):
        """Démarre le serveur"""
        # Ajouter le contexte à l'application
        for key, value in context.items():
            self.app[key] = value

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

    def get_app(self) -> web.Application:
        """Retourne l'application web"""
        return self.app 