@echo off
REM =====================================================================
REM  Khata Dalo - Windows Build Script
REM  Packages the PyQt6 app into a single standalone KhataDalo.exe
REM  Requires: Python 3.10+ installed and on PATH.
REM =====================================================================

echo.
echo ============================================
echo   Khata Dalo - Build Script
echo ============================================
echo.

REM 1. Create/activate a virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

REM 2. Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM 3. Clean previous build artifacts
echo Cleaning previous build...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q KhataDaloPOS.spec 2>nul

REM 4. Run PyInstaller
echo Building KhataDalo.exe ...
pyinstaller ^
    --name "KhataDalo" ^
    --onefile ^
    --windowed ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "PyQt6.sip" ^
    main.py

echo.
if exist dist\KhataDalo.exe (
    echo ============================================
    echo   BUILD SUCCESSFUL
    echo   Output: dist\KhataDalo.exe
    echo ============================================
) else (
    echo ============================================
    echo   BUILD FAILED - check the log above
    echo ============================================
)

pause
