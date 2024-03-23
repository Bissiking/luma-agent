const WebSocketClient = require('websocket').client;

const client = new WebSocketClient();

client.on('connectFailed', function(error) {
    console.log('Échec de la connexion au serveur WebSocket : ' + error.toString());
});

client.on('connect', function(connection) {
    console.log('Connexion établie avec succès au serveur WebSocket');

    connection.on('error', function(error) {
        console.log('Erreur de connexion WebSocket : ' + error.toString());
    });

    connection.on('close', function() {
        console.log('Connexion WebSocket fermée');
    });

    connection.on('message', function(message) {
        if (message.type === 'utf8') {
            console.log('Message reçu du serveur : ' + message.utf8Data);
        }
    });

    // Envoyer un message au serveur WebSocket
    connection.sendUTF('Hello, serveur WebSocket!');
});

// Connectez-vous au serveur WebSocket
client.connect('ws://dev.mhemery.fr:8080', { 'Sec-WebSocket-Protocol': 'hash' });
