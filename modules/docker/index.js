const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, '../../functions/sys')).writeToLogFile;
const logsDirectory = 'data/logs';
const logFileName = 'disk-log.json';
const uuid = process.env.uuid;
const axios = require('axios');
const Docker = require('dockerode');
const fs = require('fs');

// Créer une instance de Dockerode
const docker = new Docker();

// Fonction pour lister tous les containers Docker et les stocker dans un fichier JSON
function listAllContainersAndStoreJSON() {
    docker.listContainers({ all: true }, function (err, containers) {
        if (err) {
            console.error('Erreur lors de la récupération de la liste des containers Docker :', err);
            return;
        }

        // Stocker les informations sur chaque container dans un tableau
        const containersData = containers.map(function (containerInfo) {
            return {
                id: containerInfo.Id,
                name: containerInfo.Names[0],
                image: containerInfo.Image,
                status: containerInfo.State
            };
        });

        // Convertir le tableau en format JSON
        const jsonData = JSON.stringify(containersData, null, 2);

        // Chemin du fichier JSON à créer
        // const filePath = './data/containers.json';

        // Écrire les données JSON dans le fichier
        SendData(jsonData);
    });
}

function SendData(Statut) {
    // Envoie des informations à l'API
    const currentDate = new Date();
    const DateFull = currentDate.toISOString();
    const result = {
        uuid: uuid,
        date: DateFull,
        processName: 'docker',
        containers: Statut
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

// Appel de la fonction pour lister tous les containers et les stocker dans un fichier JSON
setInterval(() => {
    listAllContainersAndStoreJSON();
}, 120000); // Vérification toutes les 2 minutes