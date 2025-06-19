"""
Verbindungs-Service.
Implementiert die Geschäftslogik für Verbindungs-Operationen.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import math

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ..models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan
from ..enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

class ConnectionService(QObject):
    """Implementiert die Geschäftslogik für Verbindungs-Operationen"""
    
    # Signale
    state_changed = Signal(FlightState)
    mode_changed = Signal(FlightMode)
    error_occurred = Signal(str)
    command_executed = Signal(ControlCommand)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    connection_established = Signal()  # Neues Signal für hergestellte Verbindung
    connection_lost = Signal()  # Neues Signal für verlorene Verbindung
    connection_restored = Signal()  # Neues Signal für wiederhergestellte Verbindung
    connection_failed = Signal(str)  # Neues Signal für fehlgeschlagene Verbindung
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den Verbindungs-Service.
        
        Args:
            telemetry_manager: Optional: Telemetrie-Manager
            connection_manager: Optional: Verbindungs-Manager
        """
        super().__init__()
        
        # Manager setzen
        self._telemetry = telemetry_manager
        self._connection = connection_manager
        
        # Status und Modus
        self._state = FlightState(
            position=Position(0.0, 0.0, 0.0),
            mode=FlightMode.MANUAL,
            armed=False,
            status=FlightStatus.DISARMED,
            parameters={}
        )
        self._mode = FlightMode.MANUAL
        self._control_mode = ControlMode.BASIC
        
        # Verbindungs-Parameter
        self._connection_active = False
        self._connection_timeout = 5.0  # Verbindungs-Timeout in Sekunden
        self._reconnect_attempts = 3  # Maximale Anzahl an Wiederverbindungsversuchen
        self._reconnect_delay = 1.0  # Verzögerung zwischen Wiederverbindungsversuchen in Sekunden
        self._last_heartbeat: Optional[datetime] = None
        self._heartbeat_interval = 1.0  # Heartbeat-Intervall in Sekunden
        
        # Timer für Statusaktualisierungen
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(100)  # 100ms
        
    def set_telemetry_manager(self, telemetry_manager: TelemetryManager) -> None:
        """
        Setzt den Telemetrie-Manager.
        
        Args:
            telemetry_manager: Telemetrie-Manager
        """
        self._telemetry = telemetry_manager
        
    def set_connection_manager(self, connection_manager: ConnectionManager) -> None:
        """
        Setzt den Verbindungs-Manager.
        
        Args:
            connection_manager: Verbindungs-Manager
        """
        self._connection = connection_manager
        
    @Slot(FlightMode)
    def set_mode(self, mode: FlightMode) -> bool:
        """
        Setzt den Flugmodus.
        
        Args:
            mode: Flugmodus
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Prüfen ob Modus-Änderung erlaubt ist
        if not self._can_change_mode(mode):
            self._set_error(f"Modus-Änderung nicht erlaubt: {mode.name}")
            return False
            
        # Modus setzen
        self._mode = mode
        self.mode_changed.emit(mode)
        return True
        
    @Slot(ControlCommand)
    def execute_command(self, command: ControlCommand) -> bool:
        """
        Führt einen Steuerungsbefehl aus.
        
        Args:
            command: Steuerungsbefehl
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Prüfen ob Befehl ausgeführt werden darf
        if not self._can_execute_command(command):
            self._set_error(f"Befehl nicht erlaubt: {command.type.name}")
            return False
            
        # Befehl ausführen
        success = self._execute_command(command)
        
        if success:
            self.command_executed.emit(command)
            
        return success
        
    def set_connection_parameters(self, timeout: float, reconnect_attempts: int,
                                reconnect_delay: float, heartbeat_interval: float) -> None:
        """
        Setzt die Verbindungs-Parameter.
        
        Args:
            timeout: Verbindungs-Timeout in Sekunden
            reconnect_attempts: Maximale Anzahl an Wiederverbindungsversuchen
            reconnect_delay: Verzögerung zwischen Wiederverbindungsversuchen in Sekunden
            heartbeat_interval: Heartbeat-Intervall in Sekunden
        """
        self._connection_timeout = timeout
        self._reconnect_attempts = reconnect_attempts
        self._reconnect_delay = reconnect_delay
        self._heartbeat_interval = heartbeat_interval
        
    def connect(self) -> bool:
        """
        Stellt eine Verbindung her.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._connection_active:
            self._set_error("Verbindung bereits aktiv")
            return False
            
        if not self._connection:
            self._set_error("Kein Verbindungs-Manager verfügbar")
            return False
            
        # Verbindung herstellen
        success = self._connection.connect()
        
        if success:
            self._connection_active = True
            self._last_heartbeat = datetime.now()
            self.connection_established.emit()
            
        return success
        
    def disconnect(self) -> bool:
        """
        Trennt die Verbindung.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._connection_active:
            self._set_error("Keine aktive Verbindung")
            return False
            
        if not self._connection:
            self._set_error("Kein Verbindungs-Manager verfügbar")
            return False
            
        # Verbindung trennen
        success = self._connection.disconnect()
        
        if success:
            self._connection_active = False
            self._last_heartbeat = None
            
        return success
        
    def reconnect(self) -> bool:
        """
        Stellt die Verbindung wieder her.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Verbindung trennen
        self.disconnect()
        
        # Wiederverbindungsversuche
        for attempt in range(self._reconnect_attempts):
            if self.connect():
                self.connection_restored.emit()
                return True
                
            # Verzögerung
            QTimer.singleShot(int(self._reconnect_delay * 1000), lambda: None)
            
        # Alle Versuche fehlgeschlagen
        self.connection_failed.emit("Maximale Anzahl an Wiederverbindungsversuchen erreicht")
        return False
        
    @Slot()
    def _update_status(self) -> None:
        """
        Aktualisiert den Flugzustand.
        """
        if not self._telemetry:
            return
            
        # Telemetrie-Daten abrufen
        telemetry_data = self._telemetry.get_telemetry_data()
        
        if not telemetry_data:
            self._handle_connection_lost()
            return
            
        # Verbindung wiederhergestellt
        if not self._connection_active:
            self._handle_connection_restored()
            
        # Status aktualisieren
        self._state.position = telemetry_data.get("position", Position())
        self._state.velocity = telemetry_data.get("velocity", Position())
        self._state.acceleration = telemetry_data.get("acceleration", Position())
        self._state.attitude = telemetry_data.get("attitude", Position())
        self._state.angular_velocity = telemetry_data.get("angular_velocity", Position())
        self._state.battery_level = telemetry_data.get("battery_level", 0.0)
        self._state.signal_strength = telemetry_data.get("signal_strength", 0.0)
        
        # Status-Änderung signalisieren
        self.state_changed.emit(self._state)
        
        # Heartbeat prüfen
        if self._connection_active:
            self._check_heartbeat()
            
    def _check_heartbeat(self) -> None:
        """
        Prüft den Heartbeat.
        """
        if not self._last_heartbeat:
            return
            
        # Zeit seit letztem Heartbeat
        duration = (datetime.now() - self._last_heartbeat).total_seconds()
        
        # Timeout prüfen
        if duration > self._heartbeat_interval:
            self._handle_connection_lost()
            return
            
        # Heartbeat senden
        if self._connection:
            self._connection.send_heartbeat()
            self._last_heartbeat = datetime.now()
            
    def _handle_connection_lost(self) -> None:
        """
        Behandelt einen Verbindungsverlust.
        """
        if self._connection_active:
            self._connection_active = False
            self.connection_lost.emit()
            
    def _handle_connection_restored(self) -> None:
        """
        Behandelt eine wiederhergestellte Verbindung.
        """
        if not self._connection_active:
            self._connection_active = True
            self._last_heartbeat = datetime.now()
            self.connection_restored.emit()
            
    def _can_change_mode(self, mode: FlightMode) -> bool:
        """
        Prüft ob ein Modus-Wechsel erlaubt ist.
        
        Args:
            mode: Neuer Modus
            
        Returns:
            True wenn erlaubt, sonst False
        """
        # TODO: Implementierung der Modus-Wechsel-Prüfung
        return True
        
    def _can_execute_command(self, command: ControlCommand) -> bool:
        """
        Prüft ob ein Befehl ausgeführt werden darf.
        
        Args:
            command: Zu prüfender Befehl
            
        Returns:
            True wenn erlaubt, sonst False
        """
        # TODO: Implementierung der Befehls-Prüfung
        return True
        
    def _execute_command(self, command: ControlCommand) -> bool:
        """
        Führt einen Steuerungsbefehl aus.
        
        Args:
            command: Steuerungsbefehl
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._connection:
            return False
            
        # Befehl senden
        return self._connection.send_command(command)
        
    def _set_state(self, status: FlightStatus) -> None:
        """
        Setzt den Flugzustand.
        
        Args:
            status: Neuer Status
        """
        if self._state.status != status:
            self._state.status = status
            self.state_changed.emit(self._state)
            
    def _set_error(self, message: str) -> None:
        """
        Setzt eine Fehlermeldung.
        
        Args:
            message: Fehlermeldung
        """
        self.error_occurred.emit(message) 