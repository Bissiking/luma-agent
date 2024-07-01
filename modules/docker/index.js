const Docker = require('dockerode');
const fs = require('fs');
const { LogsInternal } = require('../../functions/logsModule');
const ModuleName = "docker";

if (!fs.existsSync('/var/run/docker.sock')) {
    console.error('Socket docker non trouvé');
    LogsInternal(ModuleName, { docker: "no-data" });

    setTimeout(() => {
        process.exit(1);
    }, 5000);
    return;
}

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
        LogsInternal(ModuleName, jsonData);
    });
}

// Appel de la fonction pour lister tous les containers et les stocker dans un fichier JSON
listAllContainersAndStoreJSON();
setInterval(() => {
    listAllContainersAndStoreJSON();
}, 300000); // Vérification toutes les 5 minutes