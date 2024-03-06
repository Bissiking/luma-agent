const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, '../../functions/sys')).writeToLogFile;
const logsDirectory = 'data/logs';
const logFileName = 'disk-log.json';
const uuid = require(path.resolve(__dirname, '../../config.json'));
const axios = require('axios');
// CONST
const fs = require("fs");
const si = require('systeminformation');

function disk() {
    const currentDate = new Date();
    const formattedDate = currentDate.toISOString().split('T')[0];
    const logFilePath = path.join(logsDirectory, `${formattedDate}-${logFileName}`);

    si.fsSize()
        .then(data => {
            const systemInfo = {
                date: currentDate.toISOString(),
                disk: data,
            };
            SendData(systemInfo);
            writeToLogFile(logFilePath, systemInfo);
        })
        .catch(error => {
            console.error('critical', 'DISK', 'La sonde MEM n\'a pas réussi à récupérer les informations. ERR: ' + error)
        })
}

// First Start
disk();
setInterval(() => {
    disk();
}, 60000);

function SendData(Statut) {
    // Envoie des informations à l'API
    const currentDate = new Date();
    const DateFull = currentDate.toISOString();
    const result = {
        uuid: uuid.uuid,
        date: DateFull,
        processName: 'disk',
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