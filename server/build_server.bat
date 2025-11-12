@echo off
echo ========================================
echo   Building Minecraft Mods Sync Server
echo ========================================
echo.

REM Activate virtual environment
call ..\.venv\Scripts\activate.bat

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building server executable...
pyinstaller --onefile ^
    --windowed ^
    --name "MinecraftModsSync_Server" ^
    --icon=NONE ^
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
    server_gui.py

echo.
echo ========================================
echo   Build completed!
echo   Executable: dist\MinecraftModsSync_Server.exe
echo ========================================
pause
