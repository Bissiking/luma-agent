const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware pour servir les fichiers statiques
app.use(express.static(path.join(__dirname, '../public')));

// Route pour obtenir les alertes
app.get('/api/alerts', (req, res) => {
    const logsDir = path.join(__dirname, '../logs');
    fs.readdir(logsDir, (err, files) => {
        if (err) {
            return res.status(500).json({ error: 'Unable to read logs directory' });
        }

        const jsonFiles = files.filter(file => file.endsWith('.json')).map(file => path.join(logsDir, file));
        let allAlerts = [];

        jsonFiles.forEach((file, index) => {
            const fileContent = fs.readFileSync(file, 'utf8');
            const data = JSON.parse(fileContent);
            allAlerts = allAlerts.concat(data.alerts);
            if (index === jsonFiles.length - 1) {
                res.json(allAlerts);
            }
        });
    });
});

app.listen(PORT, () => {
    console.log(`API server running on port ${PORT}`);
});
