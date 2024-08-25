const express = require('express');
const path = require('path');
const router = express.Router();

// Import des routes spécifiques
const sondeRoutes = require('./sondeRoutes'); // Assurez-vous que ce fichier existe
const configRoutes = require('./configRoutes'); // Assurez-vous que ce fichier existe

// Route pour la page d'accueil
router.get('/', (req, res) => {
    res.render('index', { title: 'Accueil' });
});

// Utilisation des routes spécifiques
router.use('/sondes', sondeRoutes);
router.use('/config-agent', configRoutes);

module.exports = router;
