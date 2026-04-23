@echo off
chcp 65001 >nul
title CAN Dashboard - Gurnamak
color 0A
echo.
echo  =====================================================
echo   Universal CAN Dashboard - Gurnamak
echo  =====================================================
echo.

REM ── 1. Python barmy? ─────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [YALNYSHLYK] Python tapylmady!
    echo.
    echo  python.org-dan 3.10+ yukle we yeniden caly shdy r.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i tapyldy

REM ── 2. pip bar my? ────────────────────────────────────
pip --version >nul 2>&1
if errorlevel 1 (
    echo [YALNYSHLYK] pip tapylmady!
    pause
    exit /b 1
)
echo [OK] pip tapyldy

REM ── 3. Gerekli kutuphaneleri gur ─────────────────────
echo.
echo  Kutuphaneler gurulyar...
pip install python-can cantools --quiet
if errorlevel 1 (
    echo [YALNYSHLYK] Kutuphaneler gurunmady!
    echo  Internet baglanysyny barla.
    pause
    exit /b 1
)
echo [OK] python-can, cantools gurundy

REM ── 4. PyInstaller gur (.exe ucin) ───────────────────
echo.
echo  PyInstaller gurulyar (bu .exe yasamak ucin gerek)...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [DUYDURYS] PyInstaller gurunmady - .exe yapyp bolmaz
    echo  Yone run.bat bilen ishlap bilersin!
) else (
    echo [OK] PyInstaller gurundy
)

REM ── 5. IXXAT driver barmy? (yalnyz maglumat) ─────────
echo.
echo  IXXAT driver barlagy...
reg query "HKLM\SOFTWARE\IXXAT" >nul 2>&1
if errorlevel 1 (
    echo [DUYDURYS] IXXAT driver tapylmady
    echo  Real masyn ucin IXXAT surucusini gur.
    echo  Demo mod ucin gerek dal.
) else (
    echo [OK] IXXAT driver bar
)

echo.
echo  =====================================================
echo   Gurnamak tamamlandy!
echo.
echo   Isletmek:  run.bat         (normal mod)
echo              run_demo.bat    (demo mod, hardware gerek dal)
echo              build_exe.bat   (.exe yasamak)
echo  =====================================================
echo.
pause
