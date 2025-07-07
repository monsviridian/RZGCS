[Setup]
AppName=RZGCS
AppVersion=1.0
AppPublisher=RZ Solutions
AppPublisherURL=https://rz-solutions.de
AppSupportURL=https://rz-solutions.de
AppUpdatesURL=https://rz-solutions.de
DefaultDirName={autopf}\RZGCS
DefaultGroupName=RZGCS
AllowNoIcons=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=RZGCS_Setup
SetupIconFile=RZGCSContent\Assets\logo_base.png
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\RZGCS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\RZGCS"; Filename: "{app}\RZGCS.exe"
Name: "{group}\{cm:UninstallProgram,RZGCS}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\RZGCS"; Filename: "{app}\RZGCS.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RZGCS.exe"; Description: "{cm:LaunchProgram,RZGCS}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end; 