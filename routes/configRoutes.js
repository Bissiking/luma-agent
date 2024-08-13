const express = require('express');
const router = express.Router();
const db = require('../config/database');
const path = require('path');
const fs = require('fs');
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, '../package.json'), 'utf8'));
const agentVersion = packageJson.version;

// Route pour obtenir la version de l'agent
router.get('/version', (req, res) => {
    console.log(agentVersion);
    res.json({ version: agentVersion });
});

// Route pour récupérer la configuration actuelle
router.get('/configs', (req, res) => {
    db.all('SELECT config_name FROM config', [], (err, rows) => {
        if (err) {
            return res.status(500).json({ message: 'Erreur lors de la récupération des configurations.' });
        }
        res.json(rows);
    });
});

// Route pour servir la page de configuration de l'agent
router.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../views/config-agent.html'));
});

// Route pour servir la page de configuration de l'agent
router.get('/new', (req, res) => {
    res.sendFile(path.join(__dirname, '../views/config-agent-new.html'));
});

// Route pour récupérer une configuration spécifique
router.get('/:configName', (req, res) => {
    const configName = req.params.configName;
    db.get('SELECT * FROM config WHERE config_name = ? ORDER BY id DESC LIMIT 1', [configName], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Erreur lors de la récupération des données.' });
        }
        if (!row) {
            return res.status(404).json({ message: 'Configuration non trouvée.' });
        }
        res.json(row);
    });
});

// Route pour mettre à jour ou insérer une configuration
router.post('/', (req, res) => {
    const { config_name, web_port, api_port, allow_add_sondes, update_auto, autostart_os, interface_theme_default } = req.body;

    // Validation des données
    if (!/^\d{1,4}$/.test(web_port) || !/^\d{1,4}$/.test(api_port)) {
        return res.status(400).json({ message: 'Les ports doivent être des chiffres compris entre 0 et 9999.' });
    }

    const webPort = parseInt(web_port, 10);
    const apiPort = parseInt(api_port, 10);
    const allowAddSondes = allow_add_sondes === '1';
    const updateAuto = update_auto === '1';
    const autostartOs = autostart_os === '1';

    db.run(
        `INSERT OR REPLACE INTO config (config_name, web_port, api_port, allow_add_sondes, update_auto, autostart_os, interface_theme_default)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [config_name, webPort, apiPort, allowAddSondes, updateAuto, autostartOs, interface_theme_default],
        function (err) {
            if (err) {
                return res.status(500).json({ message: 'Erreur lors de la mise à jour des données.' });
            }
            res.json({ message: 'Configuration mise à jour avec succès.' });
        }
    );
});

module.exports = router;
