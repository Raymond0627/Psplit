; Script generated for Inno Setup to generate an installer .exe
[Setup]
AppName=Lumeed Psplit
AppVersion=1.1.0
DefaultDirName={autopf}\Lumeed Psplit
DefaultGroupName=Lumeed Psplit
OutputDir=dist\installer
OutputBaseFilename=Lumeed_Psplit_Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\icon.ico
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Lumeed_Psplit\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Lumeed Psplit"; Filename: "{app}\Lumeed_Psplit.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\Lumeed Psplit"; Filename: "{app}\Lumeed_Psplit.exe"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\Lumeed_Psplit.exe"; Description: "{cm:LaunchProgram,Lumeed Psplit}"; Flags: nowait postinstall skipifsilent
