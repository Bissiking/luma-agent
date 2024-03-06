// modules/processor/index.js
const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, '../../functions/sys')).writeToLogFile;
const os = require('os');
const pidusage = require('pidusage');
const logsDirectory = 'data/logs';
const logFileName = 'processor-log.json';
const fs = require('fs');
const uuid = require(path.resolve(__dirname, '../../config.json'));
const axios = require('axios');

function processor() {
    const currentDate = new Date();
    const DateFull = currentDate.toISOString();
    const formattedDate = currentDate.toISOString().split('T')[0];
    const logFilePath = path.join(logsDirectory, `${formattedDate}-${logFileName}`);
    pidusage(process.pid, (err, stats) => {
        if (err) {
            console.error('Erreur lors de la récupération de l\'utilisation CPU :', err);
            return;
        }
        const systemInfo = {
            date: DateFull,
            cpu: {
                architecture: os.arch(),
                model: os.cpus()[0].model,
                cores: os.cpus().length,
                usage: stats.cpu.toFixed(2) + '%'
            }
        };
        SendData(systemInfo);
        writeToLogFile(logFilePath, systemInfo);
    });
}

processor();
setInterval(() => {
    processor();
}, 10000);

function SendData(Statut) {
    // Envoie des informations à l'API
    const currentDate = new Date();
    const DateFull = currentDate.toISOString();
    const result = {
        uuid: uuid.uuid,
        date: DateFull,
        processName: 'processor',
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