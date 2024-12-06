const { getBasicMetrics } = require('./utils/metrics');
const { getServicesStatus } = require('./utils/services');
const { sendMetricsToLuma } = require('./api/client');
const { log } = require('./utils/logger');
var Monitor = null;

async function startScheduler(config) {
    setInterval(async () => {
        try {
            log('info', 'Collecte des métriques...');

            // Récupération de la liste des services
            if (config.monitored_services && config.monitored_services.trim() !== "") {
                Monitor = JSON.parse(config.monitored_services);
            }
            console.log(Monitor);

            // Collecte des métriques de base
            const basicMetrics = getBasicMetrics();

            // Collecte des statuts des services (attendre la résolution)
            const serviceMetrics = await getServicesStatus(Monitor || []);

            // Agrégation des métriques
            const metrics = {
                ...basicMetrics,
                services: serviceMetrics,
            };

            log('info', `Métriques collectées : ${JSON.stringify(metrics)}`);

            // Envoi des métriques
            await sendMetricsToLuma(metrics);
        } catch (error) {
            log('error', `Erreur lors de la collecte des métriques : ${error.message}`);
        }
    }, config.send_interval * 1000);
}

module.exports = { startScheduler };
