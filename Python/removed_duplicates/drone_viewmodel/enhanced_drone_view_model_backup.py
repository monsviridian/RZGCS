#!/usr/bin/env python3
"""
Enhanced DroneViewModel - ViewModel für die Drohnensteuerung im MVVM-Pattern

Dieses ViewModel stellt die Verbindung zwischen der UI und dem EnhancedMAVSDKConnector her
und implementiert die entsprechende Geschäftslogik mit Unterstützung für Nachrichtenfilterung
und die spezielle Preflight-View für Systeminformationen.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

from backend.enhanced_mavsdk_connector import EnhancedMAVSDKConnector
from backend.drone_connection_interface import DroneConnectionInterface
from backend.logger import Logger


class EnhancedDroneViewModel(QObject):
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
        self._connector = EnhancedMAVSDKConnector(logger)
        
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
        
        # Signale mit Callbacks verbinden
        self._register_callbacks()
    
    def _register_callbacks(self):
        """Registriert die Callbacks beim Connector"""
        # Verbindungsstatus durch direkte Signal-Verbindungen über den DroneSignalHub
        self._connector._signals.connection_established.connect(self._on_connected)
        self._connector._signals.connection_lost.connect(self._on_disconnected)
        self._connector._signals.error_occurred.connect(self._on_error_occurred)
        
        # Telemetrie-Signale direkt verbinden
        self._connector._signals.armed_changed.connect(self._on_armed_changed_direct)
        self._connector._signals.flight_mode_changed.connect(self._on_flight_mode_changed_direct)
        self._connector._signals.gps_info_changed.connect(self._on_gps_info_changed)
        self._connector._signals.battery_changed.connect(self._on_battery_changed)
        self._connector._signals.attitude_changed.connect(self._on_attitude_changed)
        self._connector._signals.heading_changed.connect(self._on_heading_changed_direct)
        self._connector._signals.position_changed.connect(self._on_position_changed)
        self._connector._signals.home_position_changed.connect(self._on_home_position_changed)
        
        # Status-Texte
        self._connector._signals.statustext_received.connect(self._on_statustext_received)
        
        # Zusätzlich auch die Callback-basierte Registrierung verwenden
        # Dies stellt sicher, dass das ViewModel sowohl mit direkten Signalen als auch
        # mit dem Callback-Interface funktioniert
        self._connector.register_connection_callback(self._on_connected)
        self._connector.register_disconnection_callback(self._on_disconnected)
        
        # Register für verschiedene Telemetrie-Typen
        for telemetry_type in ['armed', 'flight_mode', 'gps_info', 'battery', 'attitude', 
                             'heading', 'position', 'home_position']:
            self._connector.register_telemetry_callback(telemetry_type, self._on_telemetry_update)
        
        self._connector.register_statustext_callback(self._on_statustext_received)
    
    # Properties für die UI
    
    def is_connected(self) -> bool:
        """Gibt zurück, ob eine Verbindung zur Drohne besteht"""
        return self._is_connected
        
    # connected als Alias für connectionState (für QML-Kompatibilität)
    connected = Property(bool, is_connected, notify=connectionStateChanged)
    
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
    armedState = Property(bool, is_armed, notify=armedStateChanged)
    flightMode = Property(str, flight_mode, notify=flightModeChanged)
    
    # Slots für die UI
    
    @Slot(str)
    def connect(self, connection_string: str) -> bool:
        """
        Universelle Verbindungsmethode für verschiedene Verbindungsarten
        
        Args:
            connection_string: Verbindungsstring im Format
                - COM8 oder COM8:115200 (serieller Port mit optionaler Baudrate)
                - /dev/ttyACM0 oder /dev/ttyACM0:115200 (Linux-Port mit Baudrate)
                - udp://127.0.0.1:14540 (UDP-Verbindung)
                - tcp://127.0.0.1:5760 (TCP-Verbindung)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        self._logger.addLog(f"[INFO] Verbinde mit {connection_string}...")
        return self._connector.connect(connection_string)
    
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
    
    # Callback-Handler
    
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
        
    # Direkte Signal-Handler (für die direkten Signale aus dem DroneSignalHub)
    
    def _on_armed_changed_direct(self, armed: bool):
        """Direkter Handler für das armed_changed Signal"""
        self._is_armed = armed
        self.armedStateChanged.emit(armed)
    
    def _on_flight_mode_changed_direct(self, mode: str):
        """Direkter Handler für das flight_mode_changed Signal"""
        self._flight_mode = mode
        self.flightModeChanged.emit(mode)
    
    def _on_heading_changed_direct(self, heading: float):
        """Direkter Handler für das heading_changed Signal"""
        self.headingChanged.emit(heading)
    
    # Callback-basierte Handler
    
    def _on_telemetry_update(self, data: dict):
        """Allgemeiner Handler für Telemetrie-Updates über das Callback-Interface"""
        # Diese Methode wird aufgerufen, wenn ein Telemetrie-Callback aktiviert wird
        # Die Daten werden dann an die spezifischen Handler weitergeleitet
        telemetry_type = data.get('type', '')
        
        if telemetry_type == 'armed':
            self._on_armed_changed(data)
        elif telemetry_type == 'flight_mode':
            self._on_flight_mode_changed(data)
        elif telemetry_type == 'heading':
            self._on_heading_changed(data)
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
    
    def _on_armed_changed(self, data: dict):
        """Wird aufgerufen, wenn sich der Armed-Status geändert hat"""
        armed = data.get('armed', False)
        self._is_armed = armed
        self.armedStateChanged.emit(armed)
    
    def _on_flight_mode_changed(self, data: dict):
        """Wird aufgerufen, wenn sich der Flugmodus geändert hat"""
        mode = data.get('mode', "UNBEKANNT")
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
    
    def _on_heading_changed(self, data: dict):
        """Wird aufgerufen, wenn sich das Heading der Drohne geändert hat"""
        heading = data.get('heading', 0.0)
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
