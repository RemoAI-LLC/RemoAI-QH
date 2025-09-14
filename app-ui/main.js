const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    titleBarStyle: 'default',
    show: false
  });

  // Load the index.html file
  mainWindow.loadFile('index.html');

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle chat message from renderer process
ipcMain.handle('send-chat-message', async (event, message) => {
  try {
    // Use Python subprocess to communicate with the backend
    const { spawn } = require('child_process');
    const path = require('path');
    
    return new Promise((resolve) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, '..', 'llm', 'src', 'api_wrapper.py'),
        '--message', message,
        '--no-interactive'
      ], {
        cwd: path.join(__dirname, '..', 'llm'),
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
      });
      
      let output = '';
      let error = '';
      
      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0 && output.trim()) {
          resolve({ success: true, response: output.trim() });
        } else {
          resolve({ success: false, error: error || 'Failed to get response from chatbot' });
        }
      });
    });
  } catch (error) {
    console.error('Error in chat handler:', error);
    return { success: false, error: error.message };
  }
});

// Handle streaming chat message
ipcMain.handle('send-streaming-chat-message', async (event, message) => {
  try {
    // For now, use the same approach as regular messages
    // In a real implementation, you'd want to implement proper streaming
    const { spawn } = require('child_process');
    const path = require('path');
    
    return new Promise((resolve) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, '..', 'llm', 'src', 'api_wrapper.py'),
        '--message', message,
        '--no-interactive',
        '--stream'
      ], {
        cwd: path.join(__dirname, '..', 'llm'),
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
      });
      
      let output = '';
      let error = '';
      
      pythonProcess.stdout.on('data', (data) => {
        const chunk = data.toString();
        output += chunk;
        // Send chunk to renderer for streaming effect
        mainWindow.webContents.send('chat-stream-chunk', chunk);
      });
      
      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0 && output.trim()) {
          resolve({ success: true, fullResponse: output.trim() });
        } else {
          resolve({ success: false, error: error || 'Failed to get response from chatbot' });
        }
      });
    });
  } catch (error) {
    console.error('Error in streaming chat handler:', error);
    return { success: false, error: error.message };
  }
});

// Handle clear chat history
ipcMain.handle('clear-chat-history', async () => {
  try {
    // For now, just return success since we don't have persistent history
    // In a real implementation, you'd want to clear the conversation history
    return { success: true };
  } catch (error) {
    console.error('Error clearing chat history:', error);
    return { success: false, error: error.message };
  }
});

// Handle get chat history
ipcMain.handle('get-chat-history', async () => {
  try {
    // For now, return empty history since we don't have persistent storage
    // In a real implementation, you'd want to retrieve conversation history
    return { success: true, history: [] };
  } catch (error) {
    console.error('Error getting chat history:', error);
    return { success: false, error: error.message };
  }
});

// Handle configuration check
ipcMain.handle('check-config', async () => {
  try {
    const fs = require('fs');
    const yaml = require('js-yaml');
    
    const configPath = path.join(__dirname, '..', 'llm', 'config.yaml');
    if (fs.existsSync(configPath)) {
      const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
      return { success: true, config: config };
    } else {
      return { success: false, error: 'Configuration file not found' };
    }
  } catch (error) {
    console.error('Error checking config:', error);
    return { success: false, error: error.message };
  }
});
