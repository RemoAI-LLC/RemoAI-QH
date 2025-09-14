const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Setting up Remo AI Electron Frontend...\n');

// Check if we're in the right directory
if (!fs.existsSync('package.json')) {
    console.error('❌ Error: package.json not found. Please run this script from the app-ui directory.');
    process.exit(1);
}

// Check Node.js version
const nodeVersion = process.version;
const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);

if (majorVersion < 16) {
    console.error(`❌ Error: Node.js version ${nodeVersion} is not supported. Please use Node.js 16 or higher.`);
    process.exit(1);
}

console.log(`✅ Node.js version: ${nodeVersion}`);

// Install dependencies
console.log('\n📦 Installing dependencies...');
try {
    execSync('npm install', { stdio: 'inherit' });
    console.log('✅ Dependencies installed successfully!');
} catch (error) {
    console.error('❌ Error installing dependencies:', error.message);
    process.exit(1);
}

// Check if parent directory has the required files
const parentDir = path.join(__dirname, '..');
const configPath = path.join(parentDir, 'config.yaml');
const srcPath = path.join(parentDir, 'src');

if (!fs.existsSync(configPath)) {
    console.warn('⚠️  Warning: config.yaml not found in parent directory.');
    console.log('   Please make sure your NPU chatbot backend is properly configured.');
}

if (!fs.existsSync(srcPath)) {
    console.warn('⚠️  Warning: src directory not found in parent directory.');
    console.log('   Please make sure your NPU chatbot backend is properly set up.');
}

console.log('\n🎉 Setup complete!');
console.log('\nTo run the application:');
console.log('  npm start          # Production mode');
console.log('  npm run dev        # Development mode with DevTools');
console.log('\nTo build the application:');
console.log('  npm run build      # Build for current platform');
console.log('  npm run dist       # Create distribution package');
console.log('\nMake sure your NPU chatbot backend is running before starting the app!');
