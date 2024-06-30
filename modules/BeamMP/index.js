const fs = require('fs');
const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, '../../functions/sys')).writeToLogFile;
const logsDirectory = 'data/logs';
const logFileName = 'BeamMP-log.json';
const checkProcessStatus = require(path.resolve(__dirname, '../../functions/processCheck')).checkProcessStatus;
const uuid = process.env.uuid;
const axios = require('axios');

// Utilisation :

function Check() {
    checkProcessStatus('BeamMP-Server')
        .then((isRunning) => {
            if (isRunning) {
                console.log('Le processus est en cours d\'exécution.');
                SendData(1);
                Sat = 1;
            } else {
                console.log('Le processus n\'est pas en cours d\'exécution.');
                SendData(0);
                Sat = 0;
            }
        })
        .catch((error) => {
            console.log('Le processus n\'est pas en cours d\'exécution.');
            SendData(0);
            Sat = 0;
        });

}

function SendData(Statut) {

    // Création des logs (Variables)

    const nDate = new Date().toLocaleString('fr-FR', {
        timeZone: 'Europe/Paris'
    });
    
    const timestamp = Date.now(nDate);

    const currentDate = new Date();
    const DateFull = currentDate.toISOString();
    const formattedDate = currentDate.toISOString().split('T')[0];
    const logFilePath = path.join(logsDirectory, `${formattedDate}-${logFileName}`);

    const systemInfo = {
        date: DateFull,
        plex: {
            processName: 'BeamMP',
            status: Statut
        }
    };

    // Création d'un logs
    writeToLogFile(logFilePath, systemInfo);

    // Envoie des informations à l'API
    const result = {
        uuid: uuid,
        date: timestamp,
        processName: 'BeamMP',
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

Check(); // Fisrt start

setInterval(() => {
    Check()
}, 300000); // Check toutes les 5 minutes
