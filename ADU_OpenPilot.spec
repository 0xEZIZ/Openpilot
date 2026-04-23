# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file -- ADU OpenPilot standalone with Splash and Sound
# Usage: pyinstaller ADU_OpenPilot.spec

import os
import glob as _glob

block_cipher = None

BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

# ── Data files (DBC, Sound, Logo) ─────────────────────────────────────────────
added_files = []

# Root DBC files
for dbc in _glob.glob(os.path.join(BASE_DIR, '*.dbc')):
    added_files.append((dbc, '.'))

# dbc_files subfolder
dbc_sub = os.path.join(BASE_DIR, 'dbc_files')
if os.path.isdir(dbc_sub):
    for dbc in _glob.glob(os.path.join(dbc_sub, '*.dbc')):
        added_files.append((dbc, 'dbc_files'))

# Sound, Logo, and Font assets (skip if missing to avoid build failure)
for asset in ['ENGINE BMW.wav', 'logo (2).jpg', 'Quantum.otf']:
    asset_path = os.path.join(BASE_DIR, 'assets', asset)
    if os.path.isfile(asset_path):
        added_files.append((asset_path, 'assets'))
    else:
        print(f"WARNING: asset not found, skipping: {asset}")

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    ['main.py'],
    pathex=[BASE_DIR],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'can',
        'can.interfaces',
        'can.interfaces.ixxat',
        'can.interfaces.ixxat.canlib',
        'can.interfaces.ixxat.canlib_vcinpl',
        'can.interfaces.ixxat.canlib_vcinpl2',
        'can.interfaces.socketcan',
        'can.interfaces.pcan',
        'can.interfaces.pcan.pcan',
        'can.interfaces.vector',
        'can.interfaces.virtual',
        'can.interfaces.slcan',
        'can.interfaces.kvaser',
        'can.interfaces.kvaser.canlib',
        'can.interfaces.gs_usb',
        'can.interfaces.cantact',
        'cantools',
        'cantools.database',
        'cantools.database.can',
        'cantools.database.can.database',
        'cantools.database.can.message',
        'cantools.database.can.signal',
        'cantools.subparsers',
        'textparser',
        'bitstruct',
        'crccheck',
        'crccheck.crc',
        'diskcache',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.font',
        'threading',
        'queue',
        'struct',
        'math',
        'time',
        'os',
        'sys',
        'json',
        'logging',
        'collections',
        'functools',
        'ctypes',
        'ctypes.wintypes',
        'winsound',
        'socket',
        'shutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'cv2',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── One-file build (Highly portable) ──────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ADU_OpenPilot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # no terminal window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico',
)
