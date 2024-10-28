const si = require('systeminformation');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
require('dotenv').config();

// Chemin du dossier pour stocker les fichiers d'état des notifications
const statusDir = path.join(__dirname, 'status');
if (!fs.existsSync(statusDir)) {
    fs.mkdirSync(statusDir);
}

// Fonction pour envoyer une notification Discord
function sendDiscordNotification(webhookUrl, message) {
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
        data.forEach(disk => {
            const total = disk.size;
            const used = disk.used;
            const usage = (used / total) * 100;

            console.log(`Partition: ${disk.mount}`);
            console.log(`  Total: ${(total / (1024 ** 3)).toFixed(2)} GB`);
            console.log(`  Used: ${(used / (1024 ** 3)).toFixed(2)} GB`);
            console.log(`  Usage: ${usage.toFixed(2)}%`);
            console.log('---------------------------');

            // Chemin du fichier d'état pour cette partition
            const stateFilePath = path.join(statusDir, `${disk.mount.replace(/\//g, '_')}.json`);

            let state = {};
            if (fs.existsSync(stateFilePath)) {
                state = JSON.parse(fs.readFileSync(stateFilePath, 'utf-8'));
            }

            const webhookUrl = process.env.DISCORD_WEBHOOK_URL; // Assurez-vous de définir cette variable d'environnement

            // Vérifier les seuils et envoyer les notifications
            if (usage >= 99 && !state.blockage) {
                sendDiscordNotification(webhookUrl, `🚨 **CRITICAL**: Utilisation du disque ${disk.mount} est remplis à 100%! (${usage}) | Disque de production bloqué ! Action immédiate requis !.`);
                state.blockage = true;
                state.critical95 = true;
                state.warning90 = true;
            } else if (usage >= 95 && !state.critical95) {
                sendDiscordNotification(webhookUrl, `⚠️ **Seuil d'alerte importante**: Utilisation du disque ${disk.mount}  est remplis à plus de 95%! (${usage}) | Action requis.`);
                state.critical95 = true;
                state.warning90 = true;
            } else if (usage >= 90 && !state.warning90) {
                sendDiscordNotification(webhookUrl, `⚠️ **Avertissment**: Utilisation du disque ${disk.mount} est remplis à plus de 90% (${usage}) | Action demandé pour éviter le blocage`);
                state.warning90 = true;
            }

            // Réinitialiser les états si le taux d'utilisation diminue
            if (usage < 90) {
                state.warning90 = false;
                state.critical95 = false;
                state.blockage = false;
            }

            console.log(statusDir);

            // Sauvegarder l'état actuel
            fs.writeFileSync(stateFilePath, JSON.stringify(state, null, 2), 'utf-8');
        });
    }).catch(error => {
        console.error(`Error fetching disk information: ${error.message}`);
    });
}

// Fonction pour démarrer la surveillance à intervalle régulier
function startDiskMonitoring(interval = 15000) {
    console.log(`Disk monitoring started with an interval of ${interval / 1000} seconds.`);
    setInterval(checkDisks, interval);
}

// Démarre le monitoring si le module est exécuté directement
if (require.main === module) {
    const interval = process.argv[2] ? parseInt(process.argv[2], 10) : 15000;
    startDiskMonitoring(interval);
}

module.exports = { startDiskMonitoring };
