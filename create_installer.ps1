# RZGCS Windows Installer Script
param(
    [string]$InstallPath = "$env:ProgramFiles\RZGCS"
)

Write-Host "RZGCS Windows Installer" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# Prüfe Administrator-Rechte
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Dieses Skript benötigt Administrator-Rechte!" -ForegroundColor Red
    Write-Host "Bitte PowerShell als Administrator ausführen." -ForegroundColor Red
    exit 1
}

# Erstelle Installationsverzeichnis
Write-Host "Erstelle Installationsverzeichnis..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null

# Kopiere Dateien
Write-Host "Kopiere RZGCS-Dateien..." -ForegroundColor Yellow
Copy-Item -Path "dist\RZGCS\*" -Destination $InstallPath -Recurse -Force

# Erstelle Startmenü-Verknüpfung
Write-Host "Erstelle Startmenü-Verknüpfung..." -ForegroundColor Yellow
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\RZGCS"
New-Item -ItemType Directory -Force -Path $StartMenuPath | Out-Null

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$StartMenuPath\RZGCS.lnk")
$Shortcut.TargetPath = "$InstallPath\RZGCS.exe"
$Shortcut.WorkingDirectory = $InstallPath
$Shortcut.IconLocation = "$InstallPath\RZGCS.exe,0"
$Shortcut.Save()

# Erstelle Desktop-Verknüpfung (optional)
$CreateDesktopShortcut = Read-Host "Desktop-Verknüpfung erstellen? (j/n)"
if ($CreateDesktopShortcut -eq "j" -or $CreateDesktopShortcut -eq "J") {
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\RZGCS.lnk")
    $Shortcut.TargetPath = "$InstallPath\RZGCS.exe"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.IconLocation = "$InstallPath\RZGCS.exe,0"
    $Shortcut.Save()
    Write-Host "Desktop-Verknüpfung erstellt!" -ForegroundColor Green
}

# Erstelle Deinstallations-Skript
$UninstallScript = @"
# RZGCS Deinstallations-Skript
Write-Host "Deinstalliere RZGCS..." -ForegroundColor Yellow

# Entferne Startmenü-Verknüpfung
Remove-Item -Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\RZGCS" -Recurse -Force -ErrorAction SilentlyContinue

# Entferne Desktop-Verknüpfung
Remove-Item -Path "$env:USERPROFILE\Desktop\RZGCS.lnk" -Force -ErrorAction SilentlyContinue

# Entferne Installationsverzeichnis
Remove-Item -Path "$InstallPath" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "RZGCS wurde erfolgreich deinstalliert!" -ForegroundColor Green
"@

$UninstallScript | Out-File -FilePath "$InstallPath\uninstall.ps1" -Encoding UTF8

Write-Host "`nRZGCS wurde erfolgreich installiert!" -ForegroundColor Green
Write-Host "Installationsverzeichnis: $InstallPath" -ForegroundColor Cyan
Write-Host "Startmenü-Verknüpfung erstellt!" -ForegroundColor Cyan
Write-Host "`nSie können RZGCS jetzt über das Startmenü oder Desktop starten." -ForegroundColor Green 