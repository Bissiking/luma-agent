const monitorSystem = require('./functions/monitorSystem');

let alerts = {};

setInterval(() => monitorSystem(alerts), 10000);
