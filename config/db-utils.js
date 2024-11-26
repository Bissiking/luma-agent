const db = require('./database');

function getAgentConfig(callback) {
    const queryDefaultConfig = `
        SELECT * FROM config
        WHERE config_use = 1
        LIMIT 1;
    `;

    db.get(queryDefaultConfig, [], (err, row) => {
        if (err) {
            console.error('Erreur lors de la récupération de la configuration de l’agent :', err);
            callback(err, null);
        } else if (row) {
            callback(null, row); // Configuration active trouvée
        } else {
            // Aucune configuration active n’est trouvée, retourner des valeurs par défaut
            const defaultConfig = {
                web_port: 80,
                api_port: 8080,
                allow_add_sondes: true,
                update_auto: true,
                autostart_os: false,
                interface_theme_default: 'Default',
                config_use: false,
            };
            callback(null, defaultConfig);
        }
    });
}

module.exports = { getAgentConfig };
