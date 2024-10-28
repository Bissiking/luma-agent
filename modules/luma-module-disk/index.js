const si = require('systeminformation');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
require('dotenv').config();

// Chemin du dossier pour stocker les fichiers d'état des notifications
const statusDir = path.join(__dirname, '../../data/disk/status');
if (!fs.existsSync(statusDir)) {
    fs.mkdirSync(statusDir, { recursive: true });
}

// Chemin du fichier JSON pour stocker les informations des disques
const diskDataPath = path.join(__dirname, '../../data/disk/disk.json');

// Chemin du fichier de configuration
const configPath = path.join(__dirname, './config.json');

// Modèle de configuration par défaut
const defaultConfig = {
    status: "stopped",
    diskCheckInterval: 15000 // Intervalle en millisecondes (15 secondes)
};

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

// Fonction pour vérifier les disques et envoyer des notifications si nécessaire
function checkDisks() {
    si.fsSize().then(data => {
        const diskInfo = []; // Pour stocker les données des disques pour le JSON

        data.forEach(disk => {
            const total = disk.size;
            const used = disk.used;
            const usage = (used / total) * 100;

            // Ajouter les informations du disque à l'objet diskInfo
            diskInfo.push({
                mount: disk.mount,
                total: (total / (1024 ** 3)).toFixed(2),
                used: (used / (1024 ** 3)).toFixed(2),
                usage: usage.toFixed(2),
                timestamp: new Date().toISOString(),
            });

            // Chemin du fichier d'état pour cette partition
            const stateFilePath = path.join(statusDir, `${disk.mount.replace(/\//g, '_')}.json`);

            let state = {};
            if (fs.existsSync(stateFilePath)) {
                state = JSON.parse(fs.readFileSync(stateFilePath, 'utf-8'));
            }

            const webhookUrl = process.env.DISCORD_WEBHOOK_URL; // Assurez-vous de définir cette variable d'environnement

            // Vérifier les seuils et envoyer les notifications
            if (usage >= 99 && !state.blockage) {
                sendDiscordNotification(webhookUrl, `🚨 **CRITICAL**: Utilisation du disque ${disk.mount} est remplie à 100%! (${usage.toFixed(2)}%) | Disque de production bloqué ! Action immédiate requise !.`);
                state.blockage = true;
                state.critical95 = true;
                state.warning90 = true;
            } else if (usage >= 95 && !state.critical95) {
                sendDiscordNotification(webhookUrl, `⚠️ **Seuil d'alerte importante**: Utilisation du disque ${disk.mount} est remplie à plus de 95%! (${usage.toFixed(2)}%) | Action requise.`);
                state.critical95 = true;
                state.warning90 = true;
            } else if (usage >= 90 && !state.warning90) {
                sendDiscordNotification(webhookUrl, `⚠️ **Avertissement**: Utilisation du disque ${disk.mount} est remplie à plus de 90% (${usage.toFixed(2)}%) | Action demandée pour éviter le blocage.`);
                state.warning90 = true;
            }

            // Réinitialiser les états si le taux d'utilisation diminue
            if (usage < 90) {
                state.warning90 = false;
                state.critical95 = false;
                state.blockage = false;
            }

            // Sauvegarder l'état actuel
            fs.writeFileSync(stateFilePath, JSON.stringify(state, null, 2), 'utf-8');
        });

        // Sauvegarder les informations des disques dans disk.json
        fs.writeFileSync(diskDataPath, JSON.stringify(diskInfo, null, 2), 'utf-8');
    }).catch(error => {
        console.error(`Error fetching disk information: ${error.message}`);
    });
}

// Fonction pour démarrer la surveillance à intervalle régulier
function startMonitoring() {
    const config = readConfig();
    const interval = config.diskCheckInterval || 60000; // Par défaut à 60 000 ms
    console.log(`Disk monitoring started with an interval of ${interval / 1000} seconds.`);
    setInterval(checkDisks, interval);
}

module.exports = { startMonitoring };

// Démarre le monitoring si le module est exécuté directement
if (require.main === module) {
    startMonitoring();
}