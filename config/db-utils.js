const { getDatabaseConnection } = require('./database');

// Fonction utilitaire pour exécuter une requête SQL avec des paramètres
const runQuery = (query, params = []) => {
    const db = getDatabaseConnection();
    return new Promise((resolve, reject) => {
        db.run(query, params, function (err) {
            if (err) {
                console.error('Erreur lors de l’exécution de la requête SQL :', err.message);
                return reject(err);
            }
            resolve(this); // Retourne les informations sur la requête exécutée
        });
    });
};

// Fonction utilitaire pour obtenir des données avec une requête SQL
const getQuery = (query, params = []) => {
    const db = getDatabaseConnection();
    return new Promise((resolve, reject) => {
        db.get(query, params, (err, row) => {
            if (err) {
                console.error('Erreur lors de l’exécution de la requête SQL :', err.message);
                return reject(err);
            }
            resolve(row); // Retourne une seule ligne de résultat
        });
    });
};

// Fonction utilitaire pour obtenir plusieurs lignes avec une requête SQL
const allQuery = (query, params = []) => {
    const db = getDatabaseConnection();
    return new Promise((resolve, reject) => {
        db.all(query, params, (err, rows) => {
            if (err) {
                console.error('Erreur lors de l’exécution de la requête SQL :', err.message);
                return reject(err);
            }
            resolve(rows); // Retourne toutes les lignes de résultats
        });
    });
};

// Exemple : Fonction pour récupérer la configuration de l'agent
const getAgentConfig = (callback) => {
    const db = getDatabaseConnection();
    db.get('SELECT * FROM agent_config LIMIT 1', [], (err, row) => {
        if (err) {
            console.error('Erreur lors de la récupération de la configuration de l’agent :', err.message);
            return callback(err);
        }
        callback(null, row);
    });
};

module.exports = {
    runQuery,
    getQuery,
    allQuery,
    getAgentConfig,
};
