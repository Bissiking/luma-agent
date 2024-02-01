const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, '../../functions/sys')).writeToLogFile;
const os = require('os');
const diskspace = require('diskspace');
const logsDirectory = 'data/logs';
const logFileName = 'disk-log.json';

process.on('message', (msg) => {
    if (msg === 'check') {
        setInterval(() => {
            const currentDate = new Date();
            const formattedDate = currentDate.toISOString().split('T')[0];
            const logFilePath = path.join(logsDirectory, `${formattedDate}-${logFileName}`);

            diskspace.check('/', (err, result) => {
                if (err) {
                    console.error('Erreur lors de la récupération de l\'espace disque :', err);
                    return;
                }

                const systemInfo = {
                    date: currentDate.toISOString(),
                    disk: {
                        total: result.total,
                        free: result.free,
                        used: result.used,
                        capacity: result.capacity,
                    },
                };

                writeToLogFile(logFilePath, systemInfo);
            });
        }, 5000);
    }
});
