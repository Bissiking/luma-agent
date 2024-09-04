const os = require('os');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
require('dotenv').config();

// Chemin du dossier pour stocker les fichiers d'état des notifications
const statusDir = path.join(__dirname, '../../data/ram');
if (!fs.existsSync(statusDir)) {
    fs.mkdirSync(statusDir, { recursive: true });
}

// Chemin du fichier JSON pour stocker les informations de la RAM
const ramDataPath = path.join(__dirname, '../../data/ram/ram.json');

// Chemin du fichier de configuration
const configPath = path.join(__dirname, './config.json');

// Modèle de configuration par défaut
const defaultConfig = {
    status: "stopped",
    ramCheckInterval: 15000 // Intervalle en millisecondes (60 secondes)
};

// Fonction pour envoyer une notification Discord
function sendDiscordNotification(webhookUrl, message) {
    if (!webhookUrl) {
        console.log('No Discord webhook URL defined, skipping notification.');
        return;
    }

    axios.post(webhookUrl, {
        content: message,
    }).then(() => {
        console.log('Discord notification sent:', message);
    }).catch(error => {
        console.error('Error sending Discord notification:', error.message);
    });
}

// Fonction pour vérifier et créer la configuration si nécessaire
function ensureConfigExists() {
    if (!fs.existsSync(configPath)) {
        console.log('Configuration file not found. Creating a default configuration...');
        fs.writeFileSync(configPath, JSON.stringify(defaultConfig, null, 2), 'utf-8');
    }
}

// Fonction pour lire la configuration
function readConfig() {
    ensureConfigExists(); // Assurer que le fichier de configuration existe
    const configData = fs.readFileSync(configPath, 'utf-8');
    return JSON.parse(configData);
}

// Fonction pour vérifier l'état de la RAM
function checkRAM() {
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const usedMemory = totalMemory - freeMemory;

    // Calcul du pourcentage d'utilisation de la RAM
    const usage = (usedMemory / totalMemory) * 100;

    // Lecture du fichier d'état pour la RAM
    const stateFilePath = path.join(__dirname, '../../data/ram/status.json');
    let state = {};
    if (fs.existsSync(stateFilePath)) {
        state = JSON.parse(fs.readFileSync(stateFilePath, 'utf-8'));
    }

    const webhookUrl = process.env.DISCORD_WEBHOOK_URL; // Assurez-vous de définir cette variable d'environnement

    // Vérifier les seuils et envoyer les notifications
    if (usage >= 99 && !state.blockage) {
        sendDiscordNotification(webhookUrl, `🚨 **CRITICAL**: Utilisation de la RAM à 100%! (${usage.toFixed(2)}%) | Blocage de la production ! Action immédiate requise !.`);
        state.blockage = true;
        state.critical95 = true;
        state.warning90 = true;
    } else if (usage >= 95 && !state.critical95) {
        sendDiscordNotification(webhookUrl, `⚠️ **Seuil d'alerte importante**: Utilisation de la RAM à plus de 95%! (${usage.toFixed(2)}%) | Action requise.`);
        state.critical95 = true;
        state.warning90 = true;
    } else if (usage >= 90 && !state.warning90) {
        sendDiscordNotification(webhookUrl, `⚠️ **Avertissement**: Utilisation de la RAM à plus de 90% (${usage.toFixed(2)}%) | Action demandée pour éviter le blocage.`);
        state.warning90 = true;
    }

    // Réinitialiser les états si le taux d'utilisation diminue
    if (usage < 90) {
        state.warning90 = false;
        state.critical95 = false;
        state.blockage = false;
    }

    // Sauvegarder l'état actuel de la RAM
    fs.writeFileSync(stateFilePath, JSON.stringify(state, null, 2), 'utf-8');

    // Sauvegarder les informations de la RAM dans ram.json
    const ramInfo = {
        total: (totalMemory / (1024 ** 3)).toFixed(2), // Convertir en GB
        used: (usedMemory / (1024 ** 3)).toFixed(2),   // Convertir en GB
        usage: usage.toFixed(2),
        timestamp: new Date().toISOString(),
    };
    fs.writeFileSync(ramDataPath, JSON.stringify(ramInfo, null, 2), 'utf-8');

    console.log(`RAM Usage: ${usage.toFixed(2)}%`);
}

// Fonction principale pour démarrer la vérification
function startMonitoring() {
    const config = readConfig();
    const interval = config.ramCheckInterval || 60000; // Par défaut à 60 000 ms

    console.log(`Starting RAM monitoring every ${interval / 1000} seconds...`);

    setInterval(() => {
        checkRAM();
    }, interval);
}

module.exports = startMonitoring;

// Démarre le monitoring si le module est exécuté directement
if (require.main === module) {
    startMonitoring();
}
