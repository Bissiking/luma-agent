// functions/forkModule.js
const { fork } = require('child_process');

function forkModule(modulePath, autostart) {
    if (autostart) {
        console.log(`Module ${modulePath} va démarrer en mode autostart.`);
        startModule();
    } else {
        console.log(`Module ${modulePath} ne sera pas démarré en mode autostart.`);
    }

    function startModule() {
        const childProcess = fork(modulePath, [autostart.toString()]);

        // Envoyez un message 'check' au processus fork
        childProcess.send('check');

        childProcess.on('message', (result) => {
            console.log(`Résultat du module ${modulePath}:`, result);
        });

        childProcess.on('exit', (code, signal) => {
            console.log(`Le module ${modulePath} s'est arrêté avec le code ${code} et le signal ${signal}.`);
            // Ajoutez ici du code pour gérer le redémarrage du module si nécessaire
        });
    }
}

module.exports = forkModule;
