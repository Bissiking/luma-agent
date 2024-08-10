const osUtils = require('os-utils');
const recordAlert = require('./recordAlert');
const checkDiskUsage = require('./checkDiskUsage');
const writeLog = require('./logger');
const { MEMORY_THRESHOLD, CPU_THRESHOLD, CPU_CHECK_INTERVAL, ALERT_CHECK_INTERVAL } = require('../config/thresholds');

let systemData = {}; // Stocke les données de surveillance
let lastLogTime = 0;

function monitorSystem() {
    const alerts = {};

    // Mémoire
    const totalMem = osUtils.totalmem();
    const freeMem = osUtils.freemem();
    const usedMem = totalMem - freeMem;
    const memoryUsage = (usedMem / totalMem) * 100;

    if (memoryUsage > MEMORY_THRESHOLD * 100) {
        recordAlert('Memory', Date.now(), memoryUsage);
        alerts['Memory'] = memoryUsage.toFixed(2);
    } else {
        alerts['Memory'] = memoryUsage.toFixed(2);
    }

    // CPU
    osUtils.cpuUsage((cpuUsage) => {
        if (cpuUsage * 100 > CPU_THRESHOLD) {
            recordAlert('CPU', Date.now(), cpuUsage * 100);
            alerts['CPU'] = (cpuUsage * 100).toFixed(2);
        } else {
            alerts['CPU'] = (cpuUsage * 100).toFixed(2);
        }

        // Disque
        checkDiskUsage().then((diskData) => {
            alerts['Disk'] = diskData;

            // Mettre à jour les données de surveillance
            systemData = {
                cpuUsage: alerts['CPU'],
                memoryUsage: alerts['Memory'],
                diskUsage: alerts['Disk']
            };

            // Écrire dans le fichier de log seulement si l'intervalle est respecté
            const currentTime = Date.now();
            if (currentTime - lastLogTime > ALERT_CHECK_INTERVAL) {
                writeLog('system_data', JSON.stringify(systemData));
                lastLogTime = currentTime; // Mettre à jour le temps de la dernière écriture
            }

        }).catch(error => {
            console.error('Erreur lors de la vérification de l\'utilisation du disque:', error);
        });
    });

    // Planifiez la prochaine vérification
    setTimeout(monitorSystem, CPU_CHECK_INTERVAL);
}

module.exports = monitorSystem;
