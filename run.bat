@echo off
chcp 65001 >nul
title Universal CAN Dashboard

REM Python barmy barla
python --version >nul 2>&1
if errorlevel 1 (
    echo [YALNYSHLYK] Python tapylmady! setup.bat islet.
    pause
    exit /b 1
)

cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Yalnyshlyk! setup.bat islet.
    pause
)
