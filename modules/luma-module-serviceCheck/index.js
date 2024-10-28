const { exec } = require('child_process');
const os = require('os');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
require('dotenv').config();

// Chemin du fichier de configuration
const configPath = path.join(__dirname, './config.json');

// Chemin du fichier d'état pour les processus
const processesStatusPath = path.join(__dirname, '../../data/processes/status.json');
const statusDir = path.join(__dirname, '../../data/processes');
if (!fs.existsSync(statusDir)) {
    fs.mkdirSync(statusDir, { recursive: true });
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

// Fonction pour vérifier l'état d'un processus
function checkProcessStatus(processName) {
    return new Promise((resolve, reject) => {
        let command = '';
        if (os.platform() === 'win32') {
            command = `powershell.exe -Command "Get-Process '${processName}' -ErrorAction SilentlyContinue"`;
        } else if (os.platform() === 'linux') {
            command = `pgrep ${processName}`;
        } else {
            reject(new Error('Système d\'exploitation non pris en charge.'));
            return;
        }

        exec(command, (error, stdout, stderr) => {
            if (os.platform() === 'win32') {
                if (error) {
                    // Si le processus n'est pas trouvé ou une autre erreur se produit, on le considère comme hors ligne
                    resolve(false);
                } else {
                    // Vérifie si le processus est trouvé dans la sortie de la commande PowerShell
                    const isProcessRunning = stdout.includes(processName);
                    resolve(isProcessRunning);
                }
            } else if (os.platform() === 'linux') {
                if (error) {
                    // Si l'erreur de commande `pgrep` indique que le processus n'est pas trouvé, on le considère comme hors ligne
                    resolve(false);
                } else {
                    // Vérifie si le processus a un ID de processus (PID) valide
                    const pid = stdout.trim();
                    const isProcessRunning = pid.length > 0;
                    resolve(isProcessRunning);
                }
            }
        });
    });
}

// Fonction pour lire la configuration
function readConfig() {
    if (!fs.existsSync(configPath)) {
        console.log('Configuration file not found.');
        return {};
    }
    const configData = fs.readFileSync(configPath, 'utf-8');
    return JSON.parse(configData);
}

// Fonction pour vérifier les processus
async function checkProcesses() {
    const config = readConfig();

    if (!config.processes || !Array.isArray(config.processes)) {
        console.log('No processes defined in configuration.');
        return;
    }

    let state = {};
    if (fs.existsSync(processesStatusPath)) {
        state = JSON.parse(fs.readFileSync(processesStatusPath, 'utf-8'));
    }

    const webhookUrl = process.env.DISCORD_WEBHOOK_URL; // Assurez-vous de définir cette variable d'environnement
    console.log(webhookUrl);

    for (const process of config.processes) {
        try {
            const isRunning = await checkProcessStatus(process.name);

            // Afficher l'état du processus
            console.log(`Process: ${process.name}, Running: ${isRunning}`);

            // Vérifier les changements d'état et envoyer des notifications si le processus est arrêté
            if (!state[process.name]) {
                state[process.name] = isRunning;
                continue;
            }

            if (state[process.name] !== isRunning) {
                if (!isRunning) {
                    const message = `🚨 **Alerte**: Le processus ${process.name} est arrêté. Veuillez vérifier !`;
                    sendDiscordNotification(webhookUrl, message);
                }
                state[process.name] = isRunning;
            }
        } catch (error) {
            console.error(`Error checking process ${process.name}:`, error);
            // Considérer le processus comme hors ligne en cas d'erreur
            state[process.name] = false;
            const message = `🚨 **Alerte**: Le processus ${process.name} ne peut pas être vérifié. Veuillez vérifier !`;
            sendDiscordNotification(webhookUrl, message);
        }
    }

    fs.writeFileSync(processesStatusPath, JSON.stringify(state, null, 2), 'utf-8');
}

// Fonction principale pour démarrer la vérification des processus
function startProcessMonitoring() {
    const config = readConfig();
    const interval = config.processCheckInterval || 60000; // Par défaut à 60 000 ms

    console.log(`Starting process monitoring every ${interval / 1000} seconds...`);

    setInterval(() => {
        checkProcesses();
    }, interval);
}

module.exports = startProcessMonitoring;

// Démarre le monitoring si le module est exécuté directement
if (require.main === module) {
    startProcessMonitoring();
}
