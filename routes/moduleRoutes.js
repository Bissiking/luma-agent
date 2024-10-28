// routes/moduleRoutes.js
const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();

// Dossier des modules
const modulesDir = path.join(__dirname, '../modules');
const { loadModules } = require('../utils/moduleUtils'); // Importer la fonction loadModules

// Route pour afficher la liste des modules
router.get('/modules', (req, res) => {
    const modules = loadModules(); // Charger les modules

    res.render('modules-list', { modules });
});

// Route pour éditer un module spécifique
router.get('/modules/edit/:id', (req, res) => {
    const moduleId = req.params.id;
    const modulePath = path.join(modulesDir, moduleId, 'module.json');

    if (fs.existsSync(modulePath)) {
        const moduleInfo = JSON.parse(fs.readFileSync(modulePath, 'utf-8'));
        res.render('module-edit', { moduleId, ...moduleInfo });
    } else {
        res.status(404).json({ message: 'Module non trouvé.' });
    }
});

// Route pour supprimer un module spécifique
router.delete('/modules/:id', (req, res) => {
    const moduleId = req.params.id;
    const modulePath = path.join(modulesDir, moduleId);

    if (fs.existsSync(modulePath)) {
        fs.rm(modulePath, { recursive: true, force: true }, err => {
            if (err) {
                return res.status(500).json({ message: 'Erreur lors de la suppression du module.' });
            }
            res.json({ message: 'Module supprimé avec succès.' });
        });
    } else {
        res.status(404).json({ message: 'Module non trouvé.' });
    }
});

// Route pour démarrer un module spécifique
router.post('/modules/start/:id', (req, res) => {
    const moduleId = req.params.id;
    const statusFilePath = path.join(modulesDir, moduleId, 'module-status.json');

    if (fs.existsSync(statusFilePath)) {
        const statusInfo = JSON.parse(fs.readFileSync(statusFilePath, 'utf-8'));
        statusInfo.status = 'running';

        fs.writeFileSync(statusFilePath, JSON.stringify(statusInfo, null, 2), 'utf-8');
        res.json({ success: true });
    } else {
        res.status(404).json({ success: false, message: 'Module non trouvé' });
    }
});

// Route pour arrêter un module spécifique
router.post('/modules/stop/:id', (req, res) => {
    const moduleId = req.params.id;
    const statusFilePath = path.join(modulesDir, moduleId, 'module-status.json');

    if (fs.existsSync(statusFilePath)) {
        const statusInfo = JSON.parse(fs.readFileSync(statusFilePath, 'utf-8'));
        statusInfo.status = 'stopped';

        fs.writeFileSync(statusFilePath, JSON.stringify(statusInfo, null, 2), 'utf-8');
        res.json({ success: true });
    } else {
        res.status(404).json({ success: false, message: 'Module non trouvé' });
    }
});

module.exports = router;
