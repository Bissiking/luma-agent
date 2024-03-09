// index.js
const fs = require('fs');
const sys = require('./functions/sys');
const forkModule = require('./functions/forkModule');
const cleanUpExistingPids = require('./functions/pidCleanup');
const axios = require('axios');

if (process.env.uuid == "" || process.env.uuid == undefined || process.env.uuid == null) {
    uuid = process.env.uuid;
    console.log("UUID: " + uuid);
    console.log("uuid non valide. Arrêt de l'agent");
    process.exit(1);
} else {
    uuid = process.env.uuid;
    console.log("UUID: " + uuid);
}

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
    })
        .then((response) => {
            console.log(response.data);

            if (response.data.success != true) {
                console.log('Echec de la récupération de la config. #0001');
                process.exit(1);
            }
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

            // First Start
            SendDataAgentUP();
        })
        .catch((error) => {
            console.error('Erreur lors de la requête :', error);
            console.log("Echec de la récupération de la configuration #0002");
            process.exit(1);

        });
} else {
    Récupdata();
    setTimeout(() => {
        // Lisez le fichier JSON pour obtenir la liste des modules
        const modulesListPath = './modules/modulesList.json';
        const moduleListRaw = fs.readFileSync(modulesListPath);
        const moduleList = JSON.parse(moduleListRaw);
        // CONFIG
        const configListPath = 'data/config/config.json';
        const configListRaw = fs.readFileSync(configListPath);
        const configList = JSON.parse(configListRaw);
        // Exécutez chaque module de la liste
        moduleList.forEach((module) => {
            let mod_autostart = module.name + '_autostart';
            let mod_autorestart = module.name + '_autorestart';

            let config_mod_autostart = configList[mod_autostart];
            let config_mod_autorestart = configList[mod_autorestart];

            forkModule(module.name, module.path, config_mod_autostart, config_mod_autorestart);
        });
    }, 5000);
}

// Récupération de la configuration tout les x Temps

function Récupdata() {
    axios.post(`https://${dom}/api/agent/statut`, {
        uuid: uuid,
        config: true,
    })
        .then((response) => {
            console.log(response.data);

            if (response.data.success != true) {
                console.log('Echec de la récupération de la config. #0003');
            }
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
            });
        })
        .catch((error) => {
            console.error('Erreur lors de la requête :', error);
            console.log("Echec de la récupération de la configuration #0004");
        });
}

function SendDataAgentUP() {
    // Envoie des informations à l'API
    const currentDate = new Date();
    const DateFull = currentDate.toISOString();
    const result = {
        uuid: uuid,
        date: DateFull,
        processName: 'agent-online',
        statut: "Online"
    };

    if (fs.existsSync('./dev.lock')) {
        var dom = "dev.mhemery.fr"
    } else {
        var dom = "mhemery.fr"
    }
    // Envoi des données à l'API
    axios.post(`https://${dom}/api/agent/statut`, { result })
        .then((response) => {
            console.log(response.data);
        })
        .catch((error) => {
            console.log('ECHEC');
            console.error('Erreur lors de la requête :', error.code);
        });
}

setInterval(() => {
    SendDataAgentUP(); 
}, 900000); // UP toutes les 15 minutes

setInterval(() => {
    Récupdata();
}, 3600000); // UP toutes les 15 minutes



// ---------------------------------

