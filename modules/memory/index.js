// modules/memory/index.js
const { LogsInternal } = require('../../functions/logsModule');
const ModuleName = "memory";
const os = require('os');

function memory() {

    const systemInfo = {
        memory: {
            total: Math.round(os.totalmem()),
            free: Math.round(os.freemem()),
        }
    };
    LogsInternal(ModuleName, systemInfo)
}

memory();
setInterval(() => {
    memory();
}, 25000);