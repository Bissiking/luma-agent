const { exec } = require('child_process');

// Fonction pour récupérer tous les services avec leurs statuts
function getAllServicesWithStatus() {
    return new Promise((resolve, reject) => {
        const isWindows = process.platform === 'win32'; // Détection de l'OS

        if (!isWindows) {
            reject('Cette commande est uniquement disponible sous Windows.');
            return;
        }

        // Commande PowerShell pour récupérer les services sous Windows
        const command = `powershell -Command "Get-Service | ConvertTo-Json -Depth 1"`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(stderr || error.message);
                return;
            }

            try {
                // Traitement des résultats JSON de PowerShell
                const services = JSON.parse(stdout).map(service => ({
                    name: service.Name,
                    status: service.Status.toLowerCase(),
                }));

                resolve(services);
            } catch (parseError) {
                reject(`Erreur d'analyse JSON : ${parseError.message}`);
            }
        });
    });
}

// Exemple d'utilisation
(async () => {
    try {
        const services = await getAllServicesWithStatus();
        console.log('Services:', services);
    } catch (error) {
        console.error('Error fetching services:', error);
    }
})();

module.exports = { getAllServicesWithStatus };
