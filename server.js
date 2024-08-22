const express = require('express');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto'); // Utilisé pour générer un token aléatoire
const db = require('./config/database'); // Importer le module de base de données
const { dbFile } = require('./config/database');

// Configuration du serveur Express
const app = express();
const port = process.env.PORT || 3000;

// Middleware pour traiter les données JSON
app.use(express.json());

// Middleware pour parser les données des formulaires
app.use(express.urlencoded({ extended: true }));

// Middleware pour servir les fichiers statiques
app.use(express.static(path.join(__dirname, 'public')));

// Chemin du fichier agent-info.json
const dataDir = path.join(__dirname, 'data');
const filePath = path.join(dataDir, 'agent-info.json');

// Vérifier si le fichier agent-info.json existe déjà
let agentOptions;
if (fs.existsSync(filePath)) {
    // Lire le contenu du fichier existant
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    try {
        agentOptions = JSON.parse(fileContent);
        console.log('Agent Info loaded from file:', agentOptions);
    } catch (error) {
        console.error('Error parsing agent-info.json:', error);
    }
}

// Si le fichier n'existe pas ou s'il n'y a pas de token, générer un nouveau token et nom
if (!agentOptions || !agentOptions.token || !agentOptions.name) {
    const generateToken = () => crypto.randomBytes(16).toString('hex');
    const agentName = process.env.AGENT_NAME || `agent-${crypto.randomBytes(4).toString('hex')}`;

    agentOptions = {
        token: agentOptions?.token || generateToken(),
        name: agentOptions?.name || agentName,
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        os: require('os').type(),
        platform: require('os').platform(),
        arch: require('os').arch(),
    };

    // Créer le dossier 'data' s'il n'existe pas
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir);
    }

    // Écrire les informations dans agent-info.json
    fs.writeFileSync(filePath, JSON.stringify(agentOptions, null, 2), 'utf-8');
    console.log('New Agent Info generated and saved:', agentOptions);
}

// Configuration des routes
const indexRoutes = require('./routes/index');
app.use('/', indexRoutes);

// Démarrer le serveur
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
    console.log(`Agent Info:`, agentOptions);
});
