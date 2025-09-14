const { spawn } = require('child_process');
const path = require('path');

console.log('🧪 Testing Remo AI Electron App...\n');

// Check if config exists
const configPath = path.join(__dirname, '..', 'llm', 'config.yaml');
const fs = require('fs');

if (!fs.existsSync(configPath)) {
    console.error('❌ Error: config.yaml not found in parent directory.');
    console.log('   Please make sure your NPU chatbot backend is properly configured.');
    process.exit(1);
}

console.log('✅ Configuration file found');

// Check if src directory exists
const srcPath = path.join(__dirname, '..', 'llm', 'src');
if (!fs.existsSync(srcPath)) {
    console.error('❌ Error: src directory not found in parent directory.');
    console.log('   Please make sure your NPU chatbot backend is properly set up.');
    process.exit(1);
}

console.log('✅ Source directory found');

// Test Python backend
console.log('\n🔍 Testing Python backend...');
const pythonTest = spawn('python', [path.join(__dirname, '..', 'llm', 'src', 'auth.py')], { 
    cwd: path.join(__dirname, '..', 'llm'),
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
});

pythonTest.stdout.on('data', (data) => {
    const output = data.toString();
    if (output.includes('✅ Authentication successful')) {
        console.log('✅ Python backend is working correctly');
    } else {
        console.log('⚠️  Python backend output:', output.trim());
    }
});

pythonTest.stderr.on('data', (data) => {
    console.error('❌ Python backend error:', data.toString());
});

pythonTest.on('close', (code) => {
    if (code === 0) {
        console.log('\n🎉 All tests passed! The app should work correctly.');
        console.log('\nTo start the app:');
        console.log('  npm start          # Production mode');
        console.log('  npm run dev        # Development mode');
    } else {
        console.log('\n❌ Some tests failed. Please check your configuration.');
        console.log('   Make sure AnythingLLM is running and properly configured.');
    }
});
