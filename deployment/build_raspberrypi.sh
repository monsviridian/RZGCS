#!/bin/bash
# RZGCS Raspberry Pi OS Build Script

# Fehler bei Ausfu00fchrung stoppen
set -e

# Erforderliche Pakete installieren
pip3 install pyinstaller pymavlink numpy matplotlib

# Qt-Abhu00e4ngigkeiten (auf Raspberry Pi mu00fcssen diese meist mit apt installiert werden)
echo "Bitte stellen Sie sicher, dass folgende Pakete installiert sind:"
echo "sudo apt-get install python3-pyqt5 python3-pyqt5.qtquick qml-module-qtquick2 qml-module-qtquick-controls2"

# Verzeichnis fu00fcr Build erstellen
BUILD_DIR="../build/raspberrypi"
mkdir -p "$BUILD_DIR"

# PyInstaller ausfu00fchren
pyinstaller --name="RZGCS" --windowed \
    --add-data="../RZGCSContent:RZGCSContent" \
    --add-data="../Python:Python" \
    --add-data="../LICENSE.md:." \
    --add-data="../THIRD_PARTY_LICENSES.md:." \
    "../main.py"

# Dateien in den Build-Ordner verschieben
mv "dist/RZGCS" "$BUILD_DIR/"
mv "RZGCS.spec" "$BUILD_DIR/"

echo "Raspberry Pi OS-Build abgeschlossen. Ausfu00fchrbare Datei befindet sich in: $BUILD_DIR/RZGCS/RZGCS"

# Installer-Skript erstellen
INSTALLER_DIR="../build/installer"
mkdir -p "$INSTALLER_DIR"

# Installer-Skript erstellen
cat > "$INSTALLER_DIR/install_rzgcs_pi.sh" << EOL
#!/bin/bash

# RZGCS Raspberry Pi Installer
echo "RZGCS Installer fu00fcr Raspberry Pi"

# Erforderliche Pakete installieren
echo "Installiere erforderliche Abhu00e4ngigkeiten..."
sudo apt-get update
sudo apt-get install -y python3-pyqt5 python3-pyqt5.qtquick qml-module-qtquick2 qml-module-qtquick-controls2

# Installationsverzeichnis erstellen
INSTALL_DIR="/opt/RZGCS"
echo "Installiere RZGCS nach $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"

# Dateien extrahieren (hier nehmen wir an, dass alle Dateien im selben Verzeichnis wie das Skript sind)
echo "Kopiere Dateien..."
sudo cp -r RZGCS/* "$INSTALL_DIR/"

# Desktop-Shortcut erstellen
echo "Erstelle Desktop-Shortcut..."
cat > ~/.local/share/applications/RZGCS.desktop << DESKTOP
[Desktop Entry]
Name=RZGCS
Exec=/opt/RZGCS/RZGCS
Icon=/opt/RZGCS/RZGCSContent/icon.png
Type=Application
Categories=Development;Engineering;
DESKTOP

# Ausfu00fchrbare Rechte setzen
sudo chmod +x "$INSTALL_DIR/RZGCS"

echo "Installation abgeschlossen! Sie ku00f6nnen RZGCS jetzt aus dem Anwendungsmenu00fc starten."
EOL

# Ausfu00fchrbar machen
chmod +x "$INSTALLER_DIR/install_rzgcs_pi.sh"

# Tar-Archiv mit Anwendung und Installer erstellen
TAR_NAME="$INSTALLER_DIR/RZGCS-RaspberryPi.tar.gz"
cp "$INSTALLER_DIR/install_rzgcs_pi.sh" "$BUILD_DIR/"
cd "$BUILD_DIR"
tar -czvf "$TAR_NAME" RZGCS install_rzgcs_pi.sh

echo "Raspberry Pi OS Installer-Paket erstellt: $TAR_NAME"
echo "Zur Installation auf dem Raspberry Pi:"
echo "1. U00dcbertragen Sie die Datei $TAR_NAME auf Ihren Raspberry Pi"
echo "2. Entpacken Sie die Datei: tar -xzvf RZGCS-RaspberryPi.tar.gz"
echo "3. Fu00fchren Sie das Installations-Skript aus: ./install_rzgcs_pi.sh"
