"""
DummyQmlComponents.py - Stellt Dummy-QML-Komponenten für UI-Tests bereit
"""
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import qmlRegisterType, QmlElement

def register_dummy_types(engine):
    """Registriert alle benötigten QML-Typen für die UI"""
    print("Registriere Dummy-QML-Komponenten...")
    
    # QML-Dateipfad
    qml_path = Path(__file__).parent.parent / "RZGCSContent"
    
    # Wichtige UI-Komponenten registrieren
    register_qml_type(engine, qml_path / "Screen01.ui.qml", "Screen01")
    register_qml_type(engine, qml_path / "LicenseView.qml", "LicenseView")
    register_qml_type(engine, qml_path / "LogsView.ui.qml", "LogsView")
    register_qml_type(engine, qml_path / "StatusBar.qml", "StatusBar")  # Wichtig für messageManager
    register_qml_type(engine, qml_path / "ConnectionView.ui.qml", "ConnectionView")
    register_qml_type(engine, qml_path / "TelemetryView.qml", "TelemetryView")
    register_qml_type(engine, qml_path / "ParametersView.qml", "ParametersView")
    register_qml_type(engine, qml_path / "CalibrationView.ui.qml", "CalibrationView")
    register_qml_type(engine, qml_path / "PreflightView.qml", "PreflightView")
    register_qml_type(engine, qml_path / "FirmwareView.ui.qml", "FirmwareView")
    
    # Registriere weitere RZGCS.Connection Komponenten
    register_connection_types()
    
    print("Alle benötigten QML-Typen wurden registriert")

def register_qml_type(engine, file_path, type_name):
    """Registriert einen QML-Typ aus einer Datei"""
    if file_path.exists():
        from PySide6.QtQml import QQmlComponent
        from PySide6.QtCore import QUrl
        
        url = QUrl.fromLocalFile(str(file_path))
        component = QQmlComponent(engine)
        component.loadUrl(url)
        
        if not component.isError():
            print(f"QML-Typ '{type_name}' registriert von {file_path.name}")
            return True
        else:
            print(f"Fehler beim Registrieren von {type_name} aus {file_path}:")
            for error in component.errors():
                print(f"  - {error.toString()}")
            return False
    else:
        print(f"Warnung: QML-Datei {file_path.name} für Typ {type_name} existiert nicht")
        return False

def register_connection_types():
    """Registriert QML-Typen für das RZGCS.Connection Namespace"""
    # Hier könnten spezielle Connection-Typen registriert werden,
    # falls die importierte RZGCS.Connection nicht funktioniert
    pass
