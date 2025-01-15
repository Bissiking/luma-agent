const { getQuery } = require('../config/db-utils');

// Fonction pour authentifier un utilisateur
const authenticateUser = async (username, password) => {
    try {
        // Requête pour récupérer l'utilisateur par nom d'utilisateur
        const user = await getQuery('SELECT * FROM users WHERE username = ?', [username]);
        if (!user) {
            throw new Error('Utilisateur non trouvé.');
        }

        // Comparaison des mots de passe (vous pouvez utiliser bcrypt pour le hachage)
        if (user.password !== password) {
            throw new Error('Mot de passe incorrect.');
        }

        // Si tout est valide, retourner l'utilisateur
        return user;
    } catch (err) {
        throw err;
    }
};

// Fonction pour déconnecter un utilisateur
const logoutUser = (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            console.error('Erreur lors de la déconnexion :', err);
            return res.redirect('/');
        }
        res.clearCookie('connect.sid');
        res.redirect('/auth/login');
    });
};

module.exports = {
    authenticateUser,
    logoutUser,
};
