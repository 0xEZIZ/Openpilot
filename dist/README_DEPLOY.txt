======================================================
  Toyota CAN Dashboard -- Deployment Guide
======================================================

METHOD 1: Portable (no installation needed)
--------------------------------------------
1. Copy the entire "CAN_Dashboard" folder to any Windows PC.
2. Double-click  CAN_Dashboard\CAN_Dashboard.exe  to run.
   No Python, no installation required!

METHOD 2: Installer (setup.exe)
--------------------------------
1. Install Inno Setup 6 (free):  https://jrsoftware.org/isdl.php
2. Go back to the project folder.
3. Double-click  build_installer.bat
4. This creates  dist\CAN_Dashboard_Setup.exe
5. Send that single setup file to anyone.
   They just double-click to install like any normal program.

DEMO MODE (no CAN hardware needed)
------------------------------------
Run from command line:
  CAN_Dashboard.exe --demo

HARDWARE NOTE
--------------
To use with real CAN hardware:
  - IXXAT USB-to-CAN:  Install IXXAT VCI driver (from ixxat.com)
  - PCAN USB:          Install PCAN driver (from peak-system.com)
  - The program auto-detects connected adapters.

======================================================
