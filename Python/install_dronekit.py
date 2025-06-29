#!/usr/bin/env python3
"""
Installation-Script für DroneKit-Integration in RZGCS
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import serial.tools.list_ports

def print_header():
    """Druckt Header-Informationen"""
    print("=" * 60)
    print("RZGCS DroneKit-Integration Installer")
    print("=" * 60)
    print()

def check_python_version():
    """Prüft Python-Version"""
    print("🔍 Prüfe Python-Version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ erforderlich!")
        print(f"   Aktuelle Version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} gefunden")
    return True

def check_pip():
    """Prüft ob pip verfügbar ist"""
    print("🔍 Prüfe pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip verfügbar")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip nicht verfügbar!")
        return False

def install_package(package, version=None):
    """Installiert ein Python-Package"""
    package_spec = f"{package}>={version}" if version else package
    
    print(f"📦 Installiere {package_spec}...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package_spec], 
                      check=True, capture_output=True)
        print(f"✅ {package} installiert")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Installieren von {package}: {e}")
        return False

def install_requirements():
    """Installiert alle erforderlichen Packages"""
    print("📦 Installiere Dependencies...")
    print()
    
    requirements = [
        ("pyside6", "6.5.0"),
        ("pymavlink", "2.4.37"),
        ("pyserial", "3.5"),
        ("numpy", "1.24.0"),
        ("pandas", "2.0.0"),
        ("pyqtgraph", "0.13.3"),
        ("dronekit", "2.9.2")
    ]
    
    success_count = 0
    for package, version in requirements:
        if install_package(package, version):
            success_count += 1
        print()
    
    return success_count == len(requirements)

def create_directories():
    """Erstellt erforderliche Verzeichnisse"""
    print("📁 Erstelle Verzeichnisse...")
    
    directories = [
        "backend/rzgcs_dronekit",
        "viewmodels",
        "tests",
        "examples"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Verzeichnis erstellt: {directory}")
        else:
            print(f"ℹ️  Verzeichnis existiert bereits: {directory}")

def check_files():
    """Prüft ob alle erforderlichen Dateien vorhanden sind"""
    print("🔍 Prüfe Dateien...")
    
    required_files = [
        "backend/rzgcs_dronekit/__init__.py",
        "backend/rzgcs_dronekit/connector.py",
        "backend/rzgcs_dronekit/connection_manager.py",
        "backend/rzgcs_dronekit/telemetry_handler.py",
        "backend/rzgcs_dronekit/control_handler.py",
        "backend/rzgcs_dronekit/mission_handler.py",
        "backend/rzgcs_dronekit/parameter_manager.py",
        "backend/rzgcs_dronekit/vehicle_manager.py",
        "backend/rzgcs_dronekit/utils.py",
        "backend/rzgcs_dronekit/README.md",
        "viewmodels/dronekit_viewmodel.py",
        "tests/test_dronekit_integration.py",
        "examples/dronekit_example.py",
        "backend/requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print("❌ Fehlende Dateien:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def test_imports():
    """Testet Imports der DroneKit-Module"""
    print("🧪 Teste Imports...")
    
    try:
        # Basis-Imports testen
        import dronekit
        print("✅ dronekit importiert")
        
        import pymavlink
        print("✅ pymavlink importiert")
        
        import PySide6
        print("✅ PySide6 importiert")
        
        # Lokale Module testen
        sys.path.insert(0, "backend")
        
        from backend.rzgcs_dronekit.connector import DroneKitConnector
        print("✅ DroneKitConnector importiert")
        
        from backend.rzgcs_dronekit.utils import DroneKitUtils
        print("✅ DroneKitUtils importiert")
        
        from backend.rzgcs_dronekit.connection_manager import DroneKitConnectionManager
        print("✅ DroneKitConnectionManager importiert")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False

def run_tests():
    """Führt Tests aus"""
    print("🧪 Führe Tests aus...")
    
    try:
        result = subprocess.run([sys.executable, "tests/test_dronekit_integration.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tests erfolgreich")
            return True
        else:
            print("❌ Tests fehlgeschlagen:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Ausführen der Tests: {e}")
        return False

def create_example_script():
    """Erstellt ein Beispiel-Script"""
    print("📝 Erstelle Beispiel-Script...")
    
    example_content = '''#!/usr/bin/env python3
"""
DroneKit-Integration Beispiel
"""

import asyncio
import sys
import os

# Pfad zum backend-Modul hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.rzgcs_dronekit.connector import DroneKitConnector

async def main():
    print("🚁 DroneKit-Integration Test")
    print("=" * 40)
    
    # Connector erstellen
    connector = DroneKitConnector("udp://127.0.0.1:14550")
    
    print("🔌 Verbinde zur Drohne...")
    success = await connector.connect()
    
    if success:
        print("✅ Verbunden!")
        
        # Telemetrie abrufen
        telemetry = connector.get_telemetry_data()
        print(f"📡 Telemetrie-Daten: {len(telemetry)} Einträge")
        
        # Verbindung trennen
        connector.disconnect()
        print("🔌 Verbindung getrennt")
    else:
        print("❌ Verbindung fehlgeschlagen")
        print("   Stellen Sie sicher, dass SITL läuft oder eine echte Drohne verbunden ist")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("test_dronekit.py", "w") as f:
        f.write(example_content)
    
    print("✅ Beispiel-Script erstellt: test_dronekit.py")

def print_usage_instructions():
    """Druckt Verwendungsanweisungen"""
    print()
    print("=" * 60)
    print("Installation abgeschlossen!")
    print("=" * 60)
    print()
    print("🚀 Nächste Schritte:")
    print()
    print("1. Testen Sie die Installation:")
    print("   python test_dronekit.py")
    print()
    print("2. Starten Sie SITL (ArduPilot Simulator):")
    print("   cd /path/to/ardupilot")
    print("   Tools/autotest/sim_vehicle.py -w")
    print()
    print("3. Oder verbinden Sie eine echte Drohne")
    print()
    print("4. Beispiel-Anwendung starten:")
    print("   python examples/dronekit_example.py")
    print()
    print("📚 Dokumentation:")
    print("   backend/rzgcs_dronekit/README.md")
    print()
    print("🧪 Tests ausführen:")
    print("   python tests/test_dronekit_integration.py")
    print()

def main():
    """Hauptfunktion"""
    print_header()
    
    # System-Informationen
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    # Prüfungen
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    print()
    
    # Installation
    if not install_requirements():
        print("❌ Installation fehlgeschlagen!")
        sys.exit(1)
    
    print()
    
    # Verzeichnisse erstellen
    create_directories()
    print()
    
    # Dateien prüfen
    if not check_files():
        print("❌ Erforderliche Dateien fehlen!")
        print("   Stellen Sie sicher, dass alle DroneKit-Dateien vorhanden sind.")
        sys.exit(1)
    
    print()
    
    # Imports testen
    if not test_imports():
        print("❌ Import-Tests fehlgeschlagen!")
        sys.exit(1)
    
    print()
    
    # Tests ausführen
    if not run_tests():
        print("⚠️  Tests fehlgeschlagen, aber Installation kann fortgesetzt werden")
    
    print()
    
    # Beispiel-Script erstellen
    create_example_script()
    
    # Verwendungsanweisungen
    print_usage_instructions()

    # Test für die Ports
    print("🔍 Prüfe Ports...")
    print(list(serial.tools.list_ports.comports()))

if __name__ == "__main__":
    main() 