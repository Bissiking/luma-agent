-- Table des utilisateurs
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Utilisation d'INTEGER et AUTOINCREMENT pour faciliter les inserts
    username VARCHAR(255) NOT NULL UNIQUE, -- Assurer l'unicité du nom d'utilisateur
    name VARCHAR(255) NOT NULL,
    familyname VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL CHECK (role IN ('Administrateur', 'Utilisateur')), -- Contrôle de valeurs possibles
    interface_theme_default VARCHAR(255) DEFAULT 'Default', -- Valeur par défaut
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table des groupes
CREATE TABLE groupes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    groupe_id VARCHAR(255) NOT NULL UNIQUE,
    groupe_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des logs des agents
CREATE TABLE agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, -- Nom de colonne cohérent
    log_etat VARCHAR(255) CHECK (log_etat IN ('Error', 'Warning', 'Info')), -- Contraintes de valeurs possibles
    log_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL -- Ajout d'une gestion de suppression
);

-- Table des sondes
CREATE TABLE sondes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id VARCHAR(255) NOT NULL UNIQUE,
    package_name VARCHAR(255) NOT NULL,
    version VARCHAR(255),
    user_install_id INTEGER, -- Nom de colonne cohérent
    sonde_statut VARCHAR(255) CHECK (sonde_statut IN ('install', 'Wait', 'Error', 'Offline')), -- Contrôle de valeurs possibles
    sonde_time_check INTEGER DEFAULT 0, -- Valeur par défaut
    sonde_threshold_warning INTEGER DEFAULT 0, -- Valeur par défaut
    sonde_threshold_error INTEGER DEFAULT 0, -- Valeur par défaut
    logs_file_max INTEGER DEFAULT 0, -- Valeur par défaut
    FOREIGN KEY (user_install_id) REFERENCES users(id) ON DELETE SET NULL -- Ajout d'une gestion de suppression
);

-- Table des logs des sondes
CREATE TABLE sondes_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sonde_id VARCHAR(255),
    sonde_etat VARCHAR(255) CHECK (sonde_etat IN ('Error', 'Warning', 'Info')), -- Contrôle de valeurs possibles
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sonde_id) REFERENCES sondes(package_id) ON DELETE CASCADE -- Suppression en cascade pour maintenir l'intégrité référentielle
);

-- Table de configuration
CREATE TABLE config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_name VARCHAR(255) NOT NULL UNIQUE,
    web_port INTEGER DEFAULT 80,
    api_port INTEGER DEFAULT 8080,
    allow_add_sondes BOOLEAN DEFAULT 1,
    update_auto BOOLEAN DEFAULT 1,
    autostart_os BOOLEAN DEFAULT 0,
    interface_theme_default VARCHAR(255) DEFAULT 'Default',
    config_use TINYINT(255) BOOLEAN 0
);
