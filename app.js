// index.js
const fs = require('fs');
const sys = require('./functions/sys');
const forkModule = require('./functions/forkModule');
const cleanUpExistingPids = require('./functions/pidCleanup');
const axios = require('axios');

var uuid = "";

// if (process.env.uuid !== "" || process.env.uuid !== undefined || process.env.uuid !== null) {
//     uuid = process.env.uuid;
//     console.log("UUID: "+uuid);
//     console.log("uuid non valide. Arrêt de l'agent");
//     process.exit(1);
// }

if (fs.existsSync('./dev.lock')) {
    console.log("Utilisation des fonctions de DEV");
    var dom = "dev.mhemery.fr";
} else {
    var dom = "mhemery.fr";
}

// Création des dossier essencielles
sys.createDirectory("data");
sys.createDirectory("data/logs");
sys.createDirectory("data/config");
sys.createDirectory("data/pid");

// Nettoyer les fichiers PID existants
cleanUpExistingPids();

if (!fs.existsSync('data/config/config.json')) {
    console.log("Récupération de la configuration");

    // CALL API
    axios.post(`https://${dom}/api/agent/statut`, {
        uuid: uuid,
        config: true
    }, { timeout: 2000 })
        .then((response) => {
            let jsonData = response.data.data;
            const jsonString = JSON.stringify(jsonData, null, 2); // Le paramètre null et 2 ajoutent de l'espacement pour une meilleure lisibilité

            // Chemin du fichier JSON à créer
            const filePath = 'data/config/config.json';

            // Écrire les données JSON dans le fichier
            fs.writeFile(filePath, jsonString, (err) => {
                if (err) {
                    console.error('Erreur lors de l\'écriture dans le fichier JSON :', err);
                    return;
                }
                console.log('Fichier JSON créé avec succès :', filePath);
                console.log('Vous pouvez redémarrer l\'agent');
            });
        })
        .catch((error) => {
            console.error('Erreur lors de la requête :', error.code);
            console.log("Echec de la récupération de la configuration");
            process.exit(1);

        });
} else {
    setTimeout(() => {
        // Lisez le fichier JSON pour obtenir la liste des modules
        const modulesListPath = './modules/modulesList.json';
        const moduleListRaw = fs.readFileSync(modulesListPath);
        const moduleList = JSON.parse(moduleListRaw);

        // Exécutez chaque module de la liste
        moduleList.forEach((module) => {
            forkModule(module.name, module.path, module.autoStart);
        });
    }, 5000);
}

// ---------------------------------

