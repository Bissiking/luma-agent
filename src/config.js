const fs = require('fs');
const path = require('path');

// Charger les configurations par défaut et spécifiques
const defaultConfig = JSON.parse(fs.readFileSync(path.join(__dirname, '../config/default.json'), 'utf-8'));
const userConfigPath = path.join(__dirname, '../config/config.json');
const userConfig = fs.existsSync(userConfigPath) ? JSON.parse(fs.readFileSync(userConfigPath, 'utf-8')) : {};

const config = { ...defaultConfig, ...userConfig }; // Fusionner les deux configurations

module.exports = config;
