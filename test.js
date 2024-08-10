const os = require('os-utils');

os.cpuUsage(function(v) {
    console.log(Math.round(v * 100));
});
