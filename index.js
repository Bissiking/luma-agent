// index.js
const fs = require('fs');
const sys = require('./functions/sys');
const forkModule = require('./functions/forkModule');

// Création des dossier essencielles
sys.createDirectory("data");
sys.createDirectory("data/logs");
sys.createDirectory("data/config");

// ---------------------------------

// Lisez le fichier JSON pour obtenir la liste des modules
const modulesListPath = './modules/modulesList.json';
const moduleListRaw = fs.readFileSync(modulesListPath);
const moduleList = JSON.parse(moduleListRaw);

// Exécutez chaque module de la liste
moduleList.forEach((module) => {
    forkModule(module.path, module.autoStart);
});