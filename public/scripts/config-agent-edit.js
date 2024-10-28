document.addEventListener('DOMContentLoaded', () => {
    const configId = window.location.pathname.split('/').pop();
    const configForm = document.getElementById('configForm');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');

    // Fonction pour charger la configuration
    function loadConfig() {
        loadingDiv.style.display = 'flex'; // Utiliser flex pour affichage
        errorDiv.style.display = 'none';
        
        fetch(`/config-agent/config/${configId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(config => {
                if (config) {
                    document.getElementById('config_name').value = config.config_name;
                    document.getElementById('web_port').value = config.web_port;
                    document.getElementById('api_port').value = config.api_port;
                    document.getElementById('allow_add_sondes').checked = config.allow_add_sondes === 1;
                    document.getElementById('update_auto').checked = config.update_auto === 1;
                    document.getElementById('autostart_os').checked = config.autostart_os === 1;
                    document.getElementById('interface_theme_default').value = config.interface_theme_default;
                    
                    configForm.style.display = 'grid'; // Utiliser grid pour affichage
                } else {
                    console.error('Configuration non trouvée');
                    errorDiv.innerText = 'Configuration non trouvée.';
                    errorDiv.style.display = 'flex'; // Utiliser flex pour affichage
                }
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des données:', error);
                errorDiv.innerText = 'Erreur lors du chargement des données.';
                errorDiv.style.display = 'flex'; // Utiliser flex pour affichage
            })
            .finally(() => {
                loadingDiv.style.display = 'none'; // Cacher le loader
            });
    }

    // Charger la configuration au démarrage
    loadConfig();

    // Ajouter un gestionnaire d'événements pour la soumission du formulaire
    configForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Empêche la soumission normale du formulaire

        // Récupérer les données du formulaire
        const formData = new FormData(configForm);
        const data = {
            config_name: formData.get('config_name'),
            web_port: formData.get('web_port'),
            api_port: formData.get('api_port'),
            allow_add_sondes: document.getElementById('allow_add_sondes').checked ? 1 : 0,
            update_auto: document.getElementById('update_auto').checked ? 1 : 0,
            autostart_os: document.getElementById('autostart_os').checked ? 1 : 0,
            interface_theme_default: formData.get('interface_theme_default')
        };

        console.log(data);
        // Envoyer les données au serveur pour mise à jour
        fetch(`/config-agent/config/${configId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(result => {
            if (result.message) {
                alert(result.message);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour des données:', error);
        });
    });
});
