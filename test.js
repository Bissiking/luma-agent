const os = require('os');

const cpus = os.cpus(); // Retourne un tableau des cœurs CPU
const loadAvg = os.loadavg(); // Charge moyenne sur 1, 5 et 15 minutes

// Calculer l'utilisation globale du CPU
const totalCores = cpus.length;
const totalSpeed = cpus[0].speed; // Fréquence totale en MHz


console.log(totalSpeed);
 