// Middleware pour vérifier si l'utilisateur est authentifié
const checkAuthentication = (req, res, next) => {
    if (req.session && req.session.user) {
        // L'utilisateur est authentifié, on continue
        return next();
    }
    // Si l'utilisateur n'est pas authentifié, rediriger vers la page de connexion
    res.redirect('/auth/login');
};

module.exports = checkAuthentication;
