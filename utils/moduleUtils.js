const path = require('path');
const fs = require('fs');

function loadModules() {
    const modulesDir = path.join(__dirname, '../modules'); // Chemin vers le dossier des modules
    const pidDir = path.join(__dirname, '../data/pid'); // Chemin vers le dossier des PIDs
    const modules = [];

    fs.readdirSync(modulesDir).forEach(dir => {
        const modulePath = path.join(modulesDir, dir);
        const moduleJsonPath = path.join(modulePath, 'module.json');
        const pidFilePath = path.join(pidDir, `${dir}.pid`);

        console.log(dir);

        if (fs.existsSync(moduleJsonPath)) {
            const moduleInfo = JSON.parse(fs.readFileSync(moduleJsonPath, 'utf-8'));

            // Vérifier si le fichier PID existe
            const isRunning = fs.existsSync(pidFilePath);


            modules.push({
                ...moduleInfo,
                id: dir, // Utiliser le nom du dossier comme ID
                isRunning: isRunning // Ajouter l'état d'exécution basé sur la présence du fichier PID
            });
        }
    });

    return modules;
}

module.exports = { loadModules };
