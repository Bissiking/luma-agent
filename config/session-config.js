const session = require('express-session');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

// Vérifiez si le dossier pour les sessions existe, sinon créez-le (si vous utilisez un stockage fichier pour la session)
const sessionStorePath = path.join(__dirname, '../data/sessions');
if (!fs.existsSync(sessionStorePath)) {
    fs.mkdirSync(sessionStorePath, { recursive: true });
}

// Configuration des sessions
const sessionConfig = {
    secret: process.env.SESSION_SECRET || crypto.randomBytes(64).toString('hex'), // Utiliser une clé secrète sécurisée
    resave: false, // Ne pas sauvegarder les sessions si elles n'ont pas été modifiées
    saveUninitialized: false, // Ne pas sauvegarder les sessions non initialisées
    cookie: {
        httpOnly: true, // Empêche JavaScript côté client d'accéder au cookie
        secure: process.env.NODE_ENV === 'production', // Utilise le cookie sécurisé en production
        maxAge: 1000 * 60 * 60 * 24 * 7, // Expiration des cookies : 7 jours
    },
    store: new session.MemoryStore(), // Stockage des sessions (à remplacer en production par un stockage persistant)
};

// Pour production : utiliser un stockage persistant pour les sessions
// Exemple avec connect-sqlite3
if (process.env.NODE_ENV === 'production') {
    const SQLiteStore = require('connect-sqlite3')(session);
    sessionConfig.store = new SQLiteStore({
        db: 'sessions.sqlite',
        dir: sessionStorePath,
    });
}

module.exports = sessionConfig;
