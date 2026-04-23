@echo off
chcp 65001 >nul
title CAN Dashboard -- Build Installer (setup.exe)
color 0A
echo.
echo  =====================================================
echo   Toyota CAN Dashboard -- Installer Builder
echo  =====================================================
echo.

cd /d "%~dp0.."

REM ── Step 1: Build EXE first ─────────────────────────────────────────────────
if not exist "dist\CAN_Dashboard\CAN_Dashboard.exe" (
    echo  [Step 1] Building EXE first...
    call scripts\build_exe.bat
    if errorlevel 1 exit /b 1
) else (
    echo  [Step 1] EXE already built: dist\CAN_Dashboard\CAN_Dashboard.exe
)

REM ── Step 2: Find Inno Setup ─────────────────────────────────────────────────
echo.
echo  [Step 2] Looking for Inno Setup...

set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set ISCC=C:\Program Files\Inno Setup 6\ISCC.exe

if "%ISCC%"=="" (
    echo.
    echo  [ERROR] Inno Setup 6 not found!
    echo.
    echo  Please download and install Inno Setup 6 from:
    echo    https://jrsoftware.org/isdl.php
    echo.
    echo  Then run this script again.
    echo.
    echo  ── Alternative (no installer needed) ─────────────────────────────
    echo  You can also distribute the folder directly:
    echo    dist\CAN_Dashboard\
    echo  Copy this folder to any Windows PC and run CAN_Dashboard.exe
    echo  No Python or installation needed!
    echo  ──────────────────────────────────────────────────────────────────
    pause
    exit /b 1
)
echo  [OK] Found: %ISCC%

REM ── Step 3: Compile installer ───────────────────────────────────────────────
echo.
echo  [Step 3] Compiling installer...
"%ISCC%" installer.iss

if errorlevel 1 (
    echo.
    echo  [ERROR] Installer build failed!
    pause
    exit /b 1
)

REM ── Done ────────────────────────────────────────────────────────────────────
echo.
echo  =====================================================
echo   [OK] INSTALLER READY!
echo.
echo   File: dist\CAN_Dashboard_Setup.exe
echo.
echo   Send this single file to any Windows PC.
echo   The recipient just double-clicks it to install.
echo   No Python needed!
echo  =====================================================
echo.
explorer dist
pause
