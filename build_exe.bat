@echo off
echo Installing requirements...
venv\Scripts\pip install -r requirements.txt

echo Cleaning up previous builds...
rmdir /s /q build
rmdir /s /q dist
del /q EyeProtector.spec
del /q EyeProtector.exe

echo Building Single EXE...
venv\Scripts\pyinstaller --noconfirm --onefile --windowed --name "EyeProtector" --distpath . --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets main.py

echo Cleaning up build artifacts...
rmdir /s /q build
del /q EyeProtector.spec

echo Build Complete!
echo You can find EyeProtector.exe in the current directory.
pause
