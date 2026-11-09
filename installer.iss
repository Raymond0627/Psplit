; Script generated for Inno Setup (optional, to generate an installer .exe)
[Setup]
AppName=Lumeed QSplit
AppVersion=1.0.0
DefaultDirName={autopf}\Lumeed QSplit
DefaultGroupName=Lumeed QSplit
OutputDir=dist\installer
OutputBaseFilename=Lumeed_QSplit_Setup
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Lumeed_QSplit\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Lumeed QSplit"; Filename: "{app}\Lumeed_QSplit.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\Lumeed QSplit"; Filename: "{app}\Lumeed_QSplit.exe"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\Lumeed_QSplit.exe"; Description: "{cm:LaunchProgram,Lumeed QSplit}"; Flags: nowait postinstall skipifsilent
