const os = require('os');
const recordAlert = require('./recordAlert');
const { memoryThreshold, cpuThreshold } = require('../config/thresholds');

function monitorSystem(alerts) {
    const currentTime = Date.now();
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    const cpuLoad = os.loadavg()[0];

    if (usedMem / totalMem > memoryThreshold) {
        recordAlert('Mémoire', currentTime, alerts);
    } else {
        alerts['Mémoire'] = null;
    }

    if (cpuLoad > cpuThreshold) {
        recordAlert('CPU', currentTime, alerts);
    } else {
        alerts['CPU'] = null;
    }
}

module.exports = monitorSystem;
