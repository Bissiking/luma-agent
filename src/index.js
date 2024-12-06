const config = require('./config');
const { startScheduler } = require('./scheduler');
const { fetchAgentConfig } = require('./api/client');
const { log } = require('./utils/logger');

(async function init() {
    log('info', 'Démarrage de l\'Agent-light...');

    // Récupérer la configuration depuis LUMA    
    const remoteConfig = await fetchAgentConfig(config);

    if (!remoteConfig) {
        log('error', 'Impossible de récupérer la configuration. Arrêt de l\'agent.');
        process.exit(1);
    }

    // Fusionner la configuration locale et distante
    const finalConfig = { ...config, ...remoteConfig };

    // Démarrer l'agent
    startScheduler(finalConfig);
})();
