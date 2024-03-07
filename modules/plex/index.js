const fs = require('fs');
const path = require('path');
const checkProcessStatus = require(path.resolve(__dirname, '../../functions/processCheck')).checkProcessStatus;
const uuid = process.env.uuid;
const axios = require('axios');
// Utilisation :

function Check() {
    checkProcessStatus('Plex Media Server')
        .then((isRunning) => {
            if (isRunning) {
                console.log('Le processus est en cours d\'exécution.');
                SendData(1)
            } else {
                console.log('Le processus n\'est pas en cours d\'exécution.');
                SendData(0)
            }
        })
        .catch((error) => {
            console.log('Le processus n\'est pas en cours d\'exécution.');
            SendData(0)
        });


    function SendData(Statut) {
        // Envoie des informations à l'API
        const currentDate = new Date();
        const DateFull = currentDate.toISOString();
        const result = {
            uuid: uuid,
            date: DateFull,
            processName: 'plex',
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
}


Check(); // Fisrt start

setInterval(() => {
    Check()
}, 300000); // Check toutes les 5 minutes
