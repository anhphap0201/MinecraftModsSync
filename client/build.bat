@echo off
chcp 65001 >nul
echo ========================================
echo   Building Minecraft Mods Sync Client
echo ========================================
echo.

REM Save current directory and change to script directory
set "ORIGINAL_DIR=%CD%"
cd /d "%~dp0"

REM Check if virtual environment exists (check both locations)
set "VENV_FOUND=0"
if exist "..\.venv\Scripts\activate.bat" (
    set "VENV_PATH=..\.venv\Scripts\activate.bat"
    set "VENV_FOUND=1"
)
if exist ".venv\Scripts\activate.bat" (
    set "VENV_PATH=.venv\Scripts\activate.bat"
    set "VENV_FOUND=1"
)

if "%VENV_FOUND%"=="0" (
    echo Error: Virtual environment not found!
    echo Please ensure .venv exists in parent or current directory
    cd /d "%ORIGINAL_DIR%"
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_PATH%"

REM Install PyInstaller if not exists
echo.
echo Installing/Updating PyInstaller...
pip install --upgrade pyinstaller

REM Clean previous builds
echo.
echo [1/4] Cleaning previous builds...
if exist build (
    rmdir /s /q build
)
if exist dist (
    rmdir /s /q dist
)
if exist "*.spec" (
    del /q *.spec
)

echo [2/4] Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name "MinecraftModsSync" ^
    --noconfirm ^
    client.py

if %errorlevel% equ 0 (
    echo.
    echo [3/4] Build completed successfully!
    
    if exist "dist\MinecraftModsSync.exe" (
        echo [4/4] Checking file...
        echo.
        echo ========================================
        echo   BUILD SUCCESSFUL!
        echo ========================================
        echo File: dist\MinecraftModsSync.exe
        dir "dist\MinecraftModsSync.exe" | find "MinecraftModsSync.exe"
        echo.
        echo Next steps:
        echo 1. Copy dist\MinecraftModsSync.exe to desired location
        echo 2. Run the executable
        echo 3. Configure server IP and select mods folder
    ) else (
        echo [4/4] ERROR: Executable not found!
    )
) else (
    echo.
    echo ========================================
    echo   Build failed! Check errors above.
    echo ========================================
)

echo.
cd /d "%ORIGINAL_DIR%"
pause
