@echo off
echo RZ Ground Control Station Installation und Startskript
echo ====================================================

echo Erstelle Installationspaket...

:: Erstelle Verzeichnisstruktur
if not exist "build\RZGCS" mkdir "build\RZGCS"
if not exist "build\RZGCS\Python" mkdir "build\RZGCS\Python"
if not exist "build\RZGCS\RZGCSContent" mkdir "build\RZGCS\RZGCSContent"
if not exist "build\RZGCS\Assets" mkdir "build\RZGCS\Assets"

:: Kopiere Python-Dateien
echo Kopiere Python-Code...
xcopy /E /Y /I "Python" "build\RZGCS\Python"

:: Kopiere UI-Dateien
echo Kopiere UI-Dateien...
xcopy /E /Y /I "RZGCSContent" "build\RZGCS\RZGCSContent"

:: Kopiere Assets
echo Kopiere Assets...
xcopy /E /Y /I "Assets" "build\RZGCS\Assets"

:: Kopiere Dokumentation
echo Kopiere Dokumentation...
copy "README.md" "build\RZGCS\"
copy "INSTALL.md" "build\RZGCS\"
copy "requirements.txt" "build\RZGCS\"

:: Erstelle Startskript
echo @echo off > "build\RZGCS\start_rzgcs.bat"
echo echo Starte RZ Ground Control Station... >> "build\RZGCS\start_rzgcs.bat"
echo cd /d %%~dp0 >> "build\RZGCS\start_rzgcs.bat"
echo python Python\main.py >> "build\RZGCS\start_rzgcs.bat"
echo pause >> "build\RZGCS\start_rzgcs.bat"

:: Erstelle Install-Skript
echo @echo off > "build\RZGCS\install.bat"
echo echo Installation der RZ Ground Control Station... >> "build\RZGCS\install.bat"
echo echo Diese Installation setzt voraus, dass Python 3.8 oder höher installiert ist. >> "build\RZGCS\install.bat"
echo cd /d %%~dp0 >> "build\RZGCS\install.bat"
echo python -m pip install -r requirements.txt >> "build\RZGCS\install.bat"
echo echo. >> "build\RZGCS\install.bat"
echo echo Installation abgeschlossen! >> "build\RZGCS\install.bat"
echo echo Sie können die Anwendung jetzt über 'start_rzgcs.bat' starten. >> "build\RZGCS\install.bat"
echo pause >> "build\RZGCS\install.bat"

:: Erstelle Desktopverknüpfung-Skript
echo @echo off > "build\RZGCS\create_shortcut.bat"
echo echo Erstelle Desktop-Verknüpfung... >> "build\RZGCS\create_shortcut.bat"
echo cd /d %%~dp0 >> "build\RZGCS\create_shortcut.bat"
echo echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\RZ Ground Control Station.lnk" >> "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo oLink.TargetPath = oWS.CurrentDirectory ^& "\start_rzgcs.bat" >> "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo oLink.IconLocation = oWS.CurrentDirectory ^& "\Assets\icon.ico" >> "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo oLink.WindowStyle = 1 >> "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo oLink.WorkingDirectory = oWS.CurrentDirectory >> "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo oLink.Description = "RZ Ground Control Station" >> "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo oLink.Save >> "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo cscript //nologo "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo del "%TEMP%\shortcut.vbs" >> "build\RZGCS\create_shortcut.bat"
echo echo Desktopverknüpfung erstellt! >> "build\RZGCS\create_shortcut.bat"
echo pause >> "build\RZGCS\create_shortcut.bat"

:: Erstelle README.txt
echo RZ Ground Control Station > "build\RZGCS\README.txt"
echo ========================= >> "build\RZGCS\README.txt"
echo. >> "build\RZGCS\README.txt"
echo Installation: >> "build\RZGCS\README.txt"
echo 1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist. >> "build\RZGCS\README.txt"
echo 2. Führen Sie 'install.bat' aus, um alle erforderlichen Abhängigkeiten zu installieren. >> "build\RZGCS\README.txt"
echo 3. Führen Sie 'start_rzgcs.bat' aus, um die Anwendung zu starten. >> "build\RZGCS\README.txt"
echo 4. Optional: Führen Sie 'create_shortcut.bat' aus, um eine Desktop-Verknüpfung zu erstellen. >> "build\RZGCS\README.txt"
echo. >> "build\RZGCS\README.txt"
echo Systemanforderungen: >> "build\RZGCS\README.txt"
echo - Windows 10/11, macOS 10.14+, Ubuntu 20.04+, oder Raspberry Pi OS >> "build\RZGCS\README.txt"
echo - Python 3.8 oder höher >> "build\RZGCS\README.txt"
echo - 2GB RAM (4GB empfohlen) >> "build\RZGCS\README.txt"
echo. >> "build\RZGCS\README.txt"
echo Support: >> "build\RZGCS\README.txt"
echo Bei Fragen oder Problemen wenden Sie sich bitte an support@rz-robotics.com >> "build\RZGCS\README.txt"

:: Optional: Erstelle ZIP-Archiv
echo Erstelle ZIP-Archiv des Pakets...
cd build
powershell -command "Compress-Archive -Path 'RZGCS' -DestinationPath 'RZGCS-distribution.zip' -Force"
cd ..

echo.
echo Installationspaket erfolgreich erstellt!
echo Sie finden das Paket im Ordner 'build\RZGCS'
echo Ein ZIP-Archiv wurde erstellt unter 'build\RZGCS-distribution.zip'
echo.
echo Hinweise zur Verwendung:
echo 1. Verteilen Sie das Paket als ZIP-Datei an Ihre Kunden
echo 2. Um die Anwendung zu installieren, muss der Kunde Python installieren und dann install.bat ausführen
echo 3. Zum Starten der Anwendung verwendet der Kunde die start_rzgcs.bat Datei
echo.
echo Drücken Sie eine beliebige Taste, um zu beenden...
pause > nul
