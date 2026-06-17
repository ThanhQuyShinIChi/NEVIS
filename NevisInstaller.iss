#define MyAppName "NEVIS MEP"
#define MyAppVersion "2.02"
#define MyAppPublisher "NewVision"
#define MyAppExeName "Nevis.exe"

[Setup]
AppId={{6E40459B-09B0-4607-88B8-1B0B0E4F3E4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={sd}\NEVIS MEP
DefaultGroupName=NEVIS MEP
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=NEVIS_MEP_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=Ico\icon_tan.ico
UninstallDisplayIcon={app}\Nevis.exe

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
Source: "release\NEVIS_MEP\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: users-modify

[Icons]
Name: "{group}\NEVIS MEP"; Filename: "{app}\Nevis.exe"; WorkingDir: "{app}"
Name: "{group}\NEVIS Library Editor"; Filename: "{app}\Nevis_Library_Editor.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\NEVIS MEP"; Filename: "{app}\Nevis.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\tools\create_install_marker.ps1"" -AppDir ""{app}"" -ProgramDataDir ""{commonappdata}\NEVIS MEP"""; Flags: runhidden waituntilterminated
Filename: "{app}\Nevis.exe"; Description: "Launch NEVIS MEP"; Flags: nowait postinstall skipifsilent
