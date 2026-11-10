; Script generated for Inno Setup to generate Folio Setup .exe
[Setup]
AppName=Folio
AppVersion=1.2.0
DefaultDirName={autopf}\Folio
DefaultGroupName=Folio
OutputDir=dist\installer
OutputBaseFilename=Folio_Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\icon.ico
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Folio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Folio"; Filename: "{app}\Folio.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\Folio"; Filename: "{app}\Folio.exe"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\Folio.exe"; Description: "{cm:LaunchProgram,Folio}"; Flags: nowait postinstall skipifsilent
