require('dotenv').config();
const axios = require('axios');
const { log } = require('../utils/logger');

const agentUuid = process.env.AGENT_UUID;
const agentToken = process.env.AGENT_TOKEN;
const apiUrl = process.env.API_URL;

async function fetchAgentConfig(config) {
    try {
        const response = await axios.get(`${apiUrl}/api/agent/config`, {
            headers: {
                'X-Agent-UUID': agentUuid,
                'X-Agent-Token': agentToken,
            }
        });

        if (response.data.success) {
            log('info', 'Configuration récupérée avec succès.');
            return response.data.config;
        } else {
            log('error', `Echec lors de la récupération de la configuration : ${response.data}`);
            return null;
        }
    } catch (error) {
        log('error', `Erreur lors de la récupération de la configuration : ${error}`);
        return null;
    }
}

/**
 * Envoie les métriques système à LUMA.
 * @param {Object} metrics - Les métriques collectées (CPU, RAM, etc.).
 */
function sendMetricsToLuma(metrics) {

    // Configuration des en-têtes pour l'authentification
    const headers = {
        'Content-Type': 'application/json',
        'X-Agent-UUID': agentUuid,
        'X-Agent-Token': agentToken,
    };

    // Envoi des métriques
    axios.post(`${apiUrl}/api/agent/metrics`, metrics, { headers })
        .then((response) => {
            console.log('//////// SEND DATA /////////');
            console.log(response.data);
        })
        .catch((error) => {
            console.error(`Erreur lors de l'envoi des métriques : ${error.message}`);
        });
}


module.exports = { fetchAgentConfig, sendMetricsToLuma };
