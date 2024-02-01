// functions/pidCleanup.js
const path = require('path');
const fs = require('fs');
function cleanUpExistingPids() {
    const pidDirectory = path.join(__dirname, '../data/pid');

    // Lire les fichiers PID dans le répertoire
    fs.readdir(pidDirectory, (err, files) => {
        if (err) {
            console.error('Erreur lors de la lecture du répertoire PID :', err);
            return;
        }

        // Supprimer chaque fichier PID
        files.forEach((file) => {
            const filePath = path.join(pidDirectory, file);
            fs.unlink(filePath, (err) => {
                if (err) {
                    console.error('Erreur lors de la suppression du fichier PID :', err);
                } else {
                    console.log(`Fichier PID supprimé avec succès : ${filePath}`);
                }
            });
        });
    });
}

module.exports = cleanUpExistingPids;
