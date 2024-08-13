document.addEventListener('DOMContentLoaded', () => {
    const configList = document.getElementById('config-list');
    const createConfigButton = document.getElementById('create-config-button');

    // Fonction pour récupérer et afficher la liste des configurations
    function loadConfigs() {
        fetch('/config-agent/configs')
            .then(response => response.json())
            .then(configs => {
                if (configs.length === 0) {
                    configList.innerHTML = '<p>Aucune configuration disponible.</p>';
                } else {
                    configList.innerHTML = '<ul>' + configs.map(config => 
                        `<li>${config.config_name} <a href="/config-agent/${config.config_name}">Modifier</a></li>`
                    ).join('') + '</ul>';
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                configList.innerHTML = '<p>Erreur lors de la récupération des configurations.</p>';
            });
    }

    // Charger les configurations lorsque la page est prête
    loadConfigs();

    // Ajouter un gestionnaire d'événements pour le bouton de création
    createConfigButton.addEventListener('click', () => {
        window.location.href = '/config-agent/new'; // Redirige vers la page de création de configuration
    });
});
