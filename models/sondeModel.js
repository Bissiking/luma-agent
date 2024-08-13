class Sonde {
    constructor(db) {
        this.db = db;
    }

    getAll(callback) {
        this.db.all('SELECT * FROM sondes ORDER BY id DESC', [], callback);
    }

    getById(id, callback) {
        this.db.get('SELECT * FROM sondes WHERE id = ?', [id], callback);
    }

    create(data, callback) {
        const { package_id, package_name, version, user_install_id, sonde_statut, sonde_time_check, sonde_threshold_warning, sonde_threshold_error, logs_file_max } = data;
        this.db.run(`INSERT INTO sondes (package_id, package_name, version, user_install_id, sonde_statut, sonde_time_check, sonde_threshold_warning, sonde_threshold_error, logs_file_max)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`, [package_id, package_name, version, user_install_id, sonde_statut, sonde_time_check, sonde_threshold_warning, sonde_threshold_error, logs_file_max], function (err) {
            callback(err, this.lastID);
        });
    }

    update(id, data, callback) {
        const { package_name, version, user_install_id, sonde_statut, sonde_time_check, sonde_threshold_warning, sonde_threshold_error, logs_file_max } = data;
        this.db.run(`UPDATE sondes SET package_name = ?, version = ?, user_install_id = ?, sonde_statut = ?, sonde_time_check = ?, sonde_threshold_warning = ?, sonde_threshold_error = ?, logs_file_max = ? WHERE id = ?`,
            [package_name, version, user_install_id, sonde_statut, sonde_time_check, sonde_threshold_warning, sonde_threshold_error, logs_file_max, id], callback);
    }

    delete(id, callback) {
        this.db.run('DELETE FROM sondes WHERE id = ?', [id], callback);
    }
}

module.exports = Sonde;
