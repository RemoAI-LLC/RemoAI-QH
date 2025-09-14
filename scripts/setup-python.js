#!/usr/bin/env node
/**
 * Python Environment Setup Script for Remo AI
 * Automatically sets up Python virtual environment and installs dependencies
 */

const { spawn, exec } = require('child_process');
const fs = require('fs-extra');
const path = require('path');
const os = require('os');

const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logStep(step, message) {
    log(`\n${colors.cyan}🚀 Step ${step}: ${message}${colors.reset}`);
}

function logSuccess(message) {
    log(`✅ ${message}`, 'green');
}

function logError(message) {
    log(`❌ ${message}`, 'red');
}

function logWarning(message) {
    log(`⚠️  ${message}`, 'yellow');
}

function logInfo(message) {
    log(`ℹ️  ${message}`, 'blue');
}

async function checkPython() {
    return new Promise((resolve) => {
        exec('python --version', (error, stdout, stderr) => {
            if (error) {
                exec('python3 --version', (error3, stdout3, stderr3) => {
                    if (error3) {
                        logError('Python not found! Please install Python 3.8+ from https://python.org');
                        resolve(false);
                    } else {
                        logSuccess(`Found Python: ${stdout3.trim()}`);
                        resolve('python3');
                    }
                });
            } else {
                logSuccess(`Found Python: ${stdout.trim()}`);
                resolve('python');
            }
        });
    });
}

async function checkNode() {
    return new Promise((resolve) => {
        exec('node --version', (error, stdout) => {
            if (error) {
                logError('Node.js not found! Please install Node.js 16+ from https://nodejs.org');
                resolve(false);
            } else {
                logSuccess(`Found Node.js: ${stdout.trim()}`);
                resolve(true);
            }
        });
    });
}

async function setupPythonEnvironment() {
    const pythonCmd = await checkPython();
    if (!pythonCmd) {
        return false;
    }

    const llmDir = path.join(__dirname, '..', 'llm');
    const venvPath = path.join(llmDir, 'npu-chatbot-env');
    
    // Check if virtual environment already exists
    if (await fs.pathExists(venvPath)) {
        logInfo('Virtual environment already exists, checking dependencies...');
        
        // Check if requirements are installed
        const pythonExe = os.platform() === 'win32' 
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
            
        if (await fs.pathExists(pythonExe)) {
            return new Promise((resolve) => {
                exec(`"${pythonExe}" -c "import flask, whisper, gradio; print('All dependencies installed')"`, (error) => {
                    if (error) {
                        logWarning('Dependencies missing, installing...');
                        installPythonDependencies(pythonExe).then(resolve);
                    } else {
                        logSuccess('All Python dependencies are already installed!');
                        resolve(true);
                    }
                });
            });
        }
    }

    logStep(1, 'Creating Python virtual environment...');
    
    return new Promise((resolve) => {
        const createVenv = spawn(pythonCmd, ['-m', 'venv', 'npu-chatbot-env'], {
            cwd: llmDir,
            stdio: 'inherit'
        });

        createVenv.on('close', (code) => {
            if (code === 0) {
                logSuccess('Virtual environment created successfully!');
                const pythonExe = os.platform() === 'win32' 
                    ? path.join(venvPath, 'Scripts', 'python.exe')
                    : path.join(venvPath, 'bin', 'python');
                installPythonDependencies(pythonExe).then(resolve);
            } else {
                logError('Failed to create virtual environment');
                resolve(false);
            }
        });
    });
}

async function installPythonDependencies(pythonExe) {
    logStep(2, 'Installing Python dependencies...');
    
    return new Promise((resolve) => {
        const installDeps = spawn(pythonExe, ['-m', 'pip', 'install', '-r', 'requirements.txt'], {
            cwd: path.join(__dirname, '..', 'llm'),
            stdio: 'inherit'
        });

        installDeps.on('close', (code) => {
            if (code === 0) {
                logSuccess('Python dependencies installed successfully!');
                resolve(true);
            } else {
                logError('Failed to install Python dependencies');
                resolve(false);
            }
        });
    });
}

async function createConfigFiles() {
    logStep(3, 'Setting up configuration files...');
    
    const configPath = path.join(__dirname, '..', 'llm', 'config.yaml');
    const personaPath = path.join(__dirname, '..', 'llm', 'persona.yaml');
    
    // Check if config.yaml exists
    if (!(await fs.pathExists(configPath))) {
        logWarning('config.yaml not found, creating template...');
        const configTemplate = `api_key: "your-api-key-here"
model_server_base_url: "http://localhost:3001/api/v1"
workspace_slug: "remo"
stream: true
stream_timeout: 60`;
        await fs.writeFile(configPath, configTemplate);
        logInfo('Please update llm/config.yaml with your AnythingLLM API key');
    } else {
        logSuccess('config.yaml already exists');
    }
    
    // Check if persona.yaml exists
    if (!(await fs.pathExists(personaPath))) {
        logWarning('persona.yaml not found, creating default personas...');
        // The persona.yaml will be created by the PersonaManager when the app starts
        logInfo('Default personas will be created on first run');
    } else {
        logSuccess('persona.yaml already exists');
    }
}

async function main() {
    log(`${colors.bright}${colors.magenta}🤖 Remo AI - Python Environment Setup${colors.reset}`);
    log(`${colors.cyan}================================================${colors.reset}`);
    
    // Check prerequisites
    logStep(0, 'Checking prerequisites...');
    
    const nodeOk = await checkNode();
    if (!nodeOk) {
        process.exit(1);
    }
    
    const pythonOk = await checkPython();
    if (!pythonOk) {
        process.exit(1);
    }
    
    // Setup Python environment
    const pythonSetupOk = await setupPythonEnvironment();
    if (!pythonSetupOk) {
        logError('Python environment setup failed!');
        process.exit(1);
    }
    
    // Create config files
    await createConfigFiles();
    
    logSuccess('Python environment setup completed successfully!');
    log(`${colors.bright}${colors.green}🎉 You can now run 'npm start' to launch Remo AI!${colors.reset}`);
    log(`${colors.cyan}================================================${colors.reset}`);
}

if (require.main === module) {
    main().catch((error) => {
        logError(`Setup failed: ${error.message}`);
        process.exit(1);
    });
}

module.exports = { main };
