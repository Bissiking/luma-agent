// public/scripts/modules.js
document.addEventListener('DOMContentLoaded', () => {
    // Gestionnaire pour le bouton de suppression
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', () => {
            const moduleId = button.getAttribute('data-id');
            if (confirm('Êtes-vous sûr de vouloir supprimer ce module ?')) {
                fetch(`/modules/${moduleId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.message === 'Module supprimé avec succès.') {
                        button.closest('tr').remove();
                    } else {
                        alert('Erreur lors de la suppression du module.');
                    }
                })
                .catch(error => {
                    console.error('Erreur:', error);
                });
            }
        });
    });
});
