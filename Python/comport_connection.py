#!/usr/bin/env python3
"""
COM Port Connection Script
Spezialisierter Script für die COM-Port-Verbindung mit der Drohne,
basierend auf den existierenden Klassen, aber mit optimierter Signalhandhabung.
"""

import os
import sys
import time
import asyncio
import threading
from pathlib import Path

# Project paths setup
project_root = str(Path(__file__).resolve().parent.parent)
python_dir = os.path.join(project_root, "Python")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

# Set up PySide6 style
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# Now import PySide6
import PySide6
from PySide6.QtCore import QObject, QUrl, Signal, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

# Import required modules
from mavsdk import System
from backend.logger import Logger
from dronekit import connect


class DroneConnectionHelper(QObject):
    """
    Helper-Klasse für die Verbindung zur Drohne via COM-Port
    """
    # Signals
    connectionStateChanged = Signal(bool)
    portsRefreshed = Signal(list)
    logMessage = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ports = []
        self._selected_port = ""
        self._drone = System()
        self._is_connected = False
        self._stop_event = threading.Event()
    
    @Slot()
    def refreshPorts(self):
        """Aktualisiert die Liste der verfügbaren COM-Ports"""
        try:
            import serial.tools.list_ports
            self._ports = [port.device for port in serial.tools.list_ports.comports()]
            self.logMessage.emit(f"[INFO] {len(self._ports)} COM-Port(s) gefunden")
            self.portsRefreshed.emit(self._ports)
        except Exception as e:
            self.logMessage.emit(f"[FEHLER] Konnte Ports nicht laden: {e}")
            self._ports = []
    
    @Slot(str)
    def setPort(self, port_name):
        """Setzt den ausgewählten COM-Port"""
        self._selected_port = port_name
        self.logMessage.emit(f"[INFO] Port ausgewählt: {port_name}")
    
    @Property(bool, notify=connectionStateChanged)
    def connected(self):
        """Gibt zurück, ob die Drohne verbunden ist"""
        return self._is_connected
    
    @Slot(str)
    def connectToDrone(self, connection_string=""):
        """
        Verbindet zur Drohne über den angegebenen Verbindungsstring (z.B. 'COM8:115200' oder 'COM8')
        und zeigt Telemetrie im Message Panel an.
        """
        if not connection_string and self._selected_port:
            connection_string = self._selected_port

        if not connection_string:
            self.logMessage.emit("[FEHLER] Kein Verbindungsstring oder Port angegeben")
            return

        self.logMessage.emit(f"[INFO] Verbinde mit: {connection_string}")

        # Parse port and baudrate
        baudrate = 115200  # Default
        if ":" in connection_string:
            port, baudrate_str = connection_string.split(":", 1)
            baudrate = int(baudrate_str)
        else:
            port = connection_string

        try:
            self.logMessage.emit(f"[INFO] Starte DroneKit-Verbindung zu {port} mit {baudrate} Baud...")
            self.vehicle = connect(port, wait_ready=True, baud=baudrate)
            self._is_connected = True
            self.connectionStateChanged.emit(True)
            self.logMessage.emit("[INFO] Verbindung zur Drohne hergestellt")
            self.logMessage.emit(f"[INFO] Flugmodus: {self.vehicle.mode.name}")
            # Telemetrie anzeigen
            for _ in range(5):  # Zeige 5x Telemetrie nach Verbindung
                gps = self.vehicle.gps_0
                battery = self.vehicle.battery
                attitude = self.vehicle.attitude
                location = self.vehicle.location.global_frame
                self.logMessage.emit(f"[TELEMETRIE] GPS: {gps} | Battery: {battery} | Attitude: {attitude} | Location: {location}")
                time.sleep(1)
        except Exception as e:
            self.logMessage.emit(f"[FEHLER] Verbindungsfehler: {e}")
            self._is_connected = False
            self.connectionStateChanged.emit(False)
    
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung zur Drohne"""
        if self._is_connected:
            self._stop_event.set()
            self._is_connected = False
            self.connectionStateChanged.emit(False)
            self.logMessage.emit("[INFO] Verbindung zur Drohne getrennt")


def main():
    """Hauptfunktion der Anwendung"""
    # Versionsinfo ausgeben
    print(f"Python-Version: {sys.version}")
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # Arbeitsverzeichnis setzen
    os.chdir(project_root)
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # Material-Stil setzen
    QQuickStyle.setStyle("Material")
    
    # Anwendung erstellen
    app = QGuiApplication(sys.argv)
    
    # Logger erstellen
    logger = Logger()
    
    # DroneConnectionHelper erstellen
    connection_helper = DroneConnectionHelper()
    
    # Logger mit Helper verbinden
    connection_helper.logMessage.connect(lambda msg: logger.addLog(msg))
    
    # COM-Ports laden
    connection_helper.refreshPorts()
    
    # Kommandozeilen-Interface
    print("\n=== COM-Port-Verbindung ===")
    print("Verfügbare Befehle:")
    print("1. Ports - Verfügbare Ports anzeigen")
    print("2. Connect <port> - Mit Port verbinden (z.B. 'Connect COM3' oder 'Connect COM3:115200')")
    print("3. Disconnect - Verbindung trennen")
    print("4. Exit - Programm beenden")
    
    # Event-Loop starten
    app_thread = threading.Thread(target=app.exec, daemon=True)
    app_thread.start()
    
    # Kommandozeilen-Interface
    try:
        while True:
            cmd = input("\nBefehl: ").strip()
            
            if cmd.lower() == "ports":
                connection_helper.refreshPorts()
                print(f"Verfügbare Ports: {', '.join(connection_helper._ports)}")
            
            elif cmd.lower().startswith("connect"):
                parts = cmd.split(" ", 1)
                if len(parts) > 1:
                    port = parts[1].strip()
                    print(f"Verbinde mit: {port}")
                    connection_helper.connectToDrone(port)
                else:
                    print("Bitte Port angeben (z.B. 'Connect COM3')")
            
            elif cmd.lower() == "disconnect":
                connection_helper.disconnect()
                print("Verbindung getrennt")
            
            elif cmd.lower() == "exit":
                print("Programm wird beendet...")
                break
            
            else:
                print("Unbekannter Befehl. Verfügbare Befehle: Ports, Connect <port>, Disconnect, Exit")
    
    except KeyboardInterrupt:
        print("\nProgramm wird beendet...")
    
    finally:
        # Ressourcen freigeben
        connection_helper._stop_event.set()
        if connection_helper._is_connected:
            connection_helper.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
