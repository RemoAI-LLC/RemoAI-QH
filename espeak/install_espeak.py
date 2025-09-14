#!/usr/bin/env python3
"""
eSpeak Installation Script for Remo AI
Automatically installs eSpeak on different platforms
"""

import subprocess
import sys
import platform
import os
import urllib.request
import zipfile
import shutil

def log(message, color=''):
    """Print colored log message"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{message}{colors['reset']}")

def log_success(message):
    log(f"[SUCCESS] {message}", 'green')

def log_error(message):
    log(f"[ERROR] {message}", 'red')

def log_warning(message):
    log(f"[WARNING] {message}", 'yellow')

def log_info(message):
    log(f"[INFO] {message}", 'blue')

def check_espeak_installed():
    """Check if eSpeak is already installed"""
    try:
        result = subprocess.run(['espeak', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            log_success(f"eSpeak already installed: {result.stdout.strip()}")
            return True
    except:
        pass
    
    # Try eSpeak-ng
    try:
        result = subprocess.run(['espeak-ng', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            log_success(f"eSpeak-ng already installed: {result.stdout.strip()}")
            return True
    except:
        pass
    
    return False

def install_espeak_windows():
    """Install eSpeak on Windows"""
    log_info("Installing eSpeak on Windows...")
    
    # Try using chocolatey
    try:
        log_info("Trying Chocolatey...")
        result = subprocess.run(['choco', 'install', 'espeak', '-y'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            log_success("eSpeak installed via Chocolatey")
            return True
    except:
        pass
    
    # Try using winget
    try:
        log_info("Trying winget...")
        result = subprocess.run(['winget', 'install', 'espeak'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            log_success("eSpeak installed via winget")
            return True
    except:
        pass
    
    # Manual download and install
    try:
        log_info("Downloading eSpeak manually...")
        espeak_url = "https://github.com/espeak-ng/espeak-ng/releases/download/1.51/espeak-ng-1.51-win64.zip"
        
        # Create temp directory
        temp_dir = "espeak_temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download eSpeak
        zip_path = os.path.join(temp_dir, "espeak-ng.zip")
        urllib.request.urlretrieve(espeak_url, zip_path)
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find espeak-ng.exe
        for root, dirs, files in os.walk(temp_dir):
            if 'espeak-ng.exe' in files:
                espeak_path = os.path.join(root, 'espeak-ng.exe')
                break
        else:
            raise Exception("espeak-ng.exe not found in downloaded files")
        
        # Copy to system PATH or local directory
        system_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'espeak-ng'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'espeak-ng'),
            'C:\\espeak-ng'
        ]
        
        for path in system_paths:
            try:
                os.makedirs(path, exist_ok=True)
                shutil.copy2(espeak_path, path)
                log_success(f"eSpeak installed to {path}")
                
                # Add to PATH
                log_warning(f"Please add {path} to your system PATH")
                return True
            except:
                continue
        
        # Fallback: copy to current directory
        shutil.copy2(espeak_path, 'espeak-ng.exe')
        log_success("eSpeak copied to current directory")
        return True
        
    except Exception as e:
        log_error(f"Manual installation failed: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

def install_espeak_linux():
    """Install eSpeak on Linux"""
    log_info("Installing eSpeak on Linux...")
    
    # Try different package managers
    package_managers = [
        ['apt', 'update', '&&', 'apt', 'install', '-y', 'espeak-ng'],
        ['yum', 'install', '-y', 'espeak-ng'],
        ['dnf', 'install', '-y', 'espeak-ng'],
        ['pacman', '-S', '--noconfirm', 'espeak-ng'],
        ['zypper', 'install', '-y', 'espeak-ng']
    ]
    
    for cmd in package_managers:
        try:
            log_info(f"Trying: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                log_success("eSpeak installed successfully")
                return True
        except:
            continue
    
    log_error("Failed to install eSpeak using package managers")
    return False

def install_espeak_macos():
    """Install eSpeak on macOS"""
    log_info("Installing eSpeak on macOS...")
    
    # Try Homebrew
    try:
        log_info("Trying Homebrew...")
        result = subprocess.run(['brew', 'install', 'espeak-ng'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            log_success("eSpeak installed via Homebrew")
            return True
    except:
        pass
    
    # Try MacPorts
    try:
        log_info("Trying MacPorts...")
        result = subprocess.run(['sudo', 'port', 'install', 'espeak-ng'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            log_success("eSpeak installed via MacPorts")
            return True
    except:
        pass
    
    log_error("Failed to install eSpeak. Please install manually from https://github.com/espeak-ng/espeak-ng")
    return False

def main():
    """Main installation function"""
    log("eSpeak Installation Script for Remo AI", 'cyan')
    log("=" * 50)
    
    # Check if already installed
    if check_espeak_installed():
        log_success("eSpeak is already installed and working!")
        return True
    
    log_info(f"Detected platform: {platform.system()}")
    
    # Install based on platform
    success = False
    if platform.system() == "Windows":
        success = install_espeak_windows()
    elif platform.system() == "Linux":
        success = install_espeak_linux()
    elif platform.system() == "Darwin":  # macOS
        success = install_espeak_macos()
    else:
        log_error(f"Unsupported platform: {platform.system()}")
        return False
    
    if success:
        log_success("eSpeak installation completed!")
        log_info("You can now use TTS functionality in Remo AI")
    else:
        log_error("eSpeak installation failed!")
        log_warning("Please install eSpeak manually:")
        log_warning("  Windows: https://github.com/espeak-ng/espeak-ng/releases")
        log_warning("  Linux: sudo apt install espeak-ng")
        log_warning("  macOS: brew install espeak-ng")
    
    return success

if __name__ == "__main__":
    main()
