"""
Wegpunkt-Manager für die Flugsteuerung.
Verwaltet Wegpunkte und Missionen.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math
import json

from .enums import WaypointType, MissionStatus, ValidationResult
from ..telemetry.telemetry_manager import TelemetryManager

@dataclass
class Waypoint:
    """Wegpunkt für die Flugsteuerung"""
    id: int
    type: WaypointType
    latitude: float
    longitude: float
    altitude: float
    parameters: Dict[str, Any]
    timestamp: datetime = datetime.now()

@dataclass
class Mission:
    """Mission für die Flugsteuerung"""
    id: int
    name: str
    waypoints: List[Waypoint]
    status: MissionStatus
    parameters: Dict[str, Any]
    timestamp: datetime = datetime.now()

class WaypointManager:
    """Verwaltet Wegpunkte und Missionen"""
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None):
        """
        Initialisiert den Wegpunkt-Manager.
        
        Args:
            telemetry_manager: Optional: Telemetrie-Manager für Datenabfrage
        """
        self._telemetry = telemetry_manager
        self._waypoints: List[Waypoint] = []
        self._missions: List[Mission] = []
        self._current_mission: Optional[Mission] = None
        self._current_waypoint_index: int = -1
        
    def set_telemetry_manager(self, telemetry_manager: TelemetryManager) -> None:
        """
        Setzt den Telemetrie-Manager.
        
        Args:
            telemetry_manager: Telemetrie-Manager
        """
        self._telemetry = telemetry_manager
        
    def add_waypoint(self, waypoint: Waypoint) -> bool:
        """
        Fügt einen Wegpunkt hinzu.
        
        Args:
            waypoint: Wegpunkt
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Wegpunkt validieren
        if not self._validate_waypoint(waypoint):
            return False
            
        # Wegpunkt hinzufügen
        self._waypoints.append(waypoint)
        return True
        
    def remove_waypoint(self, waypoint_id: int) -> bool:
        """
        Entfernt einen Wegpunkt.
        
        Args:
            waypoint_id: ID des Wegpunkts
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Wegpunkt finden
        waypoint = self._find_waypoint(waypoint_id)
        if not waypoint:
            return False
            
        # Wegpunkt entfernen
        self._waypoints.remove(waypoint)
        return True
        
    def update_waypoint(self, waypoint: Waypoint) -> bool:
        """
        Aktualisiert einen Wegpunkt.
        
        Args:
            waypoint: Wegpunkt
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Wegpunkt validieren
        if not self._validate_waypoint(waypoint):
            return False
            
        # Wegpunkt finden
        index = self._find_waypoint_index(waypoint.id)
        if index == -1:
            return False
            
        # Wegpunkt aktualisieren
        self._waypoints[index] = waypoint
        return True
        
    def get_waypoint(self, waypoint_id: int) -> Optional[Waypoint]:
        """
        Gibt einen Wegpunkt zurück.
        
        Args:
            waypoint_id: ID des Wegpunkts
            
        Returns:
            Wegpunkt oder None
        """
        return self._find_waypoint(waypoint_id)
        
    def get_all_waypoints(self) -> List[Waypoint]:
        """
        Gibt alle Wegpunkte zurück.
        
        Returns:
            Liste der Wegpunkte
        """
        return self._waypoints.copy()
        
    def create_mission(self, name: str, waypoints: List[Waypoint], parameters: Optional[Dict[str, Any]] = None) -> Optional[Mission]:
        """
        Erstellt eine Mission.
        
        Args:
            name: Name der Mission
            waypoints: Liste der Wegpunkte
            parameters: Optional: Missionsparameter
            
        Returns:
            Mission oder None
        """
        # Mission validieren
        if not self._validate_mission(name, waypoints):
            return None
            
        # Mission erstellen
        mission = Mission(
            id=len(self._missions),
            name=name,
            waypoints=waypoints.copy(),
            status=MissionStatus.NOT_STARTED,
            parameters=parameters or {}
        )
        
        # Mission hinzufügen
        self._missions.append(mission)
        return mission
        
    def start_mission(self, mission_id: int) -> bool:
        """
        Startet eine Mission.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Mission finden
        mission = self._find_mission(mission_id)
        if not mission:
            return False
            
        # Mission validieren
        if not self._validate_mission_start(mission):
            return False
            
        # Mission starten
        mission.status = MissionStatus.IN_PROGRESS
        self._current_mission = mission
        self._current_waypoint_index = 0
        
        return True
        
    def pause_mission(self) -> bool:
        """
        Pausiert die aktuelle Mission.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._current_mission:
            return False
            
        # Mission pausieren
        self._current_mission.status = MissionStatus.PAUSED
        return True
        
    def resume_mission(self) -> bool:
        """
        Setzt die aktuelle Mission fort.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._current_mission:
            return False
            
        # Mission fortsetzen
        self._current_mission.status = MissionStatus.IN_PROGRESS
        return True
        
    def abort_mission(self) -> bool:
        """
        Bricht die aktuelle Mission ab.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._current_mission:
            return False
            
        # Mission abbrechen
        self._current_mission.status = MissionStatus.ABORTED
        self._current_mission = None
        self._current_waypoint_index = -1
        
        return True
        
    def get_current_mission(self) -> Optional[Mission]:
        """
        Gibt die aktuelle Mission zurück.
        
        Returns:
            Mission oder None
        """
        return self._current_mission
        
    def get_current_waypoint(self) -> Optional[Waypoint]:
        """
        Gibt den aktuellen Wegpunkt zurück.
        
        Returns:
            Wegpunkt oder None
        """
        if not self._current_mission or self._current_waypoint_index == -1:
            return None
            
        return self._current_mission.waypoints[self._current_waypoint_index]
        
    def get_next_waypoint(self) -> Optional[Waypoint]:
        """
        Gibt den nächsten Wegpunkt zurück.
        
        Returns:
            Wegpunkt oder None
        """
        if not self._current_mission:
            return None
            
        next_index = self._current_waypoint_index + 1
        if next_index >= len(self._current_mission.waypoints):
            return None
            
        return self._current_mission.waypoints[next_index]
        
    def export_mission(self, mission_id: int, file_path: str) -> bool:
        """
        Exportiert eine Mission in eine Datei.
        
        Args:
            mission_id: ID der Mission
            file_path: Pfad zur Datei
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Mission finden
        mission = self._find_mission(mission_id)
        if not mission:
            return False
            
        try:
            # Mission in JSON konvertieren
            mission_data = {
                'id': mission.id,
                'name': mission.name,
                'status': mission.status.value,
                'parameters': mission.parameters,
                'timestamp': mission.timestamp.isoformat(),
                'waypoints': [
                    {
                        'id': wp.id,
                        'type': wp.type.value,
                        'latitude': wp.latitude,
                        'longitude': wp.longitude,
                        'altitude': wp.altitude,
                        'parameters': wp.parameters,
                        'timestamp': wp.timestamp.isoformat()
                    }
                    for wp in mission.waypoints
                ]
            }
            
            # JSON in Datei schreiben
            with open(file_path, 'w') as f:
                json.dump(mission_data, f, indent=4)
                
            return True
            
        except Exception as e:
            print(f"Fehler beim Exportieren der Mission: {e}")
            return False
            
    def import_mission(self, file_path: str) -> Optional[Mission]:
        """
        Importiert eine Mission aus einer Datei.
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Mission oder None
        """
        try:
            # JSON aus Datei lesen
            with open(file_path, 'r') as f:
                mission_data = json.load(f)
                
            # Wegpunkte erstellen
            waypoints = []
            for wp_data in mission_data['waypoints']:
                waypoint = Waypoint(
                    id=wp_data['id'],
                    type=WaypointType(wp_data['type']),
                    latitude=wp_data['latitude'],
                    longitude=wp_data['longitude'],
                    altitude=wp_data['altitude'],
                    parameters=wp_data['parameters'],
                    timestamp=datetime.fromisoformat(wp_data['timestamp'])
                )
                waypoints.append(waypoint)
                
            # Mission erstellen
            mission = Mission(
                id=mission_data['id'],
                name=mission_data['name'],
                waypoints=waypoints,
                status=MissionStatus(mission_data['status']),
                parameters=mission_data['parameters'],
                timestamp=datetime.fromisoformat(mission_data['timestamp'])
            )
            
            # Mission validieren
            if not self._validate_mission(mission.name, mission.waypoints):
                return None
                
            # Mission hinzufügen
            self._missions.append(mission)
            return mission
            
        except Exception as e:
            print(f"Fehler beim Importieren der Mission: {e}")
            return None
            
    def _validate_waypoint(self, waypoint: Waypoint) -> bool:
        """
        Validiert einen Wegpunkt.
        
        Args:
            waypoint: Wegpunkt
            
        Returns:
            True wenn gültig, sonst False
        """
        # Koordinaten validieren
        if not (-90 <= waypoint.latitude <= 90):
            return False
            
        if not (-180 <= waypoint.longitude <= 180):
            return False
            
        if not (0 <= waypoint.altitude <= 1000):
            return False
            
        return True
        
    def _validate_mission(self, name: str, waypoints: List[Waypoint]) -> bool:
        """
        Validiert eine Mission.
        
        Args:
            name: Name der Mission
            waypoints: Liste der Wegpunkte
            
        Returns:
            True wenn gültig, sonst False
        """
        # Name validieren
        if not name:
            return False
            
        # Wegpunkte validieren
        if not waypoints:
            return False
            
        for waypoint in waypoints:
            if not self._validate_waypoint(waypoint):
                return False
                
        return True
        
    def _validate_mission_start(self, mission: Mission) -> bool:
        """
        Validiert den Start einer Mission.
        
        Args:
            mission: Mission
            
        Returns:
            True wenn gültig, sonst False
        """
        # Status prüfen
        if mission.status != MissionStatus.NOT_STARTED:
            return False
            
        # Wegpunkte prüfen
        if not mission.waypoints:
            return False
            
        return True
        
    def _find_waypoint(self, waypoint_id: int) -> Optional[Waypoint]:
        """
        Findet einen Wegpunkt.
        
        Args:
            waypoint_id: ID des Wegpunkts
            
        Returns:
            Wegpunkt oder None
        """
        for waypoint in self._waypoints:
            if waypoint.id == waypoint_id:
                return waypoint
                
        return None
        
    def _find_waypoint_index(self, waypoint_id: int) -> int:
        """
        Findet den Index eines Wegpunkts.
        
        Args:
            waypoint_id: ID des Wegpunkts
            
        Returns:
            Index oder -1
        """
        for i, waypoint in enumerate(self._waypoints):
            if waypoint.id == waypoint_id:
                return i
                
        return -1
        
    def _find_mission(self, mission_id: int) -> Optional[Mission]:
        """
        Findet eine Mission.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            Mission oder None
        """
        for mission in self._missions:
            if mission.id == mission_id:
                return mission
                
        return None 