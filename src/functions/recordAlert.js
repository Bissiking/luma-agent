const fs = require('fs');
const path = require('path');

function recordAlert(type, currentTime, alerts) {
    const alertFile = path.join(__dirname, '../../logs', `alert_${type}.txt`);

    if (!alerts[type]) {
        alerts[type] = currentTime;
        fs.writeFileSync(alertFile, `Alerte de type ${type} commencée à ${new Date(currentTime).toLocaleString()}\n`);
    } else {
        const duration = ((currentTime - alerts[type]) / 1000).toFixed(2);
        fs.appendFileSync(alertFile, `Alerte active depuis ${duration} secondes.\n`);
    }
}

module.exports = recordAlert;
