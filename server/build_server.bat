@echo off
chcp 65001 >nul
echo ========================================
echo   Building Minecraft Mods Sync Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "..\.venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run this from the server directory with venv in parent folder
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
if exist "build" (
    echo Cleaning previous build...
    rmdir /s /q build
)
if exist "dist" (
    rmdir /s /q dist
)
if exist "*.spec" (
    del /q *.spec
)

REM Create mods folder if not exists
if not exist "mods" (
    echo Creating mods folder...
    mkdir mods
)

echo.
echo Building server executable...
pyinstaller --onefile ^
    --windowed ^
    --name "MinecraftModsSync_Server" ^
    --add-data "mods;mods" ^
    --hidden-import "uvicorn" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols" ^
    --hidden-import "uvicorn.protocols.http" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "uvicorn.protocols.websockets" ^
    --hidden-import "uvicorn.protocols.websockets.auto" ^
    --hidden-import "uvicorn.lifespan" ^
    --hidden-import "uvicorn.lifespan.on" ^
    --collect-all uvicorn ^
    --collect-all fastapi ^
    --noconfirm ^
    server_gui.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Build completed successfully!
    echo   Executable: dist\MinecraftModsSync_Server.exe
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Copy dist\MinecraftModsSync_Server.exe to desired location
    echo 2. Create a "mods" folder next to the .exe
    echo 3. Add your .jar mods to the mods folder
    echo 4. Run MinecraftModsSync_Server.exe
) else (
    echo.
    echo ========================================
    echo   Build failed! Check errors above.
    echo ========================================
)

echo.
pause
