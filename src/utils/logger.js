const fs = require('fs');
const path = require('path');

// Fonction pour obtenir le chemin du fichier log quotidien
function getDailyLogFilePath(logDirPath) {
    // Formate la date au format 'YYYY-MM-DD'
    const currentDate = new Date().toISOString().split('T')[0];
    const logFileName = `${currentDate}.log`;

    // Retourne le chemin complet du fichier log
    return path.join(logDirPath, logFileName);
}

// Définir le répertoire des logs
const logDirPath = path.join(__dirname, '../logs');

// Vérifier et créer le dossier de logs s'il n'existe pas
if (!fs.existsSync(logDirPath)) {
    fs.mkdirSync(logDirPath, { recursive: true });
}

// Fonction de log
function log(level, message) {
    // Obtenir le chemin du fichier log pour le jour actuel
    const logFilePath = getDailyLogFilePath(logDirPath);

    // Vérifier et créer le fichier log s'il n'existe pas
    if (!fs.existsSync(logFilePath)) {
        fs.writeFileSync(logFilePath, ''); // Crée un fichier vide
    }

    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level.toUpperCase()}] ${message}\n`;

    // Écrire dans la console et dans un fichier
    console.log(logEntry.trim());
    fs.appendFileSync(logFilePath, logEntry);
}

module.exports = { log };
