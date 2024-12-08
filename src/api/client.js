require('dotenv').config();
const axios = require('axios');
const { log } = require('../utils/logger');

const agentUuid = process.env.AGENT_UUID;
const agentToken = process.env.AGENT_TOKEN;
const apiUrl = process.env.API_URL;
const version = require('../../package.json');

async function fetchAgentConfig(config) {
    try {
        // Effectuer une requête GET pour récupérer la configuration de l'agent
        const response = await axios.get(`${apiUrl}/api/agent/config`, {
            headers: {
                'X-Agent-UUID': agentUuid,
                'X-Agent-Token': agentToken,
                'X-Agent-Version': version.version
            }
        });

        // Vérification du succès de la réponse
        if (response.data.success) {
            log('info', 'Configuration récupérée avec succès.');
            return response.data.config;
        } else {
            log(
                'error',
                `Échec lors de la récupération de la configuration : ${response.data.message || 'Réponse inattendue.'}`
            );
            return null;
        }
    } catch (error) {
        // Vérifier si l'erreur provient de la réponse ou de la requête
        if (error.response) {
            // Erreur côté serveur (exemple : 401, 404, etc.)
            log(
                'error',
                `Erreur côté serveur lors de la récupération de la configuration : ${error.response.data.message || error.response.statusText}`
            );
        } else if (error.request) {
            // Aucun retour du serveur (exemple : problème réseau)
            log('error', 'Aucune réponse du serveur. Vérifiez votre connexion ou le point d\'accès API.');
        } else {
            // Erreur lors de la configuration de la requête
            log('error', `Erreur lors de la configuration de la requête : ${error.message}`);
        }

        // Retourner `null` en cas d'échec
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
