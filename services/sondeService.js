const Sonde = require('../models/sondeModel');
const db = require('../config/database');

const sondeService = new Sonde(db);

exports.getAllSondes = (callback) => {
  sondeService.getAll(callback);
};

exports.getSondeById = (id, callback) => {
  sondeService.getById(id, callback);
};

exports.createSonde = (data, callback) => {
  sondeService.create(data, callback);
};

exports.updateSonde = (id, data, callback) => {
  sondeService.update(id, data, callback);
};

exports.deleteSonde = (id, callback) => {
  sondeService.delete(id, callback);
};
