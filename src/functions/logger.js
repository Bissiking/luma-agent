const fs = require('fs');
const path = require('path');
const { MAX_FILE_SIZE } = require('../config/thresholds');

// Répertoire des logs
const LOG_DIR = path.join(__dirname, '../logs');

// Assurez-vous que le répertoire des logs existe
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR);
}

// Fonction pour formater la date au format YYYY-MM-DD
function getFormattedDate() {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Fonction pour écrire des logs dans un fichier
function writeLog(filename, logData) {
    const dateStr = getFormattedDate();
    const filePath = path.join(LOG_DIR, `${filename}_${dateStr}.log`);
    const logEntry = `${new Date().toISOString()} - ${logData}\n`;

    let fileSize = 0;
    if (fs.existsSync(filePath)) {
        fileSize = fs.statSync(filePath).size;
    }

    if (fileSize >= MAX_FILE_SIZE) {
        let fileIndex = 1;
        let newFilePath;
        do {
            newFilePath = path.join(LOG_DIR, `${filename}_${dateStr}_${fileIndex}.log`);
            fileIndex++;
        } while (fs.existsSync(newFilePath));
        fs.writeFileSync(newFilePath, logEntry);
    } else {
        fs.writeFileSync(filePath, logEntry, { flag: 'a' });
    }
}

module.exports = writeLog;
