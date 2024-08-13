const express = require('express');
const path = require('path');
const fs = require('fs');
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

// Configuration des routes
const indexRoutes = require('./routes/index');
app.use('/', indexRoutes);

// Démarrer le serveur
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
