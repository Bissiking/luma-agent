const { exec } = require('child_process');
const os = require('os');

function checkProcessStatus(processName) {
    return new Promise((resolve, reject) => {
        let command = '';
        if (os.platform() === 'win32') {
            command = `powershell.exe -Command "Get-Process '${processName}'"`;
        } else if (os.platform() === 'linux') {
            command = `pgrep ${processName}`;
        } else {
            reject(new Error('Système d\'exploitation non pris en charge.'));
            return;
        }

        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(error);
                return;
            }

            if (os.platform() === 'win32') {
                // Vérifie si le processus est trouvé dans la sortie de la commande tasklist
                const isProcessRunning = stdout.includes(processName);
                resolve(isProcessRunning);
            } else if (os.platform() === 'linux') {
                // Vérifie si le processus a un ID de processus (PID) valide
                const pid = parseInt(stdout.trim());
                const isProcessRunning = !isNaN(pid);
                resolve(isProcessRunning);
            }
        });
    });
}



module.exports = { checkProcessStatus }