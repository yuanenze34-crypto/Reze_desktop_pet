@echo off
setlocal
cd /d "%~dp0"
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --onedir --name RezeDesktopPet --add-data "assets/reze;assets/reze" --add-data "config;config" main.py
if errorlevel 1 exit /b 1
echo Ready: dist\RezeDesktopPet\RezeDesktopPet.exe
