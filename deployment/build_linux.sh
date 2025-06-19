#!/bin/bash
# RZGCS Linux Build Script

# Fehler bei Ausfuu00fchrung stoppen
set -e

# Erforderliche Pakete installieren
pip install pyinstaller pyqt5 pymavlink numpy matplotlib

# Verzeichnis fu00fcr Build erstellen
BUILD_DIR="../build/linux"
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

echo "Linux-Build abgeschlossen. Ausfu00fchrbare Datei befindet sich in: $BUILD_DIR/RZGCS/RZGCS"

# AppImage erstellen (erfordert appimagetool)
APPIMAGE_DIR="../build/appimage"
mkdir -p "$APPIMAGE_DIR"
mkdir -p "$APPIMAGE_DIR/usr/bin"
mkdir -p "$APPIMAGE_DIR/usr/share/applications"
mkdir -p "$APPIMAGE_DIR/usr/share/icons/hicolor/256x256/apps"

# Desktop-Datei erstellen
cat > "$APPIMAGE_DIR/usr/share/applications/RZGCS.desktop" << EOL
[Desktop Entry]
Name=RZGCS
Exec=RZGCS
Icon=RZGCS
Type=Application
Categories=Development;Engineering;
EOL

# Ausfu00fchrbare Dateien kopieren
cp -r "$BUILD_DIR/RZGCS"/* "$APPIMAGE_DIR/usr/bin/"

# Icon kopieren
cp "../RZGCSContent/icon.png" "$APPIMAGE_DIR/usr/share/icons/hicolor/256x256/apps/RZGCS.png" 2>/dev/null || echo "Icon nicht gefunden, Standard-Icon wird verwendet"

# AppRun-Skript erstellen
cat > "$APPIMAGE_DIR/AppRun" << EOL
#!/bin/bash
exec "$(dirname "$0")/usr/bin/RZGCS" "$@"
EOL
chmod +x "$APPIMAGE_DIR/AppRun"

# AppImage erstellen, wenn appimagetool verfu00fcgbar ist
if command -v appimagetool &> /dev/null; then
    APPIMAGE_NAME="../build/installer/RZGCS-x86_64.AppImage"
    mkdir -p "../build/installer"
    appimagetool "$APPIMAGE_DIR" "$APPIMAGE_NAME"
    chmod +x "$APPIMAGE_NAME"
    echo "AppImage erstellt: $APPIMAGE_NAME"
else
    echo "appimagetool nicht gefunden. AppImage konnte nicht erstellt werden."
    echo "Fu00fcr AppImage-Erstellung bitte appimagetool installieren:"
    echo "https://github.com/AppImage/AppImageKit/releases"
fi

# DEB-Paket erstellen (erfordert dpkg-deb)
DEB_DIR="../build/deb"
DEB_PACKAGE_DIR="$DEB_DIR/RZGCS_1.0-1_amd64"
mkdir -p "$DEB_PACKAGE_DIR/DEBIAN"
mkdir -p "$DEB_PACKAGE_DIR/usr/bin"
mkdir -p "$DEB_PACKAGE_DIR/usr/share/applications"
mkdir -p "$DEB_PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps"

# Control-Datei erstellen
cat > "$DEB_PACKAGE_DIR/DEBIAN/control" << EOL
Package: rzgcs
Version: 1.0-1
Section: misc
Priority: optional
Architecture: amd64
Maintainer: Your Name <your.email@example.com>
Description: Remote Zone Ground Control Station
 A user-friendly drone control software with MAVLink protocol integration,
 configurable logging system, and a comprehensive flight view with interactive map.
EOL

# Desktop-Datei kopieren
cp "$APPIMAGE_DIR/usr/share/applications/RZGCS.desktop" "$DEB_PACKAGE_DIR/usr/share/applications/"

# Icon kopieren
cp "$APPIMAGE_DIR/usr/share/icons/hicolor/256x256/apps/RZGCS.png" "$DEB_PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps/" 2>/dev/null || echo "Icon nicht gefunden"

# Binu00e4rdateien kopieren
cp -r "$BUILD_DIR/RZGCS"/* "$DEB_PACKAGE_DIR/usr/bin/"

# DEB-Paket erstellen, wenn dpkg-deb verfu00fcgbar ist
if command -v dpkg-deb &> /dev/null; then
    mkdir -p "../build/installer"
    dpkg-deb --build "$DEB_PACKAGE_DIR" "../build/installer/RZGCS_1.0-1_amd64.deb"
    echo "DEB-Paket erstellt: ../build/installer/RZGCS_1.0-1_amd64.deb"
else
    echo "dpkg-deb nicht gefunden. DEB-Paket konnte nicht erstellt werden."
    echo "Fu00fcr DEB-Paket-Erstellung bitte dpkg-dev installieren."
fi
