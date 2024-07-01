// CONST
const fs = require("fs");
const si = require('systeminformation');
const { LogsInternal } = require('../../functions/logsModule');
const ModuleName = "disk";

function disk() {

    si.fsSize()
        .then(data => {
            const systemInfo = {
                disk: data,
            };
            LogsInternal(ModuleName, systemInfo);
        })
        .catch(error => {
            console.error('critical', 'DISK', 'La sonde MEM n\'a pas réussi à récupérer les informations. ERR: ' + error)
        })
}

// First Start
disk();
setInterval(() => {
    disk();
}, 3600000); //Check toutes les heures 