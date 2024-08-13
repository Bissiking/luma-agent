const sondeService = require('../services/sondeService');

exports.getAllSondes = (req, res) => {
  sondeService.getAllSondes((err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(rows);
  });
};

exports.getSondeById = (req, res) => {
  const { id } = req.params;
  sondeService.getSondeById(id, (err, row) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (!row) {
      return res.status(404).json({ error: 'Sonde not found' });
    }
    res.json(row);
  });
};

exports.createSonde = (req, res) => {
  const sondeData = req.body;
  sondeService.createSonde(sondeData, (err, id) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.status(201).json({ id });
  });
};

exports.updateSonde = (req, res) => {
  const { id } = req.params;
  const sondeData = req.body;
  sondeService.updateSonde(id, sondeData, (err) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.status(200).json({ message: 'Sonde updated' });
  });
};

exports.deleteSonde = (req, res) => {
  const { id } = req.params;
  sondeService.deleteSonde(id, (err) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.status(200).json({ message: 'Sonde deleted' });
  });
};
