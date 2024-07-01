const path = require('path');
const checkProcessStatus = require(path.resolve(__dirname, '../../functions/processCheck')).checkProcessStatus;
const { LogsInternal } = require('../../functions/logsModule');
const ModuleName = "jellyfin";

// Utilisation :

function Check() {
    checkProcessStatus('jellyfin')
        .then((isRunning) => {
            if (isRunning) {
                LogsInternal(ModuleName, 1);
                Sat = 1;
            } else {
                LogsInternal(ModuleName, 1);
                Sat = 0;
            }
        })
        .catch((error) => {
            LogsInternal(ModuleName, 1);
            Sat = 0;
        });

}

Check(); // Fisrt start

setInterval(() => {
    Check()
}, 300000); // Check toutes les 5 minutes
