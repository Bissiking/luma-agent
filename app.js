// index.js
const fs = require('fs');
const sys = require('./functions/sys');
const forkModule = require('./functions/forkModule');
const cleanUpExistingPids = require('./functions/pidCleanup');

const uuid = require('./config.json');

if (uuid.uuid == "") {
    console.log("uuid non valide.");
    process.exit(1);    
}

if (fs.existsSync('./dev.lock')) {
    console.log("Utilisation des fonctions de DEV"); 
}

// Création des dossier essencielles
sys.createDirectory("data");
sys.createDirectory("data/logs");
sys.createDirectory("data/config");
sys.createDirectory("data/pid");

// Nettoyer les fichiers PID existants
cleanUpExistingPids();

// ---------------------------------

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