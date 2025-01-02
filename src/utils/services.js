const { exec } = require('child_process');

// Fonction pour récupérer tous les services avec leurs statuts
function getAllServicesWithStatus() {
    return new Promise((resolve, reject) => {
        const isWindows = process.platform === 'win32'; // Détection de l'OS

        // Commande adaptée à l'OS
        const command = isWindows
            ? `powershell -Command "Get-Service | ConvertTo-Json -Depth 1"`
            : `systemctl list-units --type=service --all --no-pager --no-legend | awk '{print $1, $4}'`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(stderr || error.message);
                return;
            }

            try {
                // Traitement des résultats
                const services = isWindows
                    ? JSON.parse(stdout) // Windows retourne JSON avec PowerShell
                    : stdout
                          .trim()
                          .split('\n')
                          .map(line => {
                              const [name, status] = line.split(/\s+/);
                              return {
                                  name,
                                  status: status === 'running' ? 'running' : 'stopped',
                              };
                          });

                resolve(services);
            } catch (parseError) {
                reject(`Parsing error: ${parseError.message}`);
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
