@echo off
echo Installing eSpeak for Remo AI TTS...
echo =====================================

REM Try to install using winget
echo Trying winget...
winget install --id=espeak-ng.espeak-ng -e
if %errorlevel% == 0 (
    echo eSpeak installed successfully via winget!
    goto :test
)

REM Try chocolatey
echo Trying chocolatey...
choco install espeak-ng -y
if %errorlevel% == 0 (
    echo eSpeak installed successfully via chocolatey!
    goto :test
)

REM Manual download and install
echo Downloading eSpeak manually...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/espeak-ng/espeak-ng/releases/download/1.51/espeak-ng-1.51-win64.zip' -OutFile 'espeak-ng.zip'"

if exist espeak-ng.zip (
    echo Extracting eSpeak...
    powershell -Command "Expand-Archive -Path 'espeak-ng.zip' -DestinationPath 'espeak-ng' -Force"
    
    echo Installing eSpeak to C:\espeak-ng...
    if not exist C:\espeak-ng mkdir C:\espeak-ng
    xcopy /E /I /Y espeak-ng\* C:\espeak-ng\
    
    echo Adding to PATH...
    setx PATH "%PATH%;C:\espeak-ng" /M
    
    echo Cleaning up...
    del espeak-ng.zip
    rmdir /S /Q espeak-ng
    
    echo eSpeak installed to C:\espeak-ng
    echo Please restart your command prompt for PATH changes to take effect.
) else (
    echo Failed to download eSpeak
    echo Please install manually from: https://github.com/espeak-ng/espeak-ng/releases
)

:test
echo Testing eSpeak installation...
espeak-ng --version
if %errorlevel% == 0 (
    echo eSpeak is working correctly!
    espeak-ng "Hello! This is Remo AI speaking."
) else (
    echo eSpeak test failed. Please check installation.
)

pause
