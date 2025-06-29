from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import qmlRegisterType, QQmlEngine, QJSEngine, QQmlComponent, QQmlApplicationEngine
import os
from pathlib import Path

class DummyQmlComponents:
    """
    Registriert alle benötigten QML-Typen für die UI-only Ansicht
    """
    @staticmethod
    def register_dummy_types(engine):
        """Register dummy QML types needed by the application"""
        from dummy_license_controller import DummyLicenseController
        
        # QML-Typen registrieren (ohne eigene Implementierung)
        qmlRegisterType(DummyLicenseController, "RZGCS", 1, 0, "LicenseController")
        
        # UI-QML-Dateien als QML-Typen registrieren
        base_path = Path(__file__).parent.parent
        qml_path = base_path / "RZGCSContent"
        
        # Diese Liste enthält alle QML-Dateien, die als Typen registriert werden sollen
        # Format: (QML-Dateiname, Typname)
        qml_types = [
            ("Screen01.ui.qml", "Screen01"),
            ("LicenseView.qml", "LicenseView"),
            ("LogsView.ui.qml", "LogsView"),
            ("ConnectionView.qml", "StatusBar"),       # Umleitung auf eine existierende Datei
            ("ConnectionView.ui.qml", "ConnectionView"),
            ("ConnectionView.qml", "TelemetryView"),    # Umleitung auf eine existierende Datei
            ("ConnectionView.qml", "ParametersView"),   # Umleitung auf eine existierende Datei
            ("CalibrationView.ui.qml", "CalibrationView"),
            ("ConnectionView.qml", "PreflightView"),    # Umleitung auf eine existierende Datei
            ("FirmwareView.ui.qml", "FirmwareView")
        ]
        
        # Funktion zum Erstellen eines QML-Moduls aus einer Datei
        def create_qml_singleton_provider(qml_file_path):
            def singleton_provider(engine, js_engine):
                component = QQmlComponent(engine)
                component.loadUrl(qml_file_path)
                if component.isError():
                    for error in component.errors():
                        print(f"Fehler beim Laden von {qml_file_path}: {error.toString()}")
                    return None
                context = QQmlEngine.contextForObject(engine.rootObjects()[0]) if engine.rootObjects() else None
                instance = component.create(context) if context else component.create()
                if instance is None:
                    print(f"Konnte keine Instanz für {qml_file_path} erstellen")
                    if component.isError():
                        for error in component.errors():
                            print(f" - {error.toString()}")
                    return None
                return instance
            return singleton_provider
        
        # Alle QML-Dateien als Singleton-Typen registrieren
        # Hinweis: In einer realen Anwendung würde man normalerweise nicht jede UI-Datei als Singleton registrieren,
        # aber für UI-Testing ist das ein praktischer Ansatz
        for qml_file, type_name in qml_types:
            qml_file_path = qml_path / qml_file
            if qml_file_path.exists():
                try:
                    # Als URL für den Provider
                    url = QUrl.fromLocalFile(str(qml_file_path))
                    
                    # Als normalen Typ registrieren
                    def dummy_type_provider(engine, script_engine):
                        return QObject()
                        
                    qmlRegisterType(url, "RZGCS", 1, 0, type_name)
                    print(f"QML-Typ '{type_name}' registriert von {qml_file}")
                except Exception as e:
                    print(f"Fehler bei der Registrierung von {qml_file} als {type_name}: {e}")
            else:
                print(f"Warnung: QML-Datei {qml_file} nicht gefunden unter {qml_file_path}")
                
        print("Alle benötigten QML-Typen wurden registriert")
