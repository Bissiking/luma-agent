// modules/memory/index.js
const path = require('path');
const writeToLogFile = require(path.resolve(__dirname, '../../functions/sys')).writeToLogFile;

const os = require('os');
const logsDirectory = 'data/logs';
const logFileName = 'memory-log.json';


process.on('message', (msg) => {
    if (msg === 'check') {
        setInterval(() => {
            const currentDate = new Date();
            const DateFull = currentDate.toISOString();
            const formattedDate = currentDate.toISOString().split('T')[0];
            const logFilePath = path.join(logsDirectory, `${formattedDate}-${logFileName}`);
            const systemInfo = {
                date: DateFull,
                memory: {
                    total: Math.round(os.totalmem() / (1024 * 1024)) + ' MB',
                    free: Math.round(os.freemem() / (1024 * 1024)) + ' MB',
                }
            }; writeToLogFile(logFilePath, systemInfo);
        }, 5000);
    }
});
