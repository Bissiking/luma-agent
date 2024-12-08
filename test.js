const { getDiskInfo } = require('node-disk-info');
const os = require('os');

// Récupérer les métriques CPU
function getCpuMetrics() {
    const cpus = os.cpus(); // Retourne un tableau des cœurs CPU
    const loadAvg = os.loadavg(); // Charge moyenne sur 1, 5 et 15 minutes

    // Calculer l'utilisation globale du CPU
    const totalCores = cpus.length;
    const totalSpeed = cpus.reduce((sum, cpu) => sum + cpu.speed, 0); // Fréquence totale en MHz

    return {
        totalCores,
        totalSpeedMHz: totalSpeed,
        loadAvg1min: loadAvg[0],
        loadAvg5min: loadAvg[1],
        loadAvg15min: loadAvg[2],
    };
}

// Récupérer les métriques RAM
function getRamMetrics() {
    const usage = Math.round((1 - os.freemem() / os.totalmem()) * 100);
    return {
        total: os.totalmem(),
        free: os.freemem(),
        usage
    };
}

// Récupérer les informations sur les disques
async function getDiskMetrics() {
    try {
        const diskInfo = await getDiskInfo();
        return diskInfo
            .filter(disk => disk._blocks && disk._filesystem) // Ignorer les disques vides
            .map(disk => ({
                filesystem: disk._filesystem,
                size: disk._blocks,
                used: disk._used,
                available: disk._available,
                usage: parseInt(disk._capacity.replace('%', ''))
            }));
    } catch (error) {
        console.error('Erreur lors de la récupération des disques :', error.message);
        return [];
    }
}

// Fonction principale pour combiner toutes les métriques
async function getBasicMetrics() {
    const cpu = getCpuMetrics();
    const ram = getRamMetrics();
    const disks = await getDiskMetrics();

    return { cpu, ram, disks };
}

// // Appel et affichage des métriques
// (async () => {
//     const disk = await getBasicMetrics();
//     const cpu = await getBasicMetrics();
//     const ram = await getBasicMetrics();
//     console.log(disk);
//     console.log(cpu);
//     console.log(ram);
// })();