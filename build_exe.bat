@echo off
chcp 65001 >nul
title CAN Dashboard -- Build EXE
color 0B
echo.
echo  =====================================================
echo   Toyota CAN Dashboard -- .EXE Builder
echo  =====================================================
echo.

cd /d "%~dp0"

REM ── Venv Python ─────────────────────────────────────────────────────────────
set PYTHON=%~dp0venv\Scripts\python.exe
if not exist "%PYTHON%" (
    echo [ERROR] venv not found: %PYTHON%
    echo Run setup.bat first to create the virtual environment.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('"%PYTHON%" --version') do echo [OK] %%i

REM ── Install PyInstaller if missing ──────────────────────────────────────────
"%PYTHON%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INSTALL] Installing PyInstaller...
    "%PYTHON%" -m pip install pyinstaller --quiet
    if errorlevel 1 (
        echo [ERROR] PyInstaller could not be installed!
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('"%PYTHON%" -m PyInstaller --version') do echo [OK] PyInstaller %%i

REM ── Clean old build ─────────────────────────────────────────────────────────
echo.
echo  Cleaning previous build...
if exist "dist\CAN_Dashboard" rmdir /s /q "dist\CAN_Dashboard" 2>nul
if exist "build"              rmdir /s /q "build"              2>nul

REM ── Build EXE ───────────────────────────────────────────────────────────────
echo.
echo  Building... (this may take 2-4 minutes)
echo.
"%PYTHON%" -m PyInstaller toyota_can.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check the log above.
    pause
    exit /b 1
)

REM ── Verify output ───────────────────────────────────────────────────────────
if not exist "dist\CAN_Dashboard\CAN_Dashboard.exe" (
    echo [ERROR] CAN_Dashboard.exe not found in dist\CAN_Dashboard\
    pause
    exit /b 1
)

REM ── Create launcher shortcut in dist root ────────────────────────────────────
echo.
echo  Creating Run.bat launcher...
(
  echo @echo off
  echo start "" "%~dp0CAN_Dashboard\CAN_Dashboard.exe"
) > "dist\Run_CAN_Dashboard.bat"

REM ── Done ────────────────────────────────────────────────────────────────────
echo.
echo  =====================================================
echo   [OK] BUILD COMPLETE!
echo.
echo   Location : dist\CAN_Dashboard\
echo   Main EXE : dist\CAN_Dashboard\CAN_Dashboard.exe
echo.
echo   TO DEPLOY on another PC:
echo     Copy the entire  dist\CAN_Dashboard\  folder.
echo     Double-click CAN_Dashboard.exe to run.
echo     No Python needed!
echo.
echo   OR: Run  build_installer.bat  to create setup.exe
echo       (requires Inno Setup 6 to be installed)
echo  =====================================================
echo.

REM ── Open dist folder ────────────────────────────────────────────────────────
explorer "dist\CAN_Dashboard"
pause
