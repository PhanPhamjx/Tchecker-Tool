@echo off
echo Building Unity Texture Checker...

pyinstaller --noconfirm --onefile --windowed --icon "icon/iconT.jpg" --add-data "data;data" --add-data "modules;modules" --add-data "ui;ui" --name "Unity Texture Checker" main.py

echo.
echo Build complete! The executable is in the 'dist' folder.
echo.
pause 