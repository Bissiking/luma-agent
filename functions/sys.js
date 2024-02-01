// functions/sys.js
const fs = require('fs');

function createDirectory(directoryPath) {
    // Vérifiez si le dossier n'existe pas déjà
    if (!fs.existsSync(directoryPath)) {
        // Créez le dossier
        fs.mkdirSync(directoryPath);
        console.log(`Le dossier ${directoryPath} a été créé avec succès.`);
    } else {
        console.log(`Le dossier ${directoryPath} existe déjà.`);
    }
}

function writeToLogFile(logFilePath, data) {
    try {
        // Lit le fichier JSON existant (s'il y en a un)
        let existingData = [];
        if (fs.existsSync(logFilePath)) {
            const fileContent = fs.readFileSync(logFilePath, 'utf8');
            existingData = JSON.parse(fileContent);
        }

        // Ajoute les nouvelles données
        existingData.push(data);

        // Écrit le fichier JSON mis à jour
        fs.writeFileSync(logFilePath, JSON.stringify(existingData, null, 2));
    } catch (error) {
        console.error('Erreur lors de l\'écriture dans le fichier JSON :', error);
    }
}

module.exports = {
    createDirectory,
    writeToLogFile
};
