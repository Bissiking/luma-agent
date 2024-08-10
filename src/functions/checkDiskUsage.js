const si = require('systeminformation');
const recordAlert = require('./recordAlert');
const { DISK_CHECK_INTERVAL } = require('../config/thresholds');

let lastCheckTime = 0;

async function checkDiskUsage() {
    const currentTime = Date.now();
    const diskData = {};

    // Vérifier si le temps de la dernière vérification est trop court
    if (currentTime - lastCheckTime < DISK_CHECK_INTERVAL) {
        return diskData;
    }

    try {
        const disks = await si.fsSize(); // Récupérer les informations sur les partitions
        for (const disk of disks) {
            const usedPercent = (disk.used / disk.size) * 100; // Calculer le pourcentage utilisé
            diskData[disk.mount] = usedPercent.toFixed(2); // Stocker le pourcentage utilisé

            // Enregistrer ou supprimer une alerte selon le seuil
            recordAlert('Disk', currentTime, usedPercent);
        }
    } catch (error) {
        console.error('Erreur lors de la vérification de l\'utilisation du disque:', error);
    } finally {
        lastCheckTime = currentTime; // Mettre à jour le temps de la dernière vérification
    }

    return diskData;
}

module.exports = checkDiskUsage;
