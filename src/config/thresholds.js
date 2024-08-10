// src/config/thresholds.js

module.exports = {
    CPU_THRESHOLD: 90, // Seuil de pourcentage pour CPU
    MEMORY_THRESHOLD: 90, // Seuil de pourcentage pour la mémoire
    DISK_THRESHOLD: 0.90, // Seuil de pourcentage pour le disque
    CPU_CHECK_INTERVAL: 5000, // Intervalle de vérification du CPU en millisecondes (5 secondes)
    MEMORY_CHECK_INTERVAL: 5000, // Intervalle de vérification de la mémoire en millisecondes (5 secondes)
    DISK_CHECK_INTERVAL: 10000, // Intervalle de vérification du disque en millisecondes (10 secondes)
    ALERT_CHECK_INTERVAL: 30000, // Intervalle d'écriture dans le log en millisecondes (60 secondes)
    MAX_FILE_SIZE: 5 * 1024 * 1024 // Taille maximale du fichier de log en octets (5 Mo)
};
