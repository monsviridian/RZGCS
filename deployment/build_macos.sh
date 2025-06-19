#!/bin/bash
# RZGCS macOS Build Script

# Fehler bei Ausfu00fchrung stoppen
set -e

# Erforderliche Pakete installieren
pip install pyinstaller pyqt5 pymavlink numpy matplotlib

# Verzeichnis fu00fcr Build erstellen
BUILD_DIR="../build/macos"
mkdir -p "$BUILD_DIR"

# PyInstaller ausfu00fchren
pyinstaller --name="RZGCS" --windowed --icon="../RZGCSContent/icon.icns" \
    --add-data="../RZGCSContent:RZGCSContent" \
    --add-data="../Python:Python" \
    --add-data="../LICENSE.md:." \
    --add-data="../THIRD_PARTY_LICENSES.md:." \
    "../main.py"

# Dateien in den Build-Ordner verschieben
mv "dist/RZGCS.app" "$BUILD_DIR/"
mv "RZGCS.spec" "$BUILD_DIR/"

# Qt-Abhu00e4ngigkeiten mit macdeployqt hinzufu00fcgen
QT_BIN_PATH=$(python -c "from PyQt5.QtCore import QLibraryInfo; print(QLibraryInfo.location(QLibraryInfo.BinariesPath))")
"$QT_BIN_PATH/macdeployqt" "$BUILD_DIR/RZGCS.app"

echo "macOS-Build abgeschlossen. App befindet sich in: $BUILD_DIR/RZGCS.app"

# DMG-Installer erstellen
DMG_DIR="../build/installer"
mkdir -p "$DMG_DIR"

DMG_NAME="$DMG_DIR/RZGCS_Installer.dmg"

# Temporu00e4ren Ordner fu00fcr das DMG erstellen
DMG_TMP="$DMG_DIR/dmg_tmp"
mkdir -p "$DMG_TMP"

# App in den temporu00e4ren Ordner kopieren
cp -R "$BUILD_DIR/RZGCS.app" "$DMG_TMP/"

# Symlink zum Applications-Ordner erstellen
ln -s /Applications "$DMG_TMP/Applications"

# Benutzerfreundlichen Hintergrund hinzufu00fcgen (optional)
cp "../RZGCSContent/installer_background.png" "$DMG_TMP/.background.png" 2>/dev/null || echo "Kein Hintergrundbild gefunden"

# DMG erstellen
hdiutil create -volname "RZGCS Installer" -srcfolder "$DMG_TMP" -ov -format UDZO "$DMG_NAME"

# Temporu00e4ren Ordner entfernen
rm -rf "$DMG_TMP"

echo "macOS DMG-Installer erstellt: $DMG_NAME"
