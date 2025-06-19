import sys
import os
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication
import mavlink_main
from backend_bridge import BackendBridge

def main():
    # Erstelle QML-Engine
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Setze alle relevanten QML-Importpfade
    base_dir = os.path.dirname(os.path.abspath(__file__))
    engine.addImportPath(base_dir)
    engine.addImportPath(os.path.join(base_dir, "Components"))
    engine.addImportPath(os.path.join(base_dir, "Connection"))
    engine.addImportPath(os.path.join(base_dir, "com"))
    engine.addImportPath(os.path.join(base_dir, "com", "rzgcs", "licensing"))

    # Erstelle Backend-Bridge
    backend = BackendBridge()
    engine.rootContext().setContextProperty("backend", backend)

    # Lade QML
    qml_file = os.path.join(base_dir, "App.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    # Starte MAVLink-Controller
    backend.mavlink.start()

    # Starte Anwendung
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 