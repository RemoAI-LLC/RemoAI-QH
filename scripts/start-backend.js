#!/usr/bin/env node
/**
 * Backend Startup Script for Remo AI
 * Starts the Python backend server with proper error handling
 */

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs-extra');

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

async function checkBackendPrerequisites() {
    const llmDir = path.join(__dirname, '..', 'llm');
    const venvPath = path.join(llmDir, 'npu-chatbot-env');
    const pythonExe = os.platform() === 'win32' 
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');
    
    // Check if virtual environment exists
    if (!(await fs.pathExists(venvPath))) {
        logError('Python virtual environment not found!');
        logInfo('Please run "npm install" first to set up the environment.');
        return false;
    }
    
    // Check if Python executable exists
    if (!(await fs.pathExists(pythonExe))) {
        logError('Python executable not found in virtual environment!');
        logInfo('Please run "npm install" first to set up the environment.');
        return false;
    }
    
    // Check if requirements are installed
    return new Promise((resolve) => {
        const checkDeps = spawn(pythonExe, ['-c', 'import flask, whisper, gradio; print("OK")'], {
            cwd: llmDir,
            stdio: 'pipe'
        });
        
        checkDeps.on('close', (code) => {
            if (code === 0) {
                logSuccess('Backend prerequisites check passed!');
                resolve(true);
            } else {
                logError('Python dependencies not installed!');
                logInfo('Please run "npm install" first to install dependencies.');
                resolve(false);
            }
        });
    });
}

function startBackendServer() {
    const llmDir = path.join(__dirname, '..', 'llm');
    const venvPath = path.join(llmDir, 'npu-chatbot-env');
    const pythonExe = os.platform() === 'win32' 
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');
    
    const apiScript = path.join(llmDir, 'src', 'unified_api.py');
    
    log(`${colors.bright}${colors.cyan}🚀 Starting Remo AI Backend Server...${colors.reset}`);
    log(`${colors.blue}Backend URL: http://localhost:8000${colors.reset}`);
    log(`${colors.yellow}Press Ctrl+C to stop the backend server${colors.reset}\n`);
    
    const backendProcess = spawn(pythonExe, [apiScript], {
        cwd: llmDir,
        stdio: 'inherit'
    });
    
    backendProcess.on('error', (error) => {
        logError(`Failed to start backend server: ${error.message}`);
        process.exit(1);
    });
    
    backendProcess.on('close', (code) => {
        if (code !== 0) {
            logError(`Backend server exited with code ${code}`);
        } else {
            logSuccess('Backend server stopped gracefully');
        }
    });
    
    // Handle graceful shutdown
    process.on('SIGINT', () => {
        logInfo('Shutting down backend server...');
        backendProcess.kill('SIGINT');
        process.exit(0);
    });
    
    process.on('SIGTERM', () => {
        logInfo('Shutting down backend server...');
        backendProcess.kill('SIGTERM');
        process.exit(0);
    });
}

async function main() {
    log(`${colors.bright}${colors.magenta}🤖 Remo AI Backend Server${colors.reset}`);
    log(`${colors.cyan}================================${colors.reset}`);
    
    const prerequisitesOk = await checkBackendPrerequisites();
    if (!prerequisitesOk) {
        process.exit(1);
    }
    
    startBackendServer();
}

if (require.main === module) {
    main().catch((error) => {
        logError(`Backend startup failed: ${error.message}`);
        process.exit(1);
    });
}

module.exports = { main };
