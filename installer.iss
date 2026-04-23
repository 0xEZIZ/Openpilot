; Inno Setup 6 script -- ADU OpenPilot CAN Dashboard Installer
; Download Inno Setup: https://jrsoftware.org/isdl.php
; Build: pyinstaller ADU_OpenPilot.spec  THEN  compile this .iss

#define AppName      "ADU OpenPilot"
#define AppVersion   "1.0"
#define AppPublisher "ADU Project"
#define AppExeName   "ADU_OpenPilot.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=CAN_Dashboard_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#AppName}
; No admin required -- installs to user AppData if not admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
; Main EXE (onefile build)
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Include bundled DBC files so user has them next to EXE
Source: "dbc_files\*.dbc"; DestDir: "{app}\dbc_files"; Flags: ignoreversion skipifsourcedoesntexist

[Dirs]
; Create dbc_files directory (user can add their own DBC files here)
Name: "{app}\dbc_files"

[Icons]
; Start Menu
Name: "{group}\{#AppName}";         Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
; Desktop shortcut (optional)
Name: "{autodesktop}\{#AppName}";   Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
