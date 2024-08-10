const monitorSystem = require('../functions/monitorSystem');

function handleSocketConnections(io, alerts) {
    setInterval(() => {
        monitorSystem(alerts, ({ cpuUsage, memoryUsage, diskUsage }) => {
            io.emit('cpu-usage', cpuUsage);
            io.emit('memory-usage', memoryUsage);
            io.emit('disk-usage', diskUsage); // Nouveau
        });
    }, 1000);
}

module.exports = handleSocketConnections;
