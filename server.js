const express = require('express');
const path = require('path');
const session = require('express-session');
require('dotenv').config();

const { initializeAgentConfig } = require('./app/agent-config');
const sessionConfig = require('./config/session-config');
const indexRoutes = require('./routes/index');
const moduleRoutes = require('./routes/moduleRoutes');
const authRoutes = require('./routes/authRoutes');
const commonMiddlewares = require('./middlewares/common');

// Charger la configuration de l’agent
initializeAgentConfig((err, agentConfig, agentOptions) => {
    if (err) {
        console.error('Erreur critique :', err);
        process.exit(1);
    }

    const app = express();

    // Configurer les sessions
    app.use(session(sessionConfig));

    // Middleware globaux
    app.use(commonMiddlewares);

    // Configurer le moteur de template
    app.set('view engine', 'ejs');
    app.set('views', path.join(__dirname, 'views'));

    // Définir les routes
    app.use('/', indexRoutes);
    app.use('/', moduleRoutes);
    app.use('/auth', authRoutes);

    // Lancer le serveur
    const port = agentConfig.web_port || 3000;
    app.listen(port, () => {
        console.log(`Serveur lancé : http://localhost:${port}`);
        console.log('Agent Info:', agentOptions);
    });
});
