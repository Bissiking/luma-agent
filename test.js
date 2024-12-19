const si = require('systeminformation');
const { getDiskInfo } = require('node-disk-info');


function getDiskMetrics() {
    try {
        const diskInfo = getDiskInfo();
        return diskInfo
    } catch (error) {
        console.error('Erreur lors de la récupération des disques :', error.message);
        return [];
    }
}

console.log(getDiskMetrics());
 