@echo off
echo ========================================
echo  Dang dong goi Minecraft Mods Sync Client
echo ========================================
echo.

REM Xoa thu muc build cu
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist client.spec del client.spec

echo [1/3] Bat dau dong goi...
pyinstaller --onefile --windowed --icon=NONE --name="MinecraftModsSync" --add-data="config.json;." client.py

echo.
echo [2/3] Kiem tra ket qua...
if exist "dist\MinecraftModsSync.exe" (
    echo [3/3] Thanh cong! File EXE da duoc tao tai: dist\MinecraftModsSync.exe
    echo.
    echo ========================================
    echo  HOAN TAT!
    echo ========================================
    echo File: dist\MinecraftModsSync.exe
    echo Kich thuoc: 
    dir "dist\MinecraftModsSync.exe" | find "MinecraftModsSync.exe"
) else (
    echo [3/3] LOI: Khong tim thay file EXE
)

echo.
pause
