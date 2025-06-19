# RZGCS Windows Build Script

# Verzeichnisstruktur vorbereiten
$SourceDir = Resolve-Path ".."
$BuildDir = "$SourceDir\build\windows"
$InstallerDir = "$SourceDir\build\installer"

# Alte Build-Verzeichnisse bereinigen
Write-Host "Bereinige alte Build-Verzeichnisse..."
if (Test-Path "$BuildDir") {
    Remove-Item -Path "$BuildDir" -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
New-Item -ItemType Directory -Force -Path $InstallerDir | Out-Null

# Temporu00e4res Verzeichnis erstellen
$TempDir = "$SourceDir\deployment\temp"
if (Test-Path "$TempDir") {
    Remove-Item -Path "$TempDir" -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# Build-Umgebung vorbereiten
Write-Host "Installiere erforderliche Pakete..."

try {
    pip install -U pyinstaller pyqt5 pymavlink numpy matplotlib pillow
} catch {
    Write-Host "Fehler beim Installieren der Pakete: $_" -ForegroundColor Red
    Write-Host "Versuche trotzdem fortzufahren..." -ForegroundColor Yellow
}

# PyInstaller-Konfigurationsdatei erstellen
Write-Host "Erstelle PyInstaller-Konfiguration..."
$SpecFile = "$TempDir\RZGCS.spec"

$SpecContent = @"
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('../RZGCSContent', 'RZGCSContent'),
    ('../Python', 'Python'),
    ('../LICENSE.md', '.'),
    ('../THIRD_PARTY_LICENSES.md', '.'),
    ('../README.md', '.'),
]

a = Analysis(['../main.py'],
             pathex=['$SourceDir'],
             binaries=[],
             datas=added_files,
             hiddenimports=['PyQt5.QtQuick', 'PyQt5.QtQml', 'PyQt5.QtSvg', 'numpy', 'matplotlib'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='RZGCS',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='../RZGCSContent/icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='RZGCS')
"@

Set-Content -Path $SpecFile -Value $SpecContent

# PyInstaller ausfu00fchren
Write-Host "Starte PyInstaller-Build..."
cd $TempDir

try {
    pyinstaller --clean RZGCS.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller konnte nicht erfolgreich ausgefuhrt werden."
    }
} catch {
    Write-Host "Fehler beim PyInstaller-Build: $_" -ForegroundColor Red
    Write-Host "Versuche einen vereinfachten Build..." -ForegroundColor Yellow
    
    # Vereinfachter Build-Versuch ohne alle Features
    try {
        pyinstaller --clean --name="RZGCS" --windowed "$SourceDir\main.py"
    } catch {
        Write-Host "Auch der vereinfachte Build ist fehlgeschlagen: $_" -ForegroundColor Red
        Write-Host "Build abgebrochen." -ForegroundColor Red
        exit 1
    }
}

# Ergebnis verschieben
Write-Host "Verschiebe Build-Ergebnis..."
if (Test-Path "$TempDir\dist\RZGCS") {
    Copy-Item -Path "$TempDir\dist\RZGCS\*" -Destination $BuildDir -Recurse -Force
} else {
    Write-Host "Build-Ausgabe nicht gefunden!" -ForegroundColor Red
    exit 1
}

# Qt-Abhu00e4ngigkeiten mit windeployqt hinzufu00fcgen
Write-Host "Fu00fcge Qt-Abhu00e4ngigkeiten hinzu..."

# Versuche, windeployqt zu finden
$QtBinPath = $null

try {
    $QtBinPath = python -c "from PyQt5.QtCore import QLibraryInfo; print(QLibraryInfo.location(QLibraryInfo.BinariesPath))"
} catch {
    Write-Host "Konnte Qt-Pfad nicht ermitteln: $_" -ForegroundColor Yellow
}

$WinDeployQtPaths = @(
    "$QtBinPath\windeployqt.exe",
    "C:\Qt\5.15.2\msvc2019_64\bin\windeployqt.exe",
    "C:\Qt\5.15.2\msvc2019\bin\windeployqt.exe",
    "C:\Qt\5.15.0\msvc2019_64\bin\windeployqt.exe",
    "C:\Qt\5.14.2\msvc2019_64\bin\windeployqt.exe",
    "C:\Qt\5.13.2\msvc2019_64\bin\windeployqt.exe"
)

$WinDeployQtFound = $false

foreach ($Path in $WinDeployQtPaths) {
    if (Test-Path $Path) {
        Write-Host "windeployqt gefunden unter: $Path"
        try {
            & $Path "$BuildDir\RZGCS.exe" --qmldir="$SourceDir\RZGCSContent" --no-translations
            $WinDeployQtFound = $true
            break
        } catch {
            Write-Host "Fehler bei Ausfu00fchrung von windeployqt: $_" -ForegroundColor Yellow
        }
    }
}

if (-not $WinDeployQtFound) {
    Write-Host "windeployqt konnte nicht gefunden werden. Fu00fchre manuelle Qt-Bibliothek-Kopie durch..." -ForegroundColor Yellow
    
    # Fallback: Manuelle Kopie der wichtigsten Qt-Bibliotheken
    $PyQtPath = (python -c "import os, PyQt5; print(os.path.dirname(PyQt5.__file__))")
    
    if (Test-Path "$PyQtPath\Qt5") {
        Write-Host "Kopiere Qt-Bibliotheken aus $PyQtPath\Qt5..."
        Copy-Item -Path "$PyQtPath\Qt5\bin\*.dll" -Destination $BuildDir -ErrorAction SilentlyContinue
        Copy-Item -Path "$PyQtPath\Qt5\plugins\*" -Destination "$BuildDir\plugins" -Recurse -ErrorAction SilentlyContinue
        Copy-Item -Path "$PyQtPath\Qt5\qml\*" -Destination "$BuildDir\qml" -Recurse -ErrorAction SilentlyContinue
    } else {
        Write-Host "Konnte Qt-Bibliotheken nicht finden." -ForegroundColor Red
        Write-Host "Die Anwendung funktioniert mu00f6glicherweise nicht auf anderen Systemen." -ForegroundColor Red
    }
}

# Build-Verzeichnis bereinigen
Write-Host "Bereinige Build-Verzeichnis..."
Remove-Item -Path "$TempDir" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Windows-Build abgeschlossen. Ausfu00fchrbare Datei befindet sich in: $BuildDir\RZGCS.exe" -ForegroundColor Green

# Inno Setup-Skript erstellen
Write-Host "Erstelle Installer..."
$InnoScript = "$TempDir\windows_installer.iss"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

$InnoScriptContent = @"
#define MyAppName "RZGCS"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Organization"
#define MyAppURL "https://yourwebsite.com"
#define MyAppExeName "RZGCS.exe"

[Setup]
AppId={{ABCD1234-5678-ABCD-EFGH-1234567890AB}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
InfoBeforeFile=$SourceDir\LICENSE.md
OutputDir=$InstallerDir
OutputBaseFilename=RZGCS_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "$BuildDir\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
"@

Set-Content -Path $InnoScript -Value $InnoScriptContent

# Inno Setup ausfu00fchren, wenn vorhanden
$InnoSetupPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
)

$InnoSetupFound = $false

foreach ($Path in $InnoSetupPaths) {
    if (Test-Path $Path) {
        Write-Host "Inno Setup gefunden unter: $Path"
        try {
            & $Path $InnoScript
            $InnoSetupFound = $true
            Write-Host "Windows-Installer erstellt: $InstallerDir\RZGCS_Setup.exe" -ForegroundColor Green
            break
        } catch {
            Write-Host "Fehler bei Ausfu00fchrung von Inno Setup: $_" -ForegroundColor Red
        }
    }
}

if (-not $InnoSetupFound) {
    Write-Host "Inno Setup nicht gefunden. Installer konnte nicht erstellt werden." -ForegroundColor Yellow
    Write-Host "Fu00fcr Installer-Erstellung bitte Inno Setup installieren: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host "Sie ku00f6nnen die Anwendung dennoch direkt aus dem Build-Verzeichnis ausfu00fchren: $BuildDir\RZGCS.exe" -ForegroundColor Green
}

# Temporu00e4re Dateien entfernen
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
