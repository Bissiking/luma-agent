const { fork } = require('child_process');
const fs = require('fs');
const path = require('path');

function forkModule(moduleName, modulePath, autostart, autoRestart) {
    const pidModule = path.join(__dirname, '../data/pid', `${moduleName}.pid`);
    if (autostart) {
        console.log(`Module ${moduleName} va démarrer en mode autostart.`);
        startModule();
    } else {
        console.log(`Module ${moduleName} ne sera pas démarré en mode autostart.`);
    }

    function startModule() {
        const childProcess = fork(modulePath, [autostart.toString()], { stdio: 'inherit' });

        childProcess.on('spawn', function() {
            // Au démarrage du module
            fs.writeFile(pidModule, process.pid.toString(), (err) => {
                if (err) {
                    console.error('Echec de la création du PID : ' + err);
                } else {
                    console.log(`Fichier PID créé avec succès : ${pidModule}`);
                }
            });
        });

        childProcess.on('exit', (code, signal) => {
            fs.unlink(pidModule, (err) => {
                if (err) {
                    console.error('Echec de la suppression du PID : ' + err);
                } else {
                    console.log(`Fichier PID supprimé avec succès : ${pidModule}`);
                }
            });

            console.log(`Le module ${modulePath} s'est arrêté avec le code ${code} et le signal ${signal}.`);
            // Ajoutez ici du code pour gérer le redémarrage du module si nécessaire
        });
    }
}
module.exports = forkModule;
