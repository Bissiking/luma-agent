const { exec } = require('child_process');

function checkServiceStatus(serviceName) {
    return new Promise((resolve, reject) => {
        // Commande PowerShell
        const command = `powershell -Command "try { Get-Service -Name '${serviceName}' -ErrorAction Stop | Select-Object -ExpandProperty Status } catch { 'Not Found' }"`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(new Error(stderr || error.message));
                return;
            }

            const status = stdout.trim(); // Nettoyer les espaces et lignes vides
            if (status === 'Not Found') {
                resolve('nonexistent'); // Service introuvable
            } else if (status === 'Running') {
                resolve('running'); // Service en cours d'exécution
            } else if (status === 'Stopped') {
                resolve('stopped'); // Service arrêté
            } else {
                resolve('unknown'); // État inconnu
            }
        });
    });
}

async function getServicesStatus(services) {
    // Liste des promesses pour chaque service
    const serviceStatuses = await Promise.all(
        services.map(async service => ({
            name: service,
            status: await checkServiceStatus(service) // Résout l'état de chaque service
        }))
    );

    return serviceStatuses; // Retourne le tableau des statuts résolus
}

// Exemple d'utilisation
(async () => {
    try {
        const statuses = await getServicesStatus(services);
        console.log('Statuts des services :', statuses);
    } catch (error) {
        console.error('Erreur lors de la récupération des statuts :', error.message);
    }
})();

module.exports = { getServicesStatus };
