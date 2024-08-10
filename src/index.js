const { server } = require('./server/server'); // Importer le serveur depuis server.js
const monitorSystem = require('./functions/monitorSystem');
const { CPU_CHECK_INTERVAL } = require('./config/thresholds');

// Fonction pour mettre à jour les données de surveillance
async function updateSystemData() {
    try {
        await monitorSystem();
    } catch (error) {
        console.error('Erreur lors de la mise à jour des données du système:', error);
    }
}

// Mettre à jour les données toutes les X millisecondes
setInterval(updateSystemData, CPU_CHECK_INTERVAL);

// Démarrer le serveur
server.listen(3000, () => {
    console.log(`Serveur démarré sur http://localhost:3000`);
});

// Démarrer la surveillance du système
updateSystemData(); // Initialiser les données immédiatement
