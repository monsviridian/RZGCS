@echo off
echo RZGCS Windows Installer
echo ======================
echo.

REM Prüfe Administrator-Rechte
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrator-Rechte bestatigt.
) else (
    echo FEHLER: Dieses Skript benötigt Administrator-Rechte!
    echo Bitte als Administrator ausführen.
    pause
    exit /b 1
)

REM Setze Installationspfad
set "INSTALL_PATH=%ProgramFiles%\RZGCS"

echo Erstelle Installationsverzeichnis...
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"

echo Kopiere RZGCS-Dateien...
xcopy "dist\RZGCS\*" "%INSTALL_PATH%\" /E /I /Y

echo Erstelle Startmenü-Verknüpfung...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\RZGCS"
if not exist "%START_MENU%" mkdir "%START_MENU%"

REM Erstelle Verknüpfung mit PowerShell
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\RZGCS.lnk'); $Shortcut.TargetPath = '%INSTALL_PATH%\RZGCS.exe'; $Shortcut.WorkingDirectory = '%INSTALL_PATH%'; $Shortcut.IconLocation = '%INSTALL_PATH%\RZGCS.exe,0'; $Shortcut.Save()"

echo.
echo RZGCS wurde erfolgreich installiert!
echo Installationsverzeichnis: %INSTALL_PATH%
echo Startmenü-Verknüpfung erstellt!
echo.
echo Sie können RZGCS jetzt über das Startmenü starten.
echo.
pause 