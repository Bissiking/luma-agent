const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { systemData } = require('../globalData'); // Importer systemData

// Initialiser Express
const app = express();
const port = 3000;

// Créer le serveur HTTP
const server = http.createServer(app);

// Créer une instance de Socket.IO
const io = new Server(server);

// Servir les fichiers statiques
app.use(express.static('public'));

// Route pour obtenir les données de surveillance
app.get('/data', (req, res) => {
    res.json(systemData);
});

// Événement de connexion de Socket.IO
io.on('connection', (socket) => {
    console.log('Un client est connecté');
    
    // Émettre les données de surveillance en temps réel
    setInterval(() => {
        socket.emit('systemData', systemData);
    }, 30000); // Émettre toutes les 30 secondes
});

module.exports = { app, server, io };
