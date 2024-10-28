document.addEventListener('DOMContentLoaded', () => {

    // Envoi du formulaire
    const form = document.getElementById('config-form');
    form.addEventListener('submit', (event) => {
        event.preventDefault();

        // Validation des données du formulaire
        const webPort = form.web_port.value;
        const apiPort = form.api_port.value;

        if (!/^\d{1,4}$/.test(webPort) || !/^\d{1,4}$/.test(apiPort)) {
            alert('Les ports doivent être des chiffres compris entre 0 et 9999.');
            return;
        }

        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            data[key] = value;
        });

        fetch('/config-agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // Assurez-vous que la réponse est JSON
            })
            .then(result => {
                alert(result.message); // Affichez le message de la réponse
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});
