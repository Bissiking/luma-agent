const db = require('../config/database');

// Afficher la page de configuration avec les paramètres actuels
exports.getConfigPage = (req, res) => {
    db.get('SELECT * FROM config ORDER BY id DESC LIMIT 1', (err, row) => {
        if (err) {
            res.status(500).send('Erreur lors de la récupération des configurations.');
            return;
        }
        res.sendFile(path.join(__dirname, '../views/config-agent.html'));
    });
};

// Enregistrer les configurations
exports.saveConfig = (req, res) => {
    const { web_port, api_port, allow_add_sondes, update_auto, autostart_os, interface_theme_default, version_agent } = req.body;
    
    const sql = `INSERT INTO config (web_port, api_port, allow_add_sondes, update_auto, autostart_os, interface_theme_default, version_agent) 
                 VALUES (?, ?, ?, ?, ?, ?, ?) 
                 ON CONFLICT(id) 
                 DO UPDATE SET 
                 web_port=excluded.web_port, 
                 api_port=excluded.api_port, 
                 allow_add_sondes=excluded.allow_add_sondes, 
                 update_auto=excluded.update_auto, 
                 autostart_os=excluded.autostart_os, 
                 interface_theme_default=excluded.interface_theme_default, 
                 version_agent=excluded.version_agent`;
    
    db.run(sql, [web_port, api_port, allow_add_sondes, update_auto, autostart_os, interface_theme_default, version_agent], (err) => {
        if (err) {
            res.status(500).send('Erreur lors de l\'enregistrement des configurations.');
            return;
        }
        res.redirect('/config-agent');
    });
};
