# backend/serial_connector.py
import os
import sys
from PySide6.QtCore import QObject, Signal, Slot
import serial.tools.list_ports
from .mavsdk_connector import MAVSDKConnector
from .logger import Logger 
from .sensorviewmodel import SensorViewModel

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

class SerialConnector(QObject):
    print(sys.path)
    connection_successful = Signal()
    connection_failed = Signal(str)
    availablePortsChanged = Signal(list)
    connection_status_changed = Signal(bool)  # Signal für den Verbindungsstatus

    def __init__(self, logger: Logger, sensor_model: SensorViewModel ):
        super().__init__()
        self.logger = logger
        self.sensor_model = sensor_model
        #self.log("SerialConnector gestartet")
        self._ports = []
        
        self.mavsdk = MAVSDKConnector(logger, sensor=sensor_model)


        # Verknüpfen des Signals connected_changed des MAVSDKConnectors mit dem Signal des SerialConnectors
        self.mavsdk.connected_changed.connect(self.handle_connection_status)

        self.load_ports()

    @Slot()
    def load_ports(self):
        ports = serial.tools.list_ports.comports()
        self._ports = [port.device for port in ports]
        print("Verfügbare Ports:", self._ports)
        self.logger.add_log("Verfügbare Ports geladen")  # Log-Nachricht hinzufügen
        self.availablePortsChanged.emit(self._ports)

    @Slot(str, int, str)
    def connect_to_port(self, port_name, baudrate, autopilot_type):
        print(f"🔌 Verbinde zu {port_name} @ {baudrate} ({autopilot_type})")

        # Wenn mavsdk existiert, dann den Connect-Befehl aufrufen, aber keine extra Argumente übergeben
        if hasattr(self, 'mavsdk'):
            self.mavsdk.connect_mav(port_name, baudrate)  # Nur port_name und baudrate übergeben
            self.logger.add_log(f"Verbindung zu {port_name} @ {baudrate} gestartet")  # Log-Nachricht hinzufügen
        else:
            self.connection_failed.emit("MAVSDKConnector nicht gesetzt")
            self.logger.add_log("MAVSDKConnector nicht gesetzt")  # Log-Nachricht hinzufügen
            
            
        if not hasattr(self, 'mavsdk'):
            print("⚠️ Fehler: MAVSDKConnector nicht gesetzt!")
            self.connection_failed.emit("MAVSDKConnector nicht gesetzt")
            return


    # Signalhandler für den Verbindungsstatus
    def handle_connection_status(self, is_connected: bool):
        print(f"Verbindung Status: {'Erfolgreich' if is_connected else 'Fehlgeschlagen'}")
        self.connection_status_changed.emit(is_connected)
        if is_connected:
            self.connection_successful.emit()
        else:
            self.connection_failed.emit("Verbindung fehlgeschlagen")
