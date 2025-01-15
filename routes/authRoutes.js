const express = require('express');
const axios = require('axios'); // Pour envoyer la requête à l'API de LUMA
const router = express.Router();

// URL de l'API LUMA
const LUMA_API_URL = process.env.LUMA_API_URL;

router.get('/login', (req, res) => {
    res.render('login', {
        title: 'Connexion - LUMA',
        LUMA_API_URL: LUMA_API_URL
    });
})

// Route POST : Relayer les données à l'API de connexion de LUMA
router.post('/login', async (req, res) => {
    const { identifiant, password } = req.body;

    try {
        // Envoyer les données à l'API de LUMA
        const response = await axios.post(LUMA_API_URL+'/api/login', { identifiant, password });

        // Vérifier si la connexion a réussi
        if (response.data.success) {
            // Stocker les informations de l'utilisateur dans la session
            req.session.user = response.data.user;

            // Rediriger vers le tableau de bord après connexion
            res.redirect('/dashboard');
        } else {
            // Afficher une erreur si la connexion a échoué
            res.render('login', {
                title: 'Connexion - LUMA',
                LUMA_API_URL: LUMA_API_URL,
                error: response.data.error || 'Erreur inconnue',
            });
        }
    } catch (err) {
        console.error('Erreur lors de la connexion via l\'API de LUMA :', err.message);

        // Gérer les erreurs de l'API ou du réseau
        const errorMessage =
            err.response?.data?.error ||
            'Impossible de contacter le service de connexion. Veuillez réessayer.';
        res.render('login', {
            title: 'Connexion - LUMA',
            error: errorMessage,
        });
    }
});

// Route GET : Déconnexion
router.get('/logout', (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            console.error('Erreur lors de la déconnexion :', err);
            return res.redirect('/');
        }
        res.clearCookie('connect.sid');
        res.redirect('/auth/login');
    });
});

module.exports = router;
