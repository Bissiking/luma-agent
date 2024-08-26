document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Empêche le rechargement de la page

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const result = await response.json();

            if (response.ok) {
                // Redirection en cas de succès
                window.location.href = '/'; // Par exemple, redirige vers une page d'accueil/dashbord
            } else {
                // Affichage du message d'erreur
                errorMessage.textContent = result.message || 'Erreur de connexion';
            }
        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = 'Erreur de connexion';
        }
    });
});
