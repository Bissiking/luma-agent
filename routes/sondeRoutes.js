const express = require('express');
const router = express.Router();

// Définir les routes spécifiques aux sondes
router.get('/', (req, res) => {
    res.send('Page des sondes');
});

module.exports = router;
