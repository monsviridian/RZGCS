"""
DroneViewModel für RZGCS
Teil der MVVM-Architektur, verantwortlich für die Kommunikation zwischen View und Model
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from typing import Optional

from ..utils.logger import Logger
from ...backend.drone_connection_interface import DroneConnectionInterface


class DroneViewModel(QObject):
    """ViewModel für die Verbindung und Steuerung einer Drohne"""
    
    # Signale für die UI
    connectionChanged = Signal(bool)
    armedChanged = Signal(bool)
    flightModeChanged = Signal(str)
    errorOccurred = Signal(str)
    
    def __init__(self, drone_connection: DroneConnectionInterface, logger: Logger):
        """Initialisiert das DroneViewModel
        
        Args:
            drone_connection: Die DroneConnectionInterface-Implementierung
            logger: Logger-Instanz für die Protokollierung
        """
        super().__init__()
        self._connection = drone_connection
        self._logger = logger
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNBEKANNT"
        
        # Verbinde Signale vom Model
        self._connection.connected.connect(self._handle_connected)
        self._connection.disconnected.connect(self._handle_disconnected)
        self._connection.armed_received.connect(self._handle_armed_changed)
        self._connection.flight_mode_received.connect(self._handle_flight_mode_changed)
        self._connection.error_occurred.connect(self._handle_error)
        
        # Status-Updates-Timer
        self._status_timer = QTimer(self)
        self._status_timer.setInterval(1000)  # 1 Sekunde
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start()
    
    def _update_status(self):
        """Aktualisiert den Status der Drohne periodisch"""
        # Hier könnten weitere periodische Status-Updates erfolgen
        pass
        
    def _handle_connected(self):
        """Wird aufgerufen, wenn die Verbindung hergestellt wurde"""
        self._is_connected = True
        self._logger.addLog("[INFO] Verbindung zur Drohne hergestellt")
        self.connectionChanged.emit(True)
        
    def _handle_disconnected(self):
        """Wird aufgerufen, wenn die Verbindung getrennt wurde"""
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNBEKANNT"
        self._logger.addLog("[INFO] Verbindung zur Drohne getrennt")
        self.connectionChanged.emit(False)
        self.armedChanged.emit(False)
        self.flightModeChanged.emit(self._flight_mode)
        
    def _handle_armed_changed(self, armed: bool):
        """Wird aufgerufen, wenn sich der Armed-Status ändert
        
        Args:
            armed: Neuer Armed-Status
        """
        if self._is_armed != armed:
            self._is_armed = armed
            self._logger.addLog(f"[INFO] Drohne {'armiert' if armed else 'disarmiert'}")
            self.armedChanged.emit(armed)
        
    def _handle_flight_mode_changed(self, flight_mode: str):
        """Wird aufgerufen, wenn sich der Flugmodus ändert
        
        Args:
            flight_mode: Neuer Flugmodus
        """
        if self._flight_mode != flight_mode:
            self._flight_mode = flight_mode
            self._logger.addLog(f"[INFO] Flugmodus geändert: {flight_mode}")
            self.flightModeChanged.emit(flight_mode)
    
    def _handle_error(self, error_message: str):
        """Wird aufgerufen, wenn ein Fehler auftritt
        
        Args:
            error_message: Fehlermeldung
        """
        self._logger.addLog(f"[FEHLER] {error_message}")
        self.errorOccurred.emit(error_message)
    
    @Slot(str, int)
    def connect_serial(self, port: str, baudrate: int) -> bool:
        """Verbindet mit der Drohne über einen seriellen Port
        
        Args:
            port: COM-Port (z.B. 'COM3')
            baudrate: Baudrate (z.B. 57600)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich initiiert wurde
        """
        self._logger.addLog(f"[INFO] Verbinde mit Drohne über {port} bei {baudrate} Baud...")
        return self._connection.connect_serial(port, int(baudrate))
    
    @Slot(str)
    def connect(self, connection_string: str) -> bool:
        """Verbindet mit der Drohne über den angegebenen Verbindungsstring
        
        Args:
            connection_string: Verbindungsstring (z.B. 'udp://:14540')
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich initiiert wurde
        """
        self._logger.addLog(f"[INFO] Verbinde mit Drohne über {connection_string}...")
        return self._connection.connect(connection_string)
    
    @Slot()
    def disconnect(self) -> bool:
        """Trennt die Verbindung zur Drohne
        
        Returns:
            bool: True, wenn die Trennung erfolgreich war
        """
        self._logger.addLog("[INFO] Trenne Verbindung zur Drohne...")
        return self._connection.disconnect()
    
    @Slot()
    def arm(self) -> bool:
        """Armiert die Drohne
        
        Returns:
            bool: True, wenn das Armieren erfolgreich war
        """
        if not self._is_connected:
            self._logger.addLog("[FEHLER] Keine Verbindung zur Drohne")
            return False
        
        self._logger.addLog("[INFO] Armiere Drohne...")
        return self._connection.arm()
    
    @Slot()
    def disarm(self) -> bool:
        """Disarmiert die Drohne
        
        Returns:
            bool: True, wenn das Disarmieren erfolgreich war
        """
        if not self._is_connected:
            self._logger.addLog("[FEHLER] Keine Verbindung zur Drohne")
            return False
        
        self._logger.addLog("[INFO] Disarmiere Drohne...")
        return self._connection.disarm()
    
    @Slot()
    def takeoff(self) -> bool:
        """Lässt die Drohne starten
        
        Returns:
            bool: True, wenn der Start erfolgreich initiiert wurde
        """
        if not self._is_connected:
            self._logger.addLog("[FEHLER] Keine Verbindung zur Drohne")
            return False
        
        if not self._is_armed:
            self._logger.addLog("[FEHLER] Drohne ist nicht armiert")
            return False
        
        self._logger.addLog("[INFO] Starte Drohne...")
        return self._connection.takeoff()
    
    @Slot()
    def land(self) -> bool:
        """Lässt die Drohne landen
        
        Returns:
            bool: True, wenn die Landung erfolgreich initiiert wurde
        """
        if not self._is_connected:
            self._logger.addLog("[FEHLER] Keine Verbindung zur Drohne")
            return False
        
        self._logger.addLog("[INFO] Lande Drohne...")
        return self._connection.land()
    
    @Property(bool, notify=connectionChanged)
    def is_connected(self) -> bool:
        """Gibt zurück, ob eine Verbindung zur Drohne besteht
        
        Returns:
            bool: True, wenn eine Verbindung besteht
        """
        return self._is_connected
    
    @Property(bool, notify=armedChanged)
    def is_armed(self) -> bool:
        """Gibt zurück, ob die Drohne armiert ist
        
        Returns:
            bool: True, wenn die Drohne armiert ist
        """
        return self._is_armed
    
    @Property(str, notify=flightModeChanged)
    def flight_mode(self) -> str:
        """Gibt den aktuellen Flugmodus zurück
        
        Returns:
            str: Aktueller Flugmodus
        """
        return self._flight_mode
