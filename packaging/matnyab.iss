; Inno Setup script for the Matnyab Windows installer.
; Built by packaging/build.py, which passes AppVersion and stages the files.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6E2B8A43-4C1D-4F57-9C3E-7A1B5D9E0F21}
AppName=Matnyab
AppVersion={#AppVersion}
AppVerName=Matnyab {#AppVersion}
AppPublisher=Ehsan Aliverdi
AppPublisherURL=https://github.com/EhsanAliverdi/matnyab
AppSupportURL=https://github.com/EhsanAliverdi/matnyab/issues
DefaultDirName={autopf}\Matnyab
DefaultGroupName=Matnyab
DisableProgramGroupPage=yes
; Lets the user choose "only for me" (no admin needed) or "all users"
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=Matnyab-Setup-{#AppVersion}
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\Matnyab.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\Matnyab\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\build\stage\tesseract\*"; DestDir: "{app}\tesseract"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\build\stage\poppler\*"; DestDir: "{app}\poppler"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Matnyab"; Filename: "{app}\Matnyab.exe"
Name: "{autodesktop}\Matnyab"; Filename: "{app}\Matnyab.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Matnyab.exe"; Description: "{cm:LaunchProgram,Matnyab}"; Flags: nowait postinstall skipifsilent
