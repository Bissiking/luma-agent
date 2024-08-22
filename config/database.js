const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const crypto = require('crypto'); // Importé pour générer des mots de passe sécurisés

// Définir le dossier de la base de données et le fichier
const dbDir = path.join(__dirname, '../data');
const dbFile = path.join(dbDir, 'database.db');

// Vérifier et créer le dossier de la base de données s'il n'existe pas
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir);
}

// Déplacer la base de données si nécessaire
const originalDbPath = path.join(__dirname, '../database.db');
if (fs.existsSync(originalDbPath) && !fs.existsSync(dbFile)) {
  fs.renameSync(originalDbPath, dbFile);
}

// Créer une instance de la base de données
const db = new sqlite3.Database(dbFile);

// Créer les tables si elles n'existent pas déjà
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    familyname VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL CHECK (role IN ('Administrateur', 'Utilisateur')),
    password VARCHAR(255) NOT NULL,
    interface_theme_default VARCHAR(255) DEFAULT 'Default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS groupes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    groupe_id VARCHAR(255) NOT NULL UNIQUE,
    groupe_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    log_etat VARCHAR(255) CHECK (log_etat IN ('Error', 'Warning', 'Info')),
    log_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS sondes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id VARCHAR(255) NOT NULL UNIQUE,
    package_name VARCHAR(255) NOT NULL,
    version VARCHAR(255),
    user_install_id INTEGER,
    sonde_statut VARCHAR(255) CHECK (sonde_statut IN ('install', 'Wait', 'Error', 'Offline')),
    sonde_time_check INTEGER DEFAULT 0,
    sonde_threshold_warning INTEGER DEFAULT 0,
    sonde_threshold_error INTEGER DEFAULT 0,
    logs_file_max INTEGER DEFAULT 0,
    FOREIGN KEY (user_install_id) REFERENCES users(id) ON DELETE SET NULL
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS sondes_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sonde_id VARCHAR(255),
    sonde_etat VARCHAR(255) CHECK (sonde_etat IN ('Error', 'Warning', 'Info')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sonde_id) REFERENCES sondes(package_id) ON DELETE CASCADE
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_name VARCHAR(255) NOT NULL UNIQUE,
    web_port INTEGER DEFAULT 80,
    api_port INTEGER DEFAULT 8080,
    allow_add_sondes BOOLEAN DEFAULT 1,
    update_auto BOOLEAN DEFAULT 1,
    autostart_os BOOLEAN DEFAULT 0,
    interface_theme_default VARCHAR(255) DEFAULT 'Default',
    config_use BOOLEAN DEFAULT 0
  )`);

  // Vérifier si un administrateur existe déjà
  db.get(`SELECT * FROM users WHERE role = 'Administrateur' LIMIT 1`, (err, row) => {
    if (err) {
      console.error('Error checking for admin user:', err);
    } else if (!row) {
      // Aucune entrée admin n'existe, en créer une
      const username = 'admin';
      const name = 'Admin';
      const familyname = 'User';
      const role = 'Administrateur';
      const defaultTheme = 'Default';

      // Générer un mot de passe sécurisé
      const password = crypto.randomBytes(16).toString('hex');

      db.run(
        `INSERT INTO users (username, name, familyname, role, password, interface_theme_default) VALUES (?, ?, ?, ?, ?, ?)`,
        [username, name, familyname, role, password, defaultTheme],
        function (err) {
          if (err) {
            console.error('Error creating default admin user:', err);
          } else {
            console.log(`Default admin user created with ID ${this.lastID}`);
            console.log(`Admin password: ${password}`);
          }
        }
      );
    } else {
      console.log('Admin user already exists:', row);
    }
  });
});

// Exporter l'instance de la base de données
module.exports = db;
