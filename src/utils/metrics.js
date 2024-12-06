const os = require('os');

function getBasicMetrics() {
    return {
        cpu: os.loadavg()[0],
        ram: Math.round((1 - os.freemem() / os.totalmem()) * 100),
        disk: 50 // À remplacer par une bibliothèque comme 'diskusage'
    };
}

module.exports = { getBasicMetrics };
