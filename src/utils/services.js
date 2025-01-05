const { exec } = require('child_process');

// Fonction pour récupérer tous les services avec leurs statuts
function getAllServicesWithStatus() {
    return new Promise((resolve, reject) => {
        const isWindows = process.platform === 'win32';

        if (!isWindows) {
            resolve('[]');
            return;
        }

        const command = `powershell -Command "Get-Service | ConvertTo-Json -Depth 1"`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(stderr || error.message);
                return;
            }

            try {
                // Analyse du JSON retourné
                const rawServices = JSON.parse(stdout);

                // Assurez-vous que rawServices est un tableau
                const services = Array.isArray(rawServices)
                    ? rawServices.map(service => ({
                          name: service.Name || 'Unknown', // Nom par défaut si absent
                          status: typeof service.Status === 'string'
                              ? service.Status.toLowerCase()
                              : 'unknown', // Statut par défaut si non disponible
                      }))
                    : [];

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
