const fs = require('fs');
const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, './sys')).writeToLogFile;
const logsDirectory = 'data/logs';
const uuid = process.env.uuid;
const axios = require('axios');

function LogsInternal(ModuleName, systemInfo) {

    const logFileName = ModuleName + '-log.json';

    const currentDate = new Date();
    const formattedDate = currentDate.toISOString().split('T')[0];
    const logFilePath = path.join(logsDirectory, `${formattedDate}-${logFileName}`);

    // Ecriture des logs
    writeToLogFile(logFilePath, systemInfo);
    SendData(ModuleName, systemInfo);
}

function SendData(NameModule, dataInfo) {
    // Envoie des informations à l'API
    const nDate = new Date().toLocaleString('fr-FR', {
        timeZone: 'Europe/Paris'
    });

    const timestamp = Date.now(nDate);

    if (NameModule == "docker") {
        var result = {
            uuid: uuid,
            date: timestamp,
            processName: NameModule,
            containers: dataInfo
        };
    }else{
        var result = {
            uuid: uuid,
            date: timestamp,
            processName: NameModule,
            status: dataInfo
        }; 
    }

    if (fs.existsSync(path.resolve(__dirname, '../dev.lock'))) {
        var dom = "dev.mhemery.fr"
    } else {
        var dom = "mhemery.fr"
    }

    console.log(result);
    // Envoi des données à l'API
    axios.post(`https://${dom}/api/agent/statut`, { result }, { timeout: 2000 })
        .then((response) => {
            console.log(response.data);
        })
        .catch((error) => {
            console.error('Erreur lors de la requête :', error.code);
        });
}

module.exports = {
    LogsInternal
};