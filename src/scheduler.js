const { getBasicMetrics } = require('./utils/metrics');
const { getAllServicesWithStatus } = require('./utils/services');
const { checkDockerContainers, isDockerAvailable } = require('./utils/docker');
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
            const basicMetrics = await getBasicMetrics();

            // Collecte des statuts des services
            const serviceMetrics = await getAllServicesWithStatus(Monitor || []);

            // Vérification de Docker et collecte des conteneurs
            const dockerMetrics = await checkDockerContainers();

            // Agrégation des métriques
            const metrics = {
                ...basicMetrics,
                services: serviceMetrics,
                docker: dockerMetrics,
            };

            log('info', `Métriques collectées : ${JSON.stringify(metrics)}`);

            // Envoi des métriques
            sendMetricsToLuma(metrics);
        } catch (error) {
            log('error', `Erreur lors de la collecte des métriques : ${error.message}`);
        }
    }, config.send_interval * 1000);
}

module.exports = { startScheduler };
