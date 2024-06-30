// Envoie des informations à l'API
const nDate = new Date().toLocaleString('fr-FR', {
    timeZone: 'Europe/Paris'
});

const timestamp = Date.now(nDate);
const date = new Date(timestamp);

// Convertir la date en format lisible pour la timezone Europe/Paris
const options = {
    timeZone: 'Europe/Paris',
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    second: 'numeric',
    hour12: false
};
const parisTime = date.toLocaleString('fr-FR', options);

console.log(timestamp); // Affiche la date et l'heure en timezone Europe/Paris
console.log(parisTime); // Affiche la date et l'heure en timezone Europe/Paris
