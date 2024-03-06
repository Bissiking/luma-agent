// modules/memory/index.js
const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, '../../functions/sys')).writeToLogFile;

const os = require('os');
const logsDirectory = 'data/logs';
const logFileName = 'memory-log.json';
const fs = require('fs');
const uuid = require(path.resolve(__dirname, '../../config.json'));
const axios = require('axios');

function memory() {
    const currentDate = new Date();
    const DateFull = currentDate.toISOString();
    const formattedDate = currentDate.toISOString().split('T')[0];
    const logFilePath = path.join(logsDirectory, `${formattedDate}-${logFileName}`);
    const systemInfo = {
        date: DateFull,
        memory: {
            total: Math.round(os.totalmem() / (1024 * 1024)) + ' MB',
            free: Math.round(os.freemem() / (1024 * 1024)) + ' MB',
        }
    };
    SendData(systemInfo);
    writeToLogFile(logFilePath, systemInfo);
}

memory();
setInterval(() => {
    memory();
}, 20000);

function SendData(Statut) {
    // Envoie des informations à l'API
    const currentDate = new Date();
    const DateFull = currentDate.toISOString();
    const result = {
        uuid: uuid.uuid,
        date: DateFull,
        processName: 'memory',
        status: Statut
    };

    if (fs.existsSync('./dev.lock')) {
        var dom = "dev.mhemery.fr"
    } else {
        var dom = "mhemery.fr"
    }
    // Envoi des données à l'API
    axios.post(`https://${dom}/api/agent/statut`, { result }, { timeout: 2000 })
        .then((response) => {
            console.log(response.data);
        })
        .catch((error) => {
            console.error('Erreur lors de la requête :', error.code);
        });
}