// Ajoutez des scripts JavaScript si nécessaire pour interagir avec les tuiles ou autres éléments
document.addEventListener('DOMContentLoaded', () => {
    // Par exemple, vous pouvez ajouter des gestionnaires d'événements pour les tuiles actives
    document.getElementById('config-agent').addEventListener('click', () => {
        window.location.href = '/config-agent'; // Redirection vers la page de configuration de l'agent
    });
    // document.getElementById('config-users').addEventListener('click', () => {
    //     window.location.href = '/config-users'; // Redirection vers la page de configuration des utilisateurs
    // });
});
