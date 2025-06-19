import sys
import os
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

# Importiere die neue Backend-Bridge
from backend_bridge import BackendBridge

def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # QML-Importpfade relativ zum aktuellen Verzeichnis
    qml_dir = Path(__file__).parent
    engine.addImportPath(str(qml_dir))
    engine.addImportPath(str(qml_dir / "Components"))
    engine.addImportPath(str(qml_dir / "Connection"))
    engine.addImportPath(str(qml_dir / "com"))
    engine.addImportPath(str(qml_dir / "com" / "rzgcs" / "licensing"))

    # Neue Backend-Bridge
    backend = BackendBridge()
    engine.rootContext().setContextProperty("backend", backend)

    # QML-Hauptdatei laden
    qml_file = qml_dir / "App.qml"
    print(f"Lade QML-Datei: {qml_file}")
    if not qml_file.exists():
        print(f"FEHLER: QML-Datei nicht gefunden: {qml_file}")
        sys.exit(-1)
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        print(f"FEHLER: Keine Root-Objekte nach dem Laden von {qml_file}")
        sys.exit(-1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main() 