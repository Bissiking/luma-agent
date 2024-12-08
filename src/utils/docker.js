const Docker = require('dockerode');

// Crée une instance Docker (par défaut, utilise le socket Docker local)
const docker = new Docker({ socketPath: '/var/run/docker.sock' });

async function checkDockerContainers() {
    try {
        // Récupère les conteneurs
        const containers = await docker.listContainers({ all: true });

        // Formate les données des conteneurs
        const containerStatuses = containers.map(container => ({
            id: container.Id,
            name: container.Names[0].replace(/^\//, ''), // Supprime le "/" du nom
            state: container.State,
            status: container.Status,
        }));

        return containerStatuses;
    } catch (error) {
        // Vérifie si Docker n'est pas disponible
        if (error.code === 'ENOENT') {
            return false; // Docker socket n'est pas trouvé
        }
        throw error; // Autre erreur
    }
}

module.exports = { checkDockerContainers };
