"""
MAVLink Telemetrie Adapter.
Konvertiert MAVLink-Nachrichten in Telemetriedaten für das RZGCS.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

from PySide6.QtCore import QObject, Signal, Slot

from ..message_handler import MessageHandler
from backend.flight_control.models.flight_data import Position, FlightState
from backend.flight_control.enums import FlightStatus, FlightMode
from backend.flight_control.services.telemetry_service import TelemetryService

logger = logging.getLogger(__name__)

class MAVLinkTelemetryAdapter(QObject):
    """
    Adapter zur Konvertierung von MAVLink-Nachrichten in Telemetriedaten.
    Fungiert als Brücke zwischen MessageHandler und TelemetryService.
    """
    
    # Signale für Debug und Fehler
    adapter_initialized = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        """Initialisiert den Adapter."""
        super().__init__(parent)
        
        self._message_handler: Optional[MessageHandler] = None
        self._telemetry_service: Optional[TelemetryService] = None
        
        # Zwischenspeicher für aktuelle Daten
        self._position = Position(0.0, 0.0, 0.0)
        self._flight_mode = FlightMode.MANUAL
        self._armed = False
        self._status = FlightStatus.DISCONNECTED
        self._parameters = {}
        
        # Flag für Diagnose und Debug
        self._debug_mode = False
        
    def set_message_handler(self, message_handler: MessageHandler) -> None:
        """
        Konfiguriert den MessageHandler und verbindet die Signale.
        
        Args:
            message_handler: MessageHandler-Instanz
        """
        if self._message_handler:
            self._disconnect_message_handler()
            
        self._message_handler = message_handler
        
        # Verbinden der vorhandenen Signale
        # Wir verwenden nur Signale, die tatsächlich in MessageHandler definiert sind
        self._message_handler.attitude_received.connect(self._on_attitude_update)
        self._message_handler.vfr_hud_received.connect(self._on_vfr_hud_update)  # VFR_HUD enthält auch Höheninformationen
        self._message_handler.heartbeat_received.connect(self._on_heartbeat_update)
        self._message_handler.gps_received.connect(self._on_gps_update)  # Verwendung des tatsächlichen Signals
        self._message_handler.battery_received.connect(self._on_battery_update)  # Batteriesignal
        self._message_handler.raw_message_received.connect(self._on_raw_mavlink_message)
        
        logger.info("MAVLinkTelemetryAdapter: MessageHandler verbunden")
        
    def set_telemetry_service(self, telemetry_service: TelemetryService) -> None:
        """
        Setzt den TelemetryService und sendet initiale Daten.
        
        Args:
            telemetry_service: TelemetryService-Instanz
        """
        self._telemetry_service = telemetry_service
        
        # Initialen Zustand senden, falls wir schon Daten haben
        self._update_flight_state()
        logger.info("MAVLinkTelemetryAdapter: TelemetryService verbunden")
        
    def set_debug_mode(self, enabled: bool) -> None:
        """
        Aktiviert oder deaktiviert den Debug-Modus.
        
        Args:
            enabled: True für Debug-Modus, False für normalen Modus
        """
        self._debug_mode = enabled
        logger.info(f"MAVLinkTelemetryAdapter: Debug-Modus {'aktiviert' if enabled else 'deaktiviert'}")
        
    def _disconnect_message_handler(self) -> None:
        """Trennt alle Signal-Verbindungen zum aktuellen MessageHandler."""
        if not self._message_handler:
            return
        
        # Nur die tatsächlich vorhandenen Signalverbindungen trennen
        try:    
            self._message_handler.attitude_received.disconnect(self._on_attitude_update)
            self._message_handler.vfr_hud_received.disconnect(self._on_vfr_hud_update)
            self._message_handler.heartbeat_received.disconnect(self._on_heartbeat_update)
            self._message_handler.gps_received.disconnect(self._on_gps_update)
            self._message_handler.battery_received.disconnect(self._on_battery_update)
            self._message_handler.raw_message_received.disconnect(self._on_raw_mavlink_message)
        except Exception as e:
            logger.warning(f"Fehler beim Trennen der Signalverbindungen: {e}")
        
        logger.info("MAVLinkTelemetryAdapter: MessageHandler getrennt")
        
    def _update_flight_state(self) -> None:
        """Aktualisiert den Flugzustand im TelemetryService."""
        if not self._telemetry_service:
            return
            
        # Neuen Flugzustand erstellen
        flight_state = FlightState(
            position=self._position,
            mode=self._flight_mode,
            armed=self._armed,
            status=self._status,
            parameters=self._parameters
        )
        
        # Signale senden mit korrekten camelCase Signal-Namen
        self._telemetry_service.stateChanged.emit(flight_state)
        self._telemetry_service.modeChanged.emit(self._flight_mode)
        
        # Für die anderen Daten verwenden wir das allgemeine telemetry_updated Signal
        # und senden ein Dictionary mit allen relevanten Telemetriedaten
        telemetry_data = {
            'position': self._position,
            'mode': self._flight_mode,
            'status': self._status,
            'parameters': self._parameters
        }
        self._telemetry_service.telemetryUpdated.emit(telemetry_data)
        
        if self._debug_mode:
            logger.debug(f"MAVLinkTelemetryAdapter: Flugzustand aktualisiert: {flight_state}")
            
    # Handler für MAVLink-Nachrichten
    
    def _on_altitude_update(self, altitude_data: Dict[str, Any]) -> None:
        """Verarbeitet ALTITUDE-Nachrichten."""
        # Altitude-Daten verarbeiten und in Position übertragen
        self._position.z = altitude_data.get("altitude_terrain", 0.0)
        self._parameters["altitude_relative"] = altitude_data.get("altitude_relative", 0.0)
        self._parameters["altitude_amsl"] = altitude_data.get("altitude_amsl", 0.0)
        
        # Zustand aktualisieren
        self._update_flight_state()
        
    def _on_attitude_update(self, attitude_data: Dict[str, Any]) -> None:
        """Verarbeitet ATTITUDE-Nachrichten."""
        # Attitude-Daten in Parameter übertragen
        self._parameters["roll"] = attitude_data.get("roll", 0.0)
        self._parameters["pitch"] = attitude_data.get("pitch", 0.0)
        self._parameters["yaw"] = attitude_data.get("yaw", 0.0)
        
        # Zustand aktualisieren
        self._update_flight_state()
        
    def _on_vfr_hud_update(self, vfr_data: Dict[str, Any]) -> None:
        """Verarbeitet VFR_HUD-Nachrichten."""
        # VFR_HUD-Daten in Parameter übertragen
        self._parameters["airspeed"] = vfr_data.get("airspeed", 0.0)
        self._parameters["groundspeed"] = vfr_data.get("groundspeed", 0.0)
        self._parameters["heading"] = vfr_data.get("heading", 0.0)
        self._parameters["throttle"] = vfr_data.get("throttle", 0.0)
        
        # Zustand aktualisieren
        self._update_flight_state()
        
    def _on_heartbeat_update(self, heartbeat_data: Dict[str, Any]) -> None:
        """Verarbeitet HEARTBEAT-Nachrichten."""
        # Status aus base_mode extrahieren
        base_mode = heartbeat_data.get("base_mode", 0)
        custom_mode = heartbeat_data.get("custom_mode", 0)
        
        # Armed-Status aus base_mode (Bit 7) extrahieren
        self._armed = bool(base_mode & 0x80)  # 0x80 ist 10000000 in binär, also Bit 7
        
        # Flugmodus aus base_mode und custom_mode extrahieren
        # Vereinfachte Version - in der Praxis komplexere Logik notwendig
        if custom_mode == 0:
            self._flight_mode = FlightMode.MANUAL
        elif custom_mode == 3:
            self._flight_mode = FlightMode.AUTO
        elif custom_mode == 4:
            self._flight_mode = FlightMode.GUIDED
        else:
            self._flight_mode = FlightMode.STABILIZED
        
        # Status aktualisieren basierend auf system_status
        system_status = heartbeat_data.get("system_status", 0)
        if system_status == 0:
            self._status = FlightStatus.STANDBY
        elif system_status == 3:
            self._status = FlightStatus.FLYING
        elif system_status == 4:
            self._status = FlightStatus.CRITICAL
        elif system_status > 5:
            self._status = FlightStatus.EMERGENCY
        else:
            self._status = FlightStatus.CONNECTED
        
        # Zustand aktualisieren
        self._update_flight_state()
        
    def _on_gps_update(self, gps_data: Dict[str, Any]) -> None:
        """Verarbeitet GPS-Nachrichten."""
        # GPS-Daten in Position übertragen (mit angepasster Struktur)
        if "lat" in gps_data and "lon" in gps_data:
            # Das Format hängt von der tatsächlichen Implementierung ab
            # Wir nehmen an, dass die Werte bereits als Float in Grad vorliegen
            self._position.x = gps_data["lon"]
            self._position.y = gps_data["lat"]
            
            # GPS-Informationen in Parameter speichern
            self._parameters["fix_type"] = gps_data.get("fix_type", 0)
            self._parameters["satellites_visible"] = gps_data.get("satellites_visible", 0)
            
            if "alt" in gps_data:
                # Höhe direkt verwenden oder konvertieren, je nach Format
                self._parameters["gps_altitude"] = gps_data["alt"]
                # Zusätzlich auch die Position.z setzen
                self._position.z = gps_data["alt"]
            
            # Zustand aktualisieren
            self._update_flight_state()
            
    def _on_battery_update(self, battery_data: Dict[str, Any]) -> None:
        """Verarbeitet Batterie-Nachrichten."""
        # Batterieinformationen in Parameter übertragen
        if "percentage" in battery_data:
            self._parameters["battery_percentage"] = battery_data["percentage"]
        
        if "voltage" in battery_data:
            self._parameters["battery_voltage"] = battery_data["voltage"]
            
        if "current" in battery_data:
            self._parameters["battery_current"] = battery_data["current"]
        
        # Zustand aktualisieren
        self._update_flight_state()
        
    def _on_sys_status_update(self, status_data: Dict[str, Any]) -> None:
        """Verarbeitet SYS_STATUS-Nachrichten."""
        # Batterieinformationen extrahieren und in Parameter übertragen
        if "battery_remaining" in status_data:
            self._parameters["battery_percentage"] = status_data["battery_remaining"]
        
        if "voltage_battery" in status_data:
            # Umrechnung von Millivolt zu Volt
            self._parameters["battery_voltage"] = status_data["voltage_battery"] / 1000.0
            
        if "current_battery" in status_data:
            # Umrechnung von 10*mA zu A
            self._parameters["battery_current"] = status_data["current_battery"] / 100.0
        
        # Zustand aktualisieren
        self._update_flight_state()
        
    def _on_raw_mavlink_message(self, message: object) -> None:
        """
        Verarbeitet rohe MAVLink-Nachrichten direkt.
        
        Args:
            message: Pymavlink-Nachrichtenobjekt
        """
        if not self._debug_mode:
            return
            
        # Debug-Informationen für alle Nachrichtentypen
        if hasattr(message, 'get_type'):
            msg_type = message.get_type()
            logger.debug(f"MAVLinkTelemetryAdapter: Rohe MAVLink-Nachricht empfangen: {msg_type}")