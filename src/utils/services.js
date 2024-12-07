const { exec } = require('child_process');

// Vérifie si le service est en cours d'exécution (Windows ou Linux)
function checkServiceStatus(serviceName) {
    return new Promise((resolve, reject) => {
        const isWindows = process.platform === 'win32'; // Détection de l'OS

        // Commande adaptée à l'OS
        const command = isWindows
            ? `powershell -Command "try { Get-Service -Name '${serviceName}' -ErrorAction Stop | Select-Object -ExpandProperty Status } catch { 'Not Found' }"`
            : `systemctl is-active --quiet '${serviceName}' && echo 'active' || echo 'inactive'`;

        exec(command, (error, stdout, stderr) => {
            if (error && isWindows) {
                // Gestion des erreurs pour Windows
                const errorMessage = stderr || error.message;
                if (errorMessage.includes('Not Found')) {
                    resolve('nonexistent'); // Service introuvable
                } else {
                    reject(new Error(errorMessage));
                }
                return;
            } else if (error && !isWindows) {
                // Gestion des erreurs pour Linux
                resolve('nonexistent'); // Si le service n'existe pas
                return;
            }

            // Nettoyer le résultat
            const status = stdout.trim();
            if (isWindows) {
                if (status === 'Not Found') {
                    resolve('nonexistent');
                } else if (status === 'Running') {
                    resolve('running');
                } else if (status === 'Stopped') {
                    resolve('stopped');
                } else {
                    resolve('unknown');
                }
            } else {
                // Linux : Résultat de `systemctl is-active`
                if (status === 'active') {
                    resolve('running');
                } else if (status === 'inactive') {
                    resolve('stopped');
                } else {
                    resolve('unknown'); // Autres états
                }
            }
        });
    });
}

// Vérifie les statuts d'une liste de services
async function getServicesStatus(services) {
    const serviceStatuses = await Promise.all(
        services.map(async service => ({
            name: service,
            status: await checkServiceStatus(service) // Résout l'état de chaque service
        }))
    );

    return serviceStatuses;
}

module.exports = { getServicesStatus };
