const express = require('express');
const checkAuthentication = require('../middlewares/check-authentication'); // Middleware pour protéger certaines routes

const router = express.Router();

// Route principale (page d'accueil)
router.get('/', (req, res) => {
    res.render('index', { title: 'Accueil', user: req.session.user || null });
});

// Route protégée (nécessite une authentification)
router.get('/dashboard', checkAuthentication, (req, res) => {
    res.render('dashboard', { title: 'Tableau de bord', user: req.session.user });
});

module.exports = router;
