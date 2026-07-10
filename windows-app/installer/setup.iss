#define AppName "水印清除助手"
#define AppVersion "1.0.2"
#define AppPublisher "疯狂 AIGC 商业视觉"
#define AppExeName "WatermarkHelper.exe"

[Setup]
AppId={{8BCAD5AC-5C7A-40AF-90D4-8A539EC8E80C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=..\release
OutputBaseFilename={#AppName}-安装程序-v{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "..\dist\WatermarkHelper\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "创建桌面图标"; GroupDescription: "其他选项："; Flags: unchecked

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "立即打开 {#AppName}"; Flags: nowait postinstall skipifsilent
