const express = require('express');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto'); // Utilisé pour générer un token aléatoire
const db = require('./config/database'); // Importer le module de base de données
const { dbFile } = require('./config/database');
const session = require('express-session');

// Configuration du serveur Express
const app = express();
const port = process.env.PORT || 3000;

// Configurer les sessions
app.use(session({
    secret: 'mzPV%fbYE9#A4g89#4i2fbMaitXq^K^Q8%x^Zx5tCwTyiJK2Ajy8T8wZvkca4EBt%drPY!t^wt##Ez%qR%$H^f6VzynUySeHEEf2P7!akJ9f', // Remplacez par une chaîne secrète pour signer les sessions
    resave: false,          // Ne pas resauvegarder la session si elle n'est pas modifiée
    saveUninitialized: true // Sauvegarder une session non initialisée
}));

function checkAuthentication(req, res, next) {
    if (req.session.user) {
        // Si l'utilisateur est connecté, continuer vers la route demandée
        next();
    } else {
        // Si l'utilisateur n'est pas connecté, rediriger vers la page de connexion
        res.redirect('/login');
    }
}

// Middleware pour traiter les données JSON
app.use(express.json());

// Middleware pour parser les données des formulaires
app.use(express.urlencoded({ extended: true }));

// Middleware pour servir les fichiers statiques
app.use(express.static(path.join(__dirname, 'public')));

// Chemin du fichier agent-info.json
const dataDir = path.join(__dirname, 'data');
const filePath = path.join(dataDir, 'agent-info.json');

// Vérifier si le fichier agent-info.json existe déjà
let agentOptions;
if (fs.existsSync(filePath)) {
    // Lire le contenu du fichier existant
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    try {
        agentOptions = JSON.parse(fileContent);
        console.log('Agent Info loaded from file:', agentOptions);
    } catch (error) {
        console.error('Error parsing agent-info.json:', error);
    }
}

// Si le fichier n'existe pas ou s'il n'y a pas de token, générer un nouveau token et nom
if (!agentOptions || !agentOptions.token || !agentOptions.name) {
    const generateToken = () => crypto.randomBytes(16).toString('hex');
    const agentName = process.env.AGENT_NAME || `agent-${crypto.randomBytes(4).toString('hex')}`;

    agentOptions = {
        token: agentOptions?.token || generateToken(),
        name: agentOptions?.name || agentName,
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        os: require('os').type(),
        platform: require('os').platform(),
        arch: require('os').arch(),
    };

    // Créer le dossier 'data' s'il n'existe pas
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir);
    }

    // Écrire les informations dans agent-info.json
    fs.writeFileSync(filePath, JSON.stringify(agentOptions, null, 2), 'utf-8');
    console.log('New Agent Info generated and saved:', agentOptions);
}

// Middleware pour injecter isAuthenticated dans toutes les vues
app.use((req, res, next) => {
    res.locals.isAuthenticated = req.session.user ? true : false;
    next();
});

// Configurer le moteur de template EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Route de connexion accessible sans authentification
app.get('/login', (req, res) => {
    res.render('login', { title: 'Connexion' });
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;

    // Exemple de vérification de l'utilisateur dans la base de données
    db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
        if (err) {
            return res.status(500).json({ message: 'Erreur du serveur' });
        }

        if (!user || user.password !== password) {
            return res.status(401).json({ message: 'Identifiant ou mot de passe incorrect' });
        }

        // Si les identifiants sont corrects, créer une session ou un token
        req.session.user = user;
        res.json({ message: 'Connexion réussie' });
    });
});

// Route pour la déconnexion
app.get('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            return res.redirect('/');
        }
        res.clearCookie('connect.sid');
        res.redirect('/login');
    });
});

// Appliquer le middleware à toutes les routes suivantes
app.use(checkAuthentication);

// Toutes les routes définies après cette ligne seront protégées
const indexRoutes = require('./routes/index');
app.use('/', indexRoutes);

const moduleRoutes = require('./routes/moduleRoutes');
app.use('/', moduleRoutes);

// Démarrer le serveur
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
    console.log(`Agent Info:`, agentOptions);
});
