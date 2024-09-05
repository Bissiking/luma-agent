const express = require('express');
const path = require('path');
const fs = require('fs');
const router = express.Router();

// Définir les routes spécifiques aux sondes
const jsonResponse = (filePath, res) => {
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            // Fichier non disponible
            res.json({ success: false });
        } else {
            // Fichier disponible
            res.json({ success: true, data: JSON.parse(data) });
        }
    });
};

// Route pour le CPU
router.get('/cpu', (req, res) => {
    const cpuPath = path.join(__dirname, '..', 'data', 'cpu', 'cpu.json');
    jsonResponse(cpuPath, res);
});

// Route pour le Disk
router.get('/disk', (req, res) => {
    const diskPath = path.join(__dirname, '..', 'data', 'disk', 'disk.json');
    jsonResponse(diskPath, res);
});

// Route pour la RAM
router.get('/ram', (req, res) => {
    const ramPath = path.join(__dirname, '..', 'data', 'ram', 'ram.json');
    jsonResponse(ramPath, res);
});

module.exports = router;
