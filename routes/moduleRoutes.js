const express = require('express');
const checkAuthentication = require('../middlewares/check-authentication'); // Middleware pour protéger les routes
const { allQuery } = require('../config/db-utils'); // Utilitaire pour interagir avec la base de données

const router = express.Router();

// Exemple : Route pour afficher tous les modules (nécessite une authentification)
router.get('/modules', checkAuthentication, async (req, res) => {
    try {
        const modules = await allQuery('SELECT * FROM modules'); // Requête à la base de données
        res.render('modules', { title: 'Modules disponibles', modules, user: req.session.user });
    } catch (err) {
        console.error('Erreur lors de la récupération des modules :', err.message);
        res.status(500).send('Erreur interne du serveur.');
    }
});

// Exemple : Route pour accéder à un module spécifique
router.get('/modules/:id', checkAuthentication, async (req, res) => {
    const moduleId = req.params.id;
    try {
        const module = await allQuery('SELECT * FROM modules WHERE id = ?', [moduleId]);
        if (!module.length) {
            return res.status(404).send('Module introuvable.');
        }
        res.render('module-detail', { title: 'Détail du module', module: module[0], user: req.session.user });
    } catch (err) {
        console.error('Erreur lors de la récupération du module :', err.message);
        res.status(500).send('Erreur interne du serveur.');
    }
});

module.exports = router;
