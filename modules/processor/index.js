// modules/processor/index.js
const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, '../../functions/sys')).writeToLogFile;
const os = require('os');
const pidusage = require('pidusage');
const logsDirectory = 'data/logs';
const logFileName = 'processor-log.json';


process.on('message', (msg) => {
    if (msg === 'check') {
        setInterval(() => {
            const currentDate = new Date();
            const DateFull = currentDate.toISOString();
            const formattedDate = currentDate.toISOString().split('T')[0];
            const logFilePath = path.join(logsDirectory, `${formattedDate}-${logFileName}`);
            pidusage(process.pid, (err, stats) => {
                if (err) {
                    console.error('Erreur lors de la récupération de l\'utilisation CPU :', err);
                    return;
                }
                const systemInfo = {
                    date: DateFull,
                    cpu: {
                        architecture: os.arch(),
                        model: os.cpus()[0].model,
                        cores: os.cpus().length,
                        usage: stats.cpu.toFixed(2) + '%'
                    }
                };
                writeToLogFile(logFilePath, systemInfo);
            });
        }, 5000);
    }
});
