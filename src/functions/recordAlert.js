const fs = require('fs');
const path = require('path');
const { MAX_FILE_SIZE, ALERT_CHECK_INTERVAL, ALERT_THRESHOLD } = require('../config/thresholds');

const ALERT_DIR = path.join(__dirname, '../alerts');

// Assurez-vous que le répertoire des alertes existe
if (!fs.existsSync(ALERT_DIR)) {
    fs.mkdirSync(ALERT_DIR);
}

// Fonction pour écrire une alerte dans un fichier
function writeAlert(fileName, alertData) {
    const alertFilePath = path.join(ALERT_DIR, fileName);
    let fileSize = 0;

    if (fs.existsSync(alertFilePath)) {
        fileSize = fs.statSync(alertFilePath).size;
    }

    if (fileSize >= MAX_FILE_SIZE) {
        // Créer un nouveau fichier si la taille maximale est atteinte
        let fileIndex = 1;
        let newFilePath;
        do {
            newFilePath = path.join(ALERT_DIR, `${fileName}_${fileIndex}.txt`);
            fileIndex++;
        } while (fs.existsSync(newFilePath));
        fs.writeFileSync(newFilePath, alertData);
    } else {
        // Ajouter l'alerte au fichier existant
        fs.writeFileSync(alertFilePath, alertData, { flag: 'a' });
    }
}

// Fonction pour supprimer une alerte
function removeAlert(fileName) {
    const alertFilePath = path.join(ALERT_DIR, fileName);
    if (fs.existsSync(alertFilePath)) {
        fs.unlinkSync(alertFilePath);
    }
}

// Fonction principale pour gérer les alertes
function recordAlert(type, timestamp, value) {
    const formattedDate = new Date(timestamp).toISOString();
    const alertData = `${formattedDate} - ${type} Alert: ${value}%\n`;

    const fileName = `alert_${type}.txt`;

    if (type === 'Disk') {
        // Gestion spécifique pour les alertes de disque
        if (value > ALERT_THRESHOLD) {
            writeAlert(fileName, alertData);
        } else {
            removeAlert(fileName);
        }
    } else {
        // Gestion des alertes CPU et Mémoire
        writeAlert(fileName, alertData);
    }
}

module.exports = recordAlert;
