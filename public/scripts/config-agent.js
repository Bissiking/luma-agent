document.addEventListener('DOMContentLoaded', () => {
    const configList = document.getElementById('config-list');

    // Fonction pour récupérer et afficher la liste des configurations
    function loadConfigs() {
        fetch('/config-agent/configs')
            .then(response => response.json())
            .then(configs => {
                if (configs.length === 0) {
                    configList.innerHTML = '<p>Aucune configuration disponible.</p>';
                } else {
                    configList.innerHTML = `
                        <table class="config-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Nom de la configuration</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${configs.map(config => `
                                    <tr>
                                        <td>${config.id}</td>
                                        <td>${config.config_name}</td>
                                        <td>
                                            ${config.config_use !== 1 ? `
                                                <button class="btn-default" title="Définir par défaut" data-id="${config.id}">
                                                    <i class="fas fa-check"></i>
                                                </button>` : ''}
                                            <button class="btn-edit" title="Modifier" data-id="${config.id}">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn-delete" title="Supprimer" data-id="${config.id}">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>`;

                    // Ajouter des gestionnaires d'événements pour les boutons
                    document.querySelectorAll('.btn-default').forEach(button => {
                        button.addEventListener('click', () => {
                            setDefaultConfig(button.getAttribute('data-id'));
                        });
                    });

                    document.querySelectorAll('.btn-edit').forEach(button => {
                        button.addEventListener('click', () => {
                            const configId = button.getAttribute('data-id');
                            window.location.href = `/config-agent/edit/${configId}`; // Redirige vers la page d'édition avec l'ID
                        });
                    });

                    document.querySelectorAll('.btn-delete').forEach(button => {
                        button.addEventListener('click', () => {
                            const configId = button.getAttribute('data-id');
                            if (confirm('Êtes-vous sûr de vouloir supprimer cette configuration ?')) {
                                deleteConfig(configId);
                            }
                        });
                    });
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                configList.innerHTML = '<p>Erreur lors de la récupération des configurations.</p>';
            });
    }

    // Fonction pour définir une configuration par défaut
    function setDefaultConfig(configId) {
        fetch(`/config-agent/configs/${configId}/set-default`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(result => {
                loadConfigs(); // Recharger la liste des configurations après mise à jour
            })
            .catch(error => {
                console.error('Erreur:', error);
            });
    }

    // Fonction pour supprimer une configuration
    function deleteConfig(configId) {
        fetch(`/config-agent/configs/${configId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(result => {
            if (result.message) {
                alert(result.message);
                loadConfigs(); // Recharger la liste des configurations après suppression
            }
        })
        .catch(error => {
            console.error('Erreur lors de la suppression des données:', error);
        });
    }

    // Charger les configurations lorsque la page est prête
    loadConfigs();

    // Ajouter un gestionnaire d'événements pour le bouton de création
    const createConfigButton = document.getElementById('create-config-button');
    createConfigButton.addEventListener('click', () => {
        window.location.href = '/config-agent/new'; // Redirige vers la page de création de configuration
    });
});
