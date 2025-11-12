@echo off
chcp 65001 >nul
echo ========================================
echo   Building Minecraft Mods Sync Client
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "..\.venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run this from the client directory with venv in parent folder
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call ..\.venv\Scripts\activate.bat

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
pause
