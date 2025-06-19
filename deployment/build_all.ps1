# RZGCS Multi-Plattform Build Script

# Verzeichnisstruktur erstellen
$BuildRoot = "..\build"
New-Item -ItemType Directory -Force -Path $BuildRoot
New-Item -ItemType Directory -Force -Path "$BuildRoot\installer"

Write-Host "============================================"
Write-Host "RZGCS Deployment-Tool fu00fcr alle Plattformen"
Write-Host "============================================"
Write-Host ""
Write-Host "Wu00e4hlen Sie die Zielplattform:"
Write-Host "1. Windows (aktuelles System)"
Write-Host "2. macOS (erfordert macOS)"
Write-Host "3. Linux (erfordert Linux)"
Write-Host "4. Raspberry Pi OS (erfordert Raspberry Pi oder Cross-Compiling)"
Write-Host "5. Alle verfu00fcgbaren Plattformen"
Write-Host ""

$choice = Read-Host "Geben Sie Ihre Wahl ein (1-5)"

switch ($choice) {
    "1" {
        Write-Host "Starte Windows-Deployment..."
        . ".\build_windows.ps1"
    }
    "2" {
        Write-Host "macOS-Deployment kann nur auf einem macOS-System ausgefu00fchrt werden."
        Write-Host "Wenn Sie auf macOS sind, fu00fchren Sie bitte folgendes aus:"
        Write-Host "chmod +x ./build_macos.sh"
        Write-Host "./build_macos.sh"
    }
    "3" {
        Write-Host "Linux-Deployment kann nur auf einem Linux-System ausgefu00fchrt werden."
        Write-Host "Wenn Sie auf Linux sind, fu00fchren Sie bitte folgendes aus:"
        Write-Host "chmod +x ./build_linux.sh"
        Write-Host "./build_linux.sh"
    }
    "4" {
        Write-Host "Raspberry Pi OS-Deployment sollte auf einem Raspberry Pi ausgefu00fchrt werden."
        Write-Host "Wenn Sie auf einem Raspberry Pi sind, fu00fchren Sie bitte folgendes aus:"
        Write-Host "chmod +x ./build_raspberrypi.sh"
        Write-Host "./build_raspberrypi.sh"
    }
    "5" {
        Write-Host "Starte Deployment fu00fcr alle verfu00fcgbaren Plattformen..."
        
        # Windows (kann auf aktueller Plattform ausgefu00fchrt werden)
        Write-Host "Starte Windows-Deployment..."
        . ".\build_windows.ps1"
        
        # Andere Plattformen erfordern ihre jeweiligen Betriebssysteme
        Write-Host ""
        Write-Host "Deployment fu00fcr andere Plattformen erfordert die jeweiligen Betriebssysteme."
        Write-Host "Fu00fcr macOS: chmod +x ./build_macos.sh && ./build_macos.sh"
        Write-Host "Fu00fcr Linux: chmod +x ./build_linux.sh && ./build_linux.sh"
        Write-Host "Fu00fcr Raspberry Pi: chmod +x ./build_raspberrypi.sh && ./build_raspberrypi.sh"
    }
    default {
        Write-Host "Ungu00fcltige Auswahl. Beenden."
    }
}

Write-Host ""
Write-Host "============================================"
Write-Host "Deployment-Prozess abgeschlossen"
Write-Host "============================================"

Write-Host ""
Write-Host "Installationsdateien (falls erstellt) befinden sich in: $BuildRoot\installer"
Write-Host "Darin ku00f6nnen enthalten sein:"
Write-Host "- Windows: RZGCS_Setup.exe"
Write-Host "- macOS: RZGCS_Installer.dmg"
Write-Host "- Linux: RZGCS-x86_64.AppImage und RZGCS_1.0-1_amd64.deb"
Write-Host "- Raspberry Pi: RZGCS-RaspberryPi.tar.gz"
