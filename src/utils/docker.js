const fs = require('fs');
const { exec } = require('child_process');

// Vérifie si le fichier docker.sock existe
function isDockerAvailable() {
    const dockerSockPath = '/var/run/docker.sock';
    fs.stat(dockerSockPath, function (err, stat) {
        if (err == null) {
            return true
        } else if (err.code === 'ENOENT') {
            // file does not exist
            return false
        } else {
            console.log('Some other error: ', err.code);
            return false
        }
    });

}

// Vérifie les conteneurs Docker si docker.sock est présent
function checkDockerContainers() {
    return new Promise((resolve, reject) => {
        if (!isDockerAvailable()) {
            console.log('DOCKER OFF -> ' + isDockerAvailable());

            resolve(false); // Si Docker n'est pas disponible
            return;
        }

        // Commande pour lister les conteneurs Docker
        const command = 'docker ps --format "{{.Names}}:{{.State}}"';

        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(new Error(stderr || error.message));
                return;
            }

            const containers = stdout
                .trim()
                .split('\n')
                .map(line => {
                    const [name, state] = line.split(':');
                    return { name, state };
                });

            resolve(containers);
        });
    });
}

module.exports = { isDockerAvailable, checkDockerContainers };
