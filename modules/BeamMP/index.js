const path = require('path');
const checkProcessStatus = require(path.resolve(__dirname, '../../functions/processCheck')).checkProcessStatus;
const { LogsInternal } = require(path.resolve(__dirname, '../../functions/logsModule'));
const ModuleName = "BeamMP";

// Utilisation :

function Check() {
    checkProcessStatus('BeamMP-Server')
        .then((isRunning) => {
            if (isRunning) {
                LogsInternal(ModuleName, 1);
                Sat = 1;
            } else {
                LogsInternal(ModuleName, 0);

                Sat = 0;
            }
        })
        .catch((error) => {
            LogsInternal(ModuleName, 0);
            Sat = 0;
        });

}
Check(); // Fisrt start

setInterval(() => {
    Check()
}, 300000); // Check toutes les 5 minutes
