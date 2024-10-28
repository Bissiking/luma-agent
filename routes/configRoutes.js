// routes/configRoutes.js
const express = require('express');
const router = express.Router();
const db = require('../config/database');
const path = require('path');
const fs = require('fs');
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, '../package.json'), 'utf8'));
const agentVersion = packageJson.version;

// Route pour obtenir la version de l'agent
router.get('/version', (req, res) => {
    res.json({ version: agentVersion });
});

// Route pour récupérer la configuration actuelle
router.get('/configs', (req, res) => {
    db.all('SELECT id, config_name, config_use FROM config', [], (err, rows) => {
        if (err) {
            return res.status(500).json({ message: 'Erreur lors de la récupération des configurations.' });
        }
        res.json(rows);
    });
});

// Route pour servir la page de configuration de l'agent
router.get('/', (req, res) => {
    res.render('config-agent', { title: 'Configurations' });
});

// Route pour servir la page de configuration de l'agent
router.get('/new', (req, res) => {
    // res.sendFile(path.join(__dirname, '../views/config-agent-new.html'));
    res.render('config-agent-new', { title: 'Nouvelle configuration' });
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

// Servir le fichier HTML d'édition
router.get('/edit/:id', (req, res) => {
    // res.sendFile(path.join(__dirname, '../views/config-agent-edit.html'));
    res.render('config-agent-edit', { title: 'Modification d\'une configuration' });

});

// Route pour récupérer une configuration spécifique par ID
router.get('/config/:id', (req, res) => {
    const configId = req.params.id;
    db.get('SELECT * FROM config WHERE id = ?', [configId], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Erreur lors de la récupération des données.' });
        }
        if (!row) {
            return res.status(404).json({ message: 'Configuration non trouvée.' });
        }
        res.json(row);
    });
});


// ------------------------------------------- //
// PUT //

// Route pour mettre à jour une configuration spécifique par ID
router.put('/config/:id', (req, res) => {
    const configId = req.params.id;
    const { config_name, web_port, api_port, allow_add_sondes, update_auto, autostart_os, interface_theme_default } = req.body;

    db.run(
        `UPDATE config SET config_name = ?, web_port = ?, api_port = ?, allow_add_sondes = ?, update_auto = ?, autostart_os = ?, interface_theme_default = ? WHERE id = ?`,
        [config_name, web_port, api_port, allow_add_sondes, update_auto, autostart_os, interface_theme_default, configId],
        function (err) {
            if (err) {
                return res.status(500).json({ message: 'Erreur lors de la mise à jour des données.' });
            }
            res.json({ message: 'Configuration mise à jour avec succès.' });
        }
    );
});

// ------------------------------------------- //
// DELETE //

// Route pour supprimer une configuration spécifique par ID
router.delete('/configs/:id', (req, res) => {
    const configId = req.params.id;
    
    // Requête SQL pour supprimer la configuration de la base de données
    db.run('DELETE FROM config WHERE id = ?', [configId], function(err) {
        if (err) {
            return res.status(500).json({ message: 'Erreur lors de la suppression de la configuration.' });
        }
        
        if (this.changes === 0) {
            return res.status(404).json({ message: 'Configuration non trouvée.' });
        }

        res.json({ message: 'Configuration supprimée avec succès.' });
    });
});


// ------------------------------------------- //
// POST //

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

router.post('/configs/:id/set-default', (req, res) => {
    const configId = req.params.id;

    // Vérifier si la configuration existe
    db.get('SELECT * FROM config WHERE id = ?', [configId], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Erreur lors de la vérification de la configuration.' });
        }
        if (!row) {
            return res.status(404).json({ message: 'Configuration non trouvée.' });
        }

        db.serialize(() => {
            // Mettre toutes les configurations à 0
            db.run(`UPDATE config SET config_use = 0`, [], function (err) {
                if (err) {
                    return res.status(500).json({ message: 'Erreur lors de la mise à jour des configurations.' });
                }

                // Mettre la configuration sélectionnée à 1
                db.run(`UPDATE config SET config_use = 1 WHERE id = ?`, [configId], function (err) {
                    if (err) {
                        return res.status(500).json({ message: 'Erreur lors de la mise à jour de la configuration par défaut.' });
                    }

                    res.json({ message: 'Configuration définie par défaut avec succès.' });
                });
            });
        });
    });
});


module.exports = router;
