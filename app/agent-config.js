const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const os = require('os');
const versionAgent = require('../package.json');

const initializeAgentConfig = (callback) => {
    const dataDir = path.join(__dirname, '../data');
    const filePath = path.join(dataDir, 'agent-info.json');
    let agentOptions;

    if (!agentOptions || !agentOptions.token || !agentOptions.name) {
        agentOptions = {
            token: agentOptions?.token || crypto.randomBytes(16).toString('hex'),
            name: agentOptions?.name || `agent-${crypto.randomBytes(4).toString('hex')}`,
            timestamp: new Date().toISOString(),
            version: versionAgent.version,
            os: os.type(),
            platform: os.platform(),
            arch: os.arch(),
        };

        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir);
        }
        fs.writeFileSync(filePath, JSON.stringify(agentOptions, null, 2), 'utf-8');
    }

    const agentConfig = {
        web_port: process.env.WEB_PORT || 3000,
    };

    callback(null, agentConfig, agentOptions);
};

module.exports = { initializeAgentConfig };
