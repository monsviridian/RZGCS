#!/usr/bin/env python3
"""
MAVSDK Drone ViewModel - ViewModel für die Drohnensteuerung im MVVM-Pattern

Dieses ViewModel stellt die Verbindung zwischen der UI und dem MAVSDKConnectorMVVM her
und implementiert die entsprechende Geschäftslogik mit Unterstützung für Nachrichtenfilterung
und die spezielle Preflight-View für Systeminformationen.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

from backend.mavsdk_connector_mvvm import MAVSDKConnectorMVVM
from backend.logger import Logger


class MAVSDKDroneViewModel(QObject):
    """ViewModel für die Drohnensteuerung mit MAVSDK-Integration"""
    
    # Signale für die UI
    connectionStateChanged = Signal(bool)
    armedStateChanged = Signal(bool)
    flightModeChanged = Signal(str)
    gpsInfoChanged = Signal(dict)
    batteryChanged = Signal(dict)
    attitudeChanged = Signal(dict)
    headingChanged = Signal(float)
    positionChanged = Signal(dict)
    homePositionChanged = Signal(dict)
    messageReceived = Signal(str)
    systemInfoReceived = Signal(str)  # Spezielles Signal für Systeminformationen (Preflight-View)
    errorOccurred = Signal(str)
    
    def __init__(self, logger: Logger, parent=None):
        """Initialisierung des DroneViewModel"""
        super().__init__(parent)
        
        # Logger
        self._logger = logger
        
        # MAVSDK-Connector
        self._connector = MAVSDKConnectorMVVM(logger)
        
        # Verbindungsstatus
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNBEKANNT"
        self._gps_info = {"num_satellites": 0, "fix_type": 0}
        self._battery_info = {"remaining_percent": 0.0, "voltage_v": 0.0, "current_a": 0.0}
        self._attitude = {"roll_deg": 0.0, "pitch_deg": 0.0, "yaw_deg": 0.0}
        self._position = {
            "latitude_deg": 0.0,
            "longitude_deg": 0.0,
            "absolute_altitude_m": 0.0,
            "relative_altitude_m": 0.0
        }
        self._home_position = {
            "latitude_deg": 0.0,
            "longitude_deg": 0.0,
            "absolute_altitude_m": 0.0,
            "relative_altitude_m": 0.0
        }
        
        # Port management
        self._available_ports = []
        self._connection_status = "Disconnected"
        self._status_message = "Ready to connect"
        
        # Scan for available ports on init
        self.refreshPorts()
        
        # Verbinde Signale und registriere Callbacks
        self._connect_signals()
        self._register_callbacks()
    
    def _connect_signals(self):
        """Verbindet die Signale des Connectors mit lokalen Slots"""
        # Verbindungssignale
        self._connector.signals.connection_established.connect(self._on_connected)
        self._connector.signals.connection_lost.connect(self._on_disconnected)
        self._connector.signals.error_occurred.connect(self._on_error_occurred)
        
        # Telemetrie-Signale
        self._connector.signals.armed_changed.connect(self._on_armed_changed)
        self._connector.signals.flight_mode_changed.connect(self._on_flight_mode_changed)
        self._connector.signals.gps_info_changed.connect(self._on_gps_info_changed)
        self._connector.signals.battery_changed.connect(self._on_battery_changed)
        self._connector.signals.attitude_changed.connect(self._on_attitude_changed)
        self._connector.signals.heading_changed.connect(self._on_heading_changed)
        self._connector.signals.position_changed.connect(self._on_position_changed)
        self._connector.signals.home_position_changed.connect(self._on_home_position_changed)
        
        # Status-Texte
        self._connector.signals.statustext_received.connect(self._on_statustext_received)
    
    def _register_callbacks(self):
        """Registriert zusätzliche Callbacks beim Connector"""
        # Verwendet das Callback-Interface zusätzlich zu den Signalen
        # Dies stellt die Kompatibilität mit älteren Code-Teilen sicher
        self._connector.register_connection_callback(self._on_connected)
        self._connector.register_disconnection_callback(self._on_disconnected)
        
        # Telemetrie-Callbacks
        for telemetry_type in ['armed', 'flight_mode', 'gps_info', 'battery', 'attitude', 
                            'heading', 'position', 'home_position']:
            self._connector.register_telemetry_callback(telemetry_type, self._on_telemetry_update)
        
        self._connector.register_statustext_callback(self._on_statustext_received)
    
    # Signal-Definitionen für die Properties
    availablePortsChanged = Signal()
    connectionStatusChanged = Signal()
    statusMessageChanged = Signal()
    
    # Properties für die UI
    @Property(list, notify=availablePortsChanged)
    def availablePorts(self) -> list:
        """Gibt die Liste der verfügbaren COM-Ports zurück"""
        return self._available_ports
    
    @Property(str, notify=connectionStatusChanged)
    def connectionStatus(self) -> str:
        """Gibt den aktuellen Verbindungsstatus als String zurück"""
        return self._connection_status
    
    @Property(str, notify=statusMessageChanged)
    def statusMessage(self) -> str:
        """Gibt die aktuelle Statusmeldung zurück"""
        return self._status_message
    
    @Slot()
    def refreshPorts(self) -> None:
        """Aktualisiert die Liste der verfügbaren COM-Ports"""
        import serial.tools.list_ports
        
        try:
            # Get all available COM ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            
            if ports != self._available_ports:
                self._available_ports = ports
                self.availablePortsChanged.emit()
                
            if not ports:
                self._update_status("Keine COM-Ports gefunden")
            else:
                self._update_status(f"{len(ports)} COM-Port(s) gefunden")
                
        except Exception as e:
            self._update_status(f"Fehler beim Scannen der Ports: {str(e)}", is_error=True)
    
    def _update_status(self, message: str, is_error: bool = False) -> None:
        """Aktualisiert die Statusmeldung"""
        self._status_message = message
        self.statusMessageChanged.emit()
        
        # Use addLog method which is compatible with the custom Logger class
        log_message = f"[ERROR] {message}" if is_error else f"[INFO] {message}"
        self._logger.addLog(log_message)
    
    @Slot(str)
    def connectDrone(self, connection_string: str) -> None:
        """Stellt eine Verbindung zur Drohne her"""
        if not connection_string:
            self._update_status("Keine Verbindungsdaten angegeben", is_error=True)
            return
            
        self._update_status(f"Verbinde mit: {connection_string}")
        
        try:
            # Call the appropriate connect method based on the connection string
            if connection_string.startswith("udp:"):
                self._connector.connect_udp(connection_string)
            elif connection_string.startswith("tcp:"):
                self._connector.connect_tcp(connection_string)
            elif connection_string.startswith("simulator"):
                self._connector.connect_simulator()
            else:
                # Assume it's a serial connection
                if ":" in connection_string:
                    port, baudrate = connection_string.split(":", 1)
                    self._connector.connect_serial(port, int(baudrate or "57600"))
                else:
                    self._connector.connect_serial(connection_string, 57600)
                    
        except Exception as e:
            error_msg = f"Verbindungsfehler: {str(e)}"
            self._update_status(error_msg, is_error=True)
            self.errorOccurred.emit(error_msg)
    
    @Slot()
    def disconnect(self) -> None:
        """Trennt die Verbindung zur Drohne"""
        self._update_status("Trenne Verbindung...")
        self._connector.disconnect()
    
    # Callbacks für Verbindungsstatus
    def _on_connected(self) -> None:
        """Wird aufgerufen, wenn eine Verbindung hergestellt wurde"""
        self._is_connected = True
        self._connection_status = "Connected"
        self.connectionStateChanged.emit(True)
        self.connectionStatusChanged.emit()
        self._update_status("Verbindung hergestellt")
    
    def _on_disconnected(self) -> None:
        """Wird aufgerufen, wenn die Verbindung getrennt wurde"""
        self._is_connected = False
        self._connection_status = "Disconnected"
        self.connectionStateChanged.emit(False)
        self.connectionStatusChanged.emit()
        self._update_status("Verbindung getrennt")
    
    def is_connected(self) -> bool:
        """Gibt zurück, ob eine Verbindung zur Drohne besteht"""
        return self._is_connected
    
    def is_armed(self) -> bool:
        """Gibt zurück, ob die Drohne armiert ist"""
        return self._is_armed
    
    def flight_mode(self) -> str:
        """Gibt den aktuellen Flugmodus zurück"""
        return self._flight_mode
    
    def gps_info(self) -> dict:
        """Gibt die GPS-Informationen zurück"""
        return self._gps_info
    
    def battery_info(self) -> dict:
        """Gibt die Batterie-Informationen zurück"""
        return self._battery_info
    
    def attitude(self) -> dict:
        """Gibt die Lage der Drohne zurück"""
        return self._attitude
    
    def heading(self) -> float:
        """Gibt das Heading der Drohne zurück"""
        return self._attitude["yaw_deg"]
    
    def position(self) -> dict:
        """Gibt die Position der Drohne zurück"""
        return self._position
    
    def home_position(self) -> dict:
        """Gibt die Home-Position der Drohne zurück"""
        return self._home_position
    
    # Properties für QML
    connectionState = Property(bool, is_connected, notify=connectionStateChanged)
    connected = Property(bool, is_connected, notify=connectionStateChanged)  # Alias für QML
    armedState = Property(bool, is_armed, notify=armedStateChanged)
    flightMode = Property(str, flight_mode, notify=flightModeChanged)
    
    # Slots für die UI
    
    @Slot(str)
    def connectDrone(self, connection_string: str) -> bool:
        """
        Verbindet mit einer Drohne über den angegebenen Verbindungsstring
        
        Args:
            connection_string: Verbindungsstring (z.B. 'COM3' oder 'udp://127.0.0.1:14550')
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        self._logger.addLog(f"[INFO] Verbinde mit {connection_string}...")
        
        # Überprüfe, ob es sich um einen seriellen Port handelt
        if connection_string.startswith("COM") or "/dev/" in connection_string:
            # Standardbaudrate für serielle Verbindung
            baudrate = 57600
            
            # Prüfe, ob eine Baudrate angegeben wurde (Format: COM3:115200)
            if ":" in connection_string:
                port, baudrate_str = connection_string.split(":")
                try:
                    baudrate = int(baudrate_str)
                except ValueError:
                    self._logger.addLog(f"[WARNUNG] Ungültige Baudrate: {baudrate_str}, verwende Standardbaudrate 57600")
            else:
                port = connection_string
                
            return self.connect_serial(port, baudrate)
        
        # Für andere Verbindungstypen (UDP, TCP, etc.)
        elif ":" in connection_string:
            return self._connector.connect(connection_string)
        else:
            self._logger.addLog(f"[FEHLER] Ungültiger Verbindungsstring: {connection_string}")
            return False
    
    @Slot(str, int)
    def connect_serial(self, port: str, baudrate: int) -> bool:
        """
        Verbindet mit einer Drohne über einen seriellen Port
        
        Args:
            port: COM-Port oder Device (z.B. COM3, /dev/ttyACM0)
            baudrate: Baudrate (z.B. 57600, 115200)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        self._logger.addLog(f"[INFO] Verbinde mit {port} bei {baudrate} Baud...")
        return self._connector.connect_serial(port, baudrate)
    
    @Slot()
    def disconnect(self) -> bool:
        """
        Trennt die Verbindung zur Drohne
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich getrennt wurde
        """
        self._logger.addLog("[INFO] Trenne Verbindung...")
        return self._connector.disconnect()
    
    @Slot()
    def arm(self) -> bool:
        """
        Armiert die Drohne
        
        Returns:
            bool: True, wenn der Armierungs-Befehl erfolgreich gesendet wurde
        """
        return self._connector.arm()
    
    @Slot()
    def disarm(self) -> bool:
        """
        Disarmiert die Drohne
        
        Returns:
            bool: True, wenn der Disarmierungs-Befehl erfolgreich gesendet wurde
        """
        return self._connector.disarm()
    
    @Slot()
    def takeoff(self) -> bool:
        """
        Lässt die Drohne starten
        
        Returns:
            bool: True, wenn der Takeoff-Befehl erfolgreich gesendet wurde
        """
        return self._connector.takeoff()
    
    @Slot()
    def land(self) -> bool:
        """
        Lässt die Drohne landen
        
        Returns:
            bool: True, wenn der Land-Befehl erfolgreich gesendet wurde
        """
        return self._connector.land()
    
    # Signal-Handler
    
    def _on_connected(self):
        """Wird aufgerufen, wenn eine Verbindung hergestellt wurde"""
        self._is_connected = True
        self.connectionStateChanged.emit(True)
        self._logger.addLog("[INFO] Verbindung hergestellt")
    
    def _on_disconnected(self):
        """Wird aufgerufen, wenn die Verbindung getrennt wurde"""
        self._is_connected = False
        self.connectionStateChanged.emit(False)
        self._logger.addLog("[INFO] Verbindung getrennt")
    
    def _on_error_occurred(self, error_message: str):
        """Wird aufgerufen, wenn ein Fehler aufgetreten ist"""
        self.errorOccurred.emit(error_message)
    
    def _on_armed_changed(self, armed: bool):
        """Wird aufgerufen, wenn sich der Armed-Status geändert hat"""
        self._is_armed = armed
        self.armedStateChanged.emit(armed)
    
    def _on_flight_mode_changed(self, mode: str):
        """Wird aufgerufen, wenn sich der Flugmodus geändert hat"""
        self._flight_mode = mode
        self.flightModeChanged.emit(mode)
    
    def _on_gps_info_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die GPS-Informationen geändert haben"""
        self._gps_info = data
        self.gpsInfoChanged.emit(data)
    
    def _on_battery_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die Batterie-Informationen geändert haben"""
        self._battery_info = data
        self.batteryChanged.emit(data)
    
    def _on_attitude_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die Lage der Drohne geändert hat"""
        self._attitude = data
        self.attitudeChanged.emit(data)
    
    def _on_heading_changed(self, heading: float):
        """Wird aufgerufen, wenn sich das Heading der Drohne geändert hat"""
        self.headingChanged.emit(heading)
    
    def _on_position_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die Position der Drohne geändert hat"""
        self._position = data
        self.positionChanged.emit(data)
    
    def _on_home_position_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die Home-Position der Drohne geändert hat"""
        self._home_position = data
        self.homePositionChanged.emit(data)
    
    def _on_statustext_received(self, text: str):
        """
        Wird aufgerufen, wenn ein Status-Text empfangen wurde
        
        Implementiert den speziellen Filtermechanismus für die Preflight-View,
        der Systeminformationen gezielt filtert und hervorhebt.
        """
        # Prüfen, ob es sich um eine Systeminformation handelt
        if text.startswith("[SYSTEM INFO]"):
            # Spezielle Behandlung für die Preflight-View
            # Dies nutzt den speziellen Filtermechanismus, der Systeminformationen
            # (Frame-Typ, RCOut, MicoAir743, ChibiOS, ArduCopter Version, PreArm-Warnungen)
            # gezielt filtert und mit größerer Schrift und Hervorhebung darstellt
            self.systemInfoReceived.emit(text)
        else:
            # Normale Nachricht
            self.messageReceived.emit(text)
    
    # Callback-Handler für die Callback-basierte API
    
    def _on_telemetry_update(self, data: dict):
        """
        Allgemeiner Handler für Telemetrie-Updates über das Callback-Interface
        
        Diese Methode wird aufgerufen, wenn ein Telemetrie-Callback aktiviert wird
        und leitet die Daten an die spezifischen Handler weiter.
        """
        telemetry_type = data.get('type', '')
        
        if telemetry_type == 'armed':
            self._on_armed_changed(data.get('armed', False))
        elif telemetry_type == 'flight_mode':
            self._on_flight_mode_changed(data.get('mode', "UNBEKANNT"))
        elif telemetry_type == 'heading':
            self._on_heading_changed(data.get('heading', 0.0))
        elif telemetry_type == 'position':
            self._on_position_changed(data)
        elif telemetry_type == 'attitude':
            self._on_attitude_changed(data)
        elif telemetry_type == 'battery':
            self._on_battery_changed(data)
        elif telemetry_type == 'gps_info':
            self._on_gps_info_changed(data)
        elif telemetry_type == 'home_position':
            self._on_home_position_changed(data)
