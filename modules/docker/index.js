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
        const filePath = './containers.json';

        // Écrire les données JSON dans le fichier
        fs.writeFile(filePath, jsonData, (err) => {
            if (err) {
                console.error('Erreur lors de l\'écriture dans le fichier JSON :', err);
                return;
            }
            console.log('Fichier JSON créé avec succès :', filePath);
        });
    });
}

// Appel de la fonction pour lister tous les containers et les stocker dans un fichier JSON
listAllContainersAndStoreJSON();
