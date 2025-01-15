const express = require('express');
const path = require('path');

const commonMiddlewares = (req, res, next) => {
    // Middleware JSON et URL Encoded
    express.json()(req, res, next);
    express.urlencoded({ extended: true })(req, res, next);

    // Middleware pour servir les fichiers statiques
    express.static(path.join(__dirname, '../public'))(req, res, next);

    // Middleware global pour injecter l'authentification
    res.locals.isAuthenticated = req.session?.user ? true : false;
    next();
};

module.exports = commonMiddlewares;
