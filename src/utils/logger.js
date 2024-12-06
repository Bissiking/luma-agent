const fs = require('fs');
const path = require('path');

// Définir le chemin du fichier de log
const logDirPath = path.join(__dirname, '../logs');
const logFilePath = path.join(logDirPath, 'agent.log');

// Vérifier et créer le dossier de logs s'il n'existe pas
if (!fs.existsSync(logDirPath)) {
    fs.mkdirSync(logDirPath, { recursive: true });
}

// Vérifier et créer le fichier de log s'il n'existe pas
if (!fs.existsSync(logFilePath)) {
    fs.writeFileSync(logFilePath, ''); // Crée un fichier vide
}

function log(level, message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level.toUpperCase()}] ${message}\n`;

    // Écrire dans la console et dans un fichier
    console.log(logEntry.trim());
    fs.appendFileSync(logFilePath, logEntry);
}

module.exports = { log };
