const fs = require('fs');
const path = require('path');
const os = require('os');

// Chemin du fichier de configuration
const configPath = path.join(__dirname, './config.json');

// Modèle de configuration par défaut
const defaultConfig = {
    status: "stopped",
    cpuCheckInterval: 60000 // Intervalle en millisecondes (60 secondes)
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

// Fonction pour vérifier l'état du CPU
function checkCPU() {
    const cpus = os.cpus();
    let totalIdle = 0;
    let totalTick = 0;

    cpus.forEach(cpu => {
        for (const type in cpu.times) {
            totalTick += cpu.times[type];
        }
        totalIdle += cpu.times.idle;
    });

    const idle = totalIdle / cpus.length;
    const total = totalTick / cpus.length;

    // Calcul du pourcentage d'utilisation du CPU
    const usage = ((total - idle) / total) * 100;

    console.log(`CPU Usage: ${usage.toFixed(2)}%`);
}

// Fonction principale pour démarrer la vérification
function startMonitoring() {
    const config = readConfig();
    const interval = config.cpuCheckInterval || 60000; // Par défaut à 60 000 ms

    console.log(`Starting CPU monitoring every ${interval / 1000} seconds...`);
    
    setInterval(() => {
        checkCPU();
    }, interval);
}

module.exports = startMonitoring;
