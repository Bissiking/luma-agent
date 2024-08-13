// controllers/metricController.js
const db = require('../config/database');

exports.getMetrics = (req, res) => {
  db.all('SELECT * FROM metrics ORDER BY timestamp DESC', [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(rows);
  });
};

// Ajoutez d'autres fonctions comme createMetric, updateMetric, deleteMetric ici
