// modules/processor/index.js
const os = require('os');
const os2 = require('os-utils');
const pidusage = require('pidusage');
const path = require('path');
const { LogsInternal } = require(path.resolve(__dirname, '../../functions/logsModule'));
const ModuleName = "processor";

function processor() {
    os2.cpuUsage(function(cpuUsage) {
        console.log('CPU Usage (%): ' + cpuUsage * 100);

        pidusage(process.pid, (err, stats) => {
            if (err) {
                console.error('Erreur lors de la récupération de l\'utilisation CPU :', err);
                return;
            }

            const systemInfo = {
                cpu: {
                    architecture: os.arch(),
                    model: os.cpus()[0].model,
                    cores: os.cpus().length,
                    usage: cpuUsage * 100
                }
            };

            console.log(systemInfo);
            LogsInternal(ModuleName, systemInfo);
        });
    });
}

processor();
setInterval(() => {
    processor();
}, 20000);
