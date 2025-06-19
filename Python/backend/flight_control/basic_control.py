"""
Einfache Steuerungsfunktionen für die Flugsteuerung.
Implementiert grundlegende Flugmanöver und Steuerungsbefehle.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

from .enums import FlightStatus, CommandType
from ..telemetry.telemetry_manager import TelemetryManager

@dataclass
class ControlCommand:
    """Steuerungsbefehl"""
    type: CommandType
    parameters: Dict[str, Any]
    timestamp: datetime = datetime.now()

class BasicControl:
    """Implementiert einfache Steuerungsfunktionen"""
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None):
        """
        Initialisiert die einfache Steuerung.
        
        Args:
            telemetry_manager: Optional: Telemetrie-Manager für Datenabfrage
        """
        self._telemetry = telemetry_manager
        self._status = FlightStatus.DISCONNECTED
        self._last_command: Optional[ControlCommand] = None
        self._command_history: List[ControlCommand] = []
        
    def set_telemetry_manager(self, telemetry_manager: TelemetryManager) -> None:
        """
        Setzt den Telemetrie-Manager.
        
        Args:
            telemetry_manager: Telemetrie-Manager
        """
        self._telemetry = telemetry_manager
        
    def takeoff(self, altitude: float) -> bool:
        """
        Startet das Flugzeug.
        
        Args:
            altitude: Zielhöhe in Metern
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._validate_takeoff(altitude):
            return False
            
        command = ControlCommand(
            type=CommandType.TAKEOFF,
            parameters={'altitude': altitude}
        )
        
        return self._execute_command(command)
        
    def land(self) -> bool:
        """
        Landet das Flugzeug.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._validate_landing():
            return False
            
        command = ControlCommand(
            type=CommandType.LAND,
            parameters={}
        )
        
        return self._execute_command(command)
        
    def return_to_launch(self) -> bool:
        """
        Kehrt zum Startpunkt zurück.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._validate_rtl():
            return False
            
        command = ControlCommand(
            type=CommandType.RTL,
            parameters={}
        )
        
        return self._execute_command(command)
        
    def hold_position(self) -> bool:
        """
        Hält die aktuelle Position.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._validate_hold():
            return False
            
        command = ControlCommand(
            type=CommandType.HOLD,
            parameters={}
        )
        
        return self._execute_command(command)
        
    def set_altitude(self, altitude: float) -> bool:
        """
        Setzt die Flughöhe.
        
        Args:
            altitude: Zielhöhe in Metern
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._validate_altitude(altitude):
            return False
            
        command = ControlCommand(
            type=CommandType.SET_ALTITUDE,
            parameters={'altitude': altitude}
        )
        
        return self._execute_command(command)
        
    def set_heading(self, heading: float) -> bool:
        """
        Setzt den Kurs.
        
        Args:
            heading: Zielkurs in Grad (0-360)
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._validate_heading(heading):
            return False
            
        command = ControlCommand(
            type=CommandType.SET_HEADING,
            parameters={'heading': heading}
        )
        
        return self._execute_command(command)
        
    def set_speed(self, speed: float) -> bool:
        """
        Setzt die Geschwindigkeit.
        
        Args:
            speed: Zielgeschwindigkeit in m/s
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._validate_speed(speed):
            return False
            
        command = ControlCommand(
            type=CommandType.SET_SPEED,
            parameters={'speed': speed}
        )
        
        return self._execute_command(command)
        
    def get_last_command(self) -> Optional[ControlCommand]:
        """
        Gibt den letzten Befehl zurück.
        
        Returns:
            Letzter Befehl oder None
        """
        return self._last_command
        
    def get_command_history(self) -> List[ControlCommand]:
        """
        Gibt die Befehlsgeschichte zurück.
        
        Returns:
            Liste der Befehle
        """
        return self._command_history.copy()
        
    def _execute_command(self, command: ControlCommand) -> bool:
        """
        Führt einen Befehl aus.
        
        Args:
            command: Auszuführender Befehl
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Befehl ausführen
            if command.type == CommandType.TAKEOFF:
                self._execute_takeoff(command.parameters)
            elif command.type == CommandType.LAND:
                self._execute_landing()
            elif command.type == CommandType.RTL:
                self._execute_rtl()
            elif command.type == CommandType.HOLD:
                self._execute_hold()
            elif command.type == CommandType.SET_ALTITUDE:
                self._execute_set_altitude(command.parameters)
            elif command.type == CommandType.SET_HEADING:
                self._execute_set_heading(command.parameters)
            elif command.type == CommandType.SET_SPEED:
                self._execute_set_speed(command.parameters)
            else:
                raise ValueError(f"Unbekannter Befehlstyp: {command.type}")
                
            # Befehl speichern
            self._last_command = command
            self._command_history.append(command)
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Ausführen des Befehls: {str(e)}")
            return False
            
    def _validate_takeoff(self, altitude: float) -> bool:
        """
        Validiert einen Startbefehl.
        
        Args:
            altitude: Zielhöhe
            
        Returns:
            True wenn gültig, sonst False
        """
        if not self._telemetry:
            return False
            
        # Aktuelle Höhe abrufen
        current_altitude = self._telemetry.get_current_data('ALTITUDE')
        if not current_altitude:
            return False
            
        # Höhe validieren
        if altitude <= current_altitude:
            return False
            
        return True
        
    def _validate_landing(self) -> bool:
        """
        Validiert einen Landebefehl.
        
        Returns:
            True wenn gültig, sonst False
        """
        if not self._telemetry:
            return False
            
        # Flugstatus prüfen
        if self._status not in [FlightStatus.FLYING, FlightStatus.ERROR]:
            return False
            
        return True
        
    def _validate_rtl(self) -> bool:
        """
        Validiert einen RTL-Befehl.
        
        Returns:
            True wenn gültig, sonst False
        """
        if not self._telemetry:
            return False
            
        # Flugstatus prüfen
        if self._status not in [FlightStatus.FLYING, FlightStatus.ERROR]:
            return False
            
        return True
        
    def _validate_hold(self) -> bool:
        """
        Validiert einen Hold-Befehl.
        
        Returns:
            True wenn gültig, sonst False
        """
        if not self._telemetry:
            return False
            
        # Flugstatus prüfen
        if self._status != FlightStatus.FLYING:
            return False
            
        return True
        
    def _validate_altitude(self, altitude: float) -> bool:
        """
        Validiert einen Höhenbefehl.
        
        Args:
            altitude: Zielhöhe
            
        Returns:
            True wenn gültig, sonst False
        """
        if not self._telemetry:
            return False
            
        # Aktuelle Höhe abrufen
        current_altitude = self._telemetry.get_current_data('ALTITUDE')
        if not current_altitude:
            return False
            
        # Höhenänderung validieren
        max_altitude_change = 50.0  # Maximale Höhenänderung pro Befehl
        if abs(altitude - current_altitude) > max_altitude_change:
            return False
            
        return True
        
    def _validate_heading(self, heading: float) -> bool:
        """
        Validiert einen Kursbefehl.
        
        Args:
            heading: Zielkurs
            
        Returns:
            True wenn gültig, sonst False
        """
        if not self._telemetry:
            return False
            
        # Kurs validieren
        if not (0 <= heading <= 360):
            return False
            
        return True
        
    def _validate_speed(self, speed: float) -> bool:
        """
        Validiert einen Geschwindigkeitsbefehl.
        
        Args:
            speed: Zielgeschwindigkeit
            
        Returns:
            True wenn gültig, sonst False
        """
        if not self._telemetry:
            return False
            
        # Geschwindigkeit validieren
        min_speed = 5.0  # Minimale Geschwindigkeit
        max_speed = 30.0  # Maximale Geschwindigkeit
        if not (min_speed <= speed <= max_speed):
            return False
            
        return True
        
    def _execute_takeoff(self, parameters: Dict[str, Any]) -> None:
        """
        Führt einen Startbefehl aus.
        
        Args:
            parameters: Befehlsparameter
        """
        altitude = parameters['altitude']
        # TODO: Implementierung
        
    def _execute_landing(self) -> None:
        """Führt einen Landebefehl aus"""
        # TODO: Implementierung
        
    def _execute_rtl(self) -> None:
        """Führt einen RTL-Befehl aus"""
        # TODO: Implementierung
        
    def _execute_hold(self) -> None:
        """Führt einen Hold-Befehl aus"""
        # TODO: Implementierung
        
    def _execute_set_altitude(self, parameters: Dict[str, Any]) -> None:
        """
        Führt einen Höhenbefehl aus.
        
        Args:
            parameters: Befehlsparameter
        """
        altitude = parameters['altitude']
        # TODO: Implementierung
        
    def _execute_set_heading(self, parameters: Dict[str, Any]) -> None:
        """
        Führt einen Kursbefehl aus.
        
        Args:
            parameters: Befehlsparameter
        """
        heading = parameters['heading']
        # TODO: Implementierung
        
    def _execute_set_speed(self, parameters: Dict[str, Any]) -> None:
        """
        Führt einen Geschwindigkeitsbefehl aus.
        
        Args:
            parameters: Befehlsparameter
        """
        speed = parameters['speed']
        # TODO: Implementierung 