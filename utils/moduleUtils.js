const path = require('path');
const fs = require('fs');

function loadModules() {
    const modulesDir = path.join(__dirname, '../modules'); // Chemin vers le dossier des modules
    const modules = [];

    fs.readdirSync(modulesDir).forEach(dir => {
        const modulePath = path.join(modulesDir, dir);
        const moduleJsonPath = path.join(modulePath, 'module.json');
        const statusJsonPath = path.join(modulePath, 'module-status.json');

        if (fs.existsSync(moduleJsonPath) && fs.existsSync(statusJsonPath)) {
            const moduleInfo = JSON.parse(fs.readFileSync(moduleJsonPath, 'utf-8'));
            const statusInfo = JSON.parse(fs.readFileSync(statusJsonPath, 'utf-8'));

            modules.push({
                ...moduleInfo,
                status: statusInfo.status, // Status from the status file
                id: dir, // Using directory name as ID
            });
        }
    });

    return modules;
}

module.exports = { loadModules };
