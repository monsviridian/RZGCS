"""
Missionsplaner für die Flugsteuerung.
Plant und optimiert Flugmissionen.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math
import json

from .enums import WaypointType, MissionStatus, ValidationResult
from .waypoint_manager import WaypointManager, Waypoint, Mission
from ..telemetry.telemetry_manager import TelemetryManager

@dataclass
class MissionPlan:
    """Plan für eine Flugmission"""
    mission: Mission
    estimated_duration: float  # in Sekunden
    estimated_distance: float  # in Metern
    estimated_energy: float    # in Prozent
    waypoint_sequence: List[int]
    parameters: Dict[str, Any]
    timestamp: datetime = datetime.now()

class MissionPlanner:
    """Plant und optimiert Flugmissionen"""
    
    def __init__(self, waypoint_manager: WaypointManager, telemetry_manager: Optional[TelemetryManager] = None):
        """
        Initialisiert den Missionsplaner.
        
        Args:
            waypoint_manager: Wegpunkt-Manager
            telemetry_manager: Optional: Telemetrie-Manager für Datenabfrage
        """
        self._waypoint_manager = waypoint_manager
        self._telemetry = telemetry_manager
        self._mission_plans: List[MissionPlan] = []
        self._current_plan: Optional[MissionPlan] = None
        
    def set_telemetry_manager(self, telemetry_manager: TelemetryManager) -> None:
        """
        Setzt den Telemetrie-Manager.
        
        Args:
            telemetry_manager: Telemetrie-Manager
        """
        self._telemetry = telemetry_manager
        
    def create_mission_plan(self, mission: Mission, parameters: Optional[Dict[str, Any]] = None) -> Optional[MissionPlan]:
        """
        Erstellt einen Missionsplan.
        
        Args:
            mission: Mission
            parameters: Optional: Planparameter
            
        Returns:
            Missionsplan oder None
        """
        # Mission validieren
        if not self._validate_mission(mission):
            return None
            
        # Wegpunktsequenz optimieren
        waypoint_sequence = self._optimize_waypoint_sequence(mission.waypoints)
        
        # Schätzungen berechnen
        estimated_duration = self._estimate_duration(mission.waypoints, waypoint_sequence)
        estimated_distance = self._calculate_distance(mission.waypoints, waypoint_sequence)
        estimated_energy = self._estimate_energy_consumption(mission.waypoints, waypoint_sequence)
        
        # Plan erstellen
        plan = MissionPlan(
            mission=mission,
            estimated_duration=estimated_duration,
            estimated_distance=estimated_distance,
            estimated_energy=estimated_energy,
            waypoint_sequence=waypoint_sequence,
            parameters=parameters or {}
        )
        
        # Plan speichern
        self._mission_plans.append(plan)
        return plan
        
    def optimize_mission_plan(self, plan: MissionPlan) -> Optional[MissionPlan]:
        """
        Optimiert einen Missionsplan.
        
        Args:
            plan: Missionsplan
            
        Returns:
            Optimierter Plan oder None
        """
        # Plan validieren
        if not self._validate_plan(plan):
            return None
            
        # Wegpunktsequenz optimieren
        waypoint_sequence = self._optimize_waypoint_sequence(plan.mission.waypoints)
        
        # Schätzungen aktualisieren
        estimated_duration = self._estimate_duration(plan.mission.waypoints, waypoint_sequence)
        estimated_distance = self._calculate_distance(plan.mission.waypoints, waypoint_sequence)
        estimated_energy = self._estimate_energy_consumption(plan.mission.waypoints, waypoint_sequence)
        
        # Plan aktualisieren
        plan.waypoint_sequence = waypoint_sequence
        plan.estimated_duration = estimated_duration
        plan.estimated_distance = estimated_distance
        plan.estimated_energy = estimated_energy
        
        return plan
        
    def get_mission_plan(self, mission_id: int) -> Optional[MissionPlan]:
        """
        Gibt einen Missionsplan zurück.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            Missionsplan oder None
        """
        for plan in self._mission_plans:
            if plan.mission.id == mission_id:
                return plan
                
        return None
        
    def get_all_mission_plans(self) -> List[MissionPlan]:
        """
        Gibt alle Missionspläne zurück.
        
        Returns:
            Liste der Missionspläne
        """
        return self._mission_plans.copy()
        
    def export_mission_plan(self, plan: MissionPlan, file_path: str) -> bool:
        """
        Exportiert einen Missionsplan in eine Datei.
        
        Args:
            plan: Missionsplan
            file_path: Pfad zur Datei
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Plan in JSON konvertieren
            plan_data = {
                'mission_id': plan.mission.id,
                'estimated_duration': plan.estimated_duration,
                'estimated_distance': plan.estimated_distance,
                'estimated_energy': plan.estimated_energy,
                'waypoint_sequence': plan.waypoint_sequence,
                'parameters': plan.parameters,
                'timestamp': plan.timestamp.isoformat()
            }
            
            # JSON in Datei schreiben
            with open(file_path, 'w') as f:
                json.dump(plan_data, f, indent=4)
                
            return True
            
        except Exception as e:
            print(f"Fehler beim Exportieren des Missionsplans: {e}")
            return False
            
    def import_mission_plan(self, file_path: str) -> Optional[MissionPlan]:
        """
        Importiert einen Missionsplan aus einer Datei.
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Missionsplan oder None
        """
        try:
            # JSON aus Datei lesen
            with open(file_path, 'r') as f:
                plan_data = json.load(f)
                
            # Mission finden
            mission = self._waypoint_manager.get_current_mission()
            if not mission or mission.id != plan_data['mission_id']:
                return None
                
            # Plan erstellen
            plan = MissionPlan(
                mission=mission,
                estimated_duration=plan_data['estimated_duration'],
                estimated_distance=plan_data['estimated_distance'],
                estimated_energy=plan_data['estimated_energy'],
                waypoint_sequence=plan_data['waypoint_sequence'],
                parameters=plan_data['parameters'],
                timestamp=datetime.fromisoformat(plan_data['timestamp'])
            )
            
            # Plan validieren
            if not self._validate_plan(plan):
                return None
                
            # Plan speichern
            self._mission_plans.append(plan)
            return plan
            
        except Exception as e:
            print(f"Fehler beim Importieren des Missionsplans: {e}")
            return None
            
    def _validate_mission(self, mission: Mission) -> bool:
        """
        Validiert eine Mission.
        
        Args:
            mission: Mission
            
        Returns:
            True wenn gültig, sonst False
        """
        # Mission prüfen
        if not mission or not mission.waypoints:
            return False
            
        # Wegpunkte prüfen
        for waypoint in mission.waypoints:
            if not self._validate_waypoint(waypoint):
                return False
                
        return True
        
    def _validate_plan(self, plan: MissionPlan) -> bool:
        """
        Validiert einen Missionsplan.
        
        Args:
            plan: Missionsplan
            
        Returns:
            True wenn gültig, sonst False
        """
        # Plan prüfen
        if not plan or not plan.mission:
            return False
            
        # Schätzungen prüfen
        if not (0 <= plan.estimated_duration <= 3600):  # max 1 Stunde
            return False
            
        if not (0 <= plan.estimated_distance <= 100000):  # max 100km
            return False
            
        if not (0 <= plan.estimated_energy <= 100):  # max 100%
            return False
            
        # Wegpunktsequenz prüfen
        if not plan.waypoint_sequence:
            return False
            
        if len(plan.waypoint_sequence) != len(plan.mission.waypoints):
            return False
            
        return True
        
    def _validate_waypoint(self, waypoint: Waypoint) -> bool:
        """
        Validiert einen Wegpunkt.
        
        Args:
            waypoint: Wegpunkt
            
        Returns:
            True wenn gültig, sonst False
        """
        # Koordinaten prüfen
        if not (-90 <= waypoint.latitude <= 90):
            return False
            
        if not (-180 <= waypoint.longitude <= 180):
            return False
            
        if not (0 <= waypoint.altitude <= 1000):
            return False
            
        return True
        
    def _optimize_waypoint_sequence(self, waypoints: List[Waypoint]) -> List[int]:
        """
        Optimiert die Wegpunktsequenz.
        
        Args:
            waypoints: Liste der Wegpunkte
            
        Returns:
            Optimierte Sequenz
        """
        # TODO: Implementierung eines Optimierungsalgorithmus
        # Für jetzt: Einfache sequentielle Reihenfolge
        return list(range(len(waypoints)))
        
    def _estimate_duration(self, waypoints: List[Waypoint], sequence: List[int]) -> float:
        """
        Schätzt die Missionsdauer.
        
        Args:
            waypoints: Liste der Wegpunkte
            sequence: Wegpunktsequenz
            
        Returns:
            Geschätzte Dauer in Sekunden
        """
        # TODO: Implementierung einer genaueren Schätzung
        # Für jetzt: Einfache Schätzung basierend auf Distanz
        distance = self._calculate_distance(waypoints, sequence)
        return distance / 10  # Annahme: 10m/s Durchschnittsgeschwindigkeit
        
    def _calculate_distance(self, waypoints: List[Waypoint], sequence: List[int]) -> float:
        """
        Berechnet die Missionsdistanz.
        
        Args:
            waypoints: Liste der Wegpunkte
            sequence: Wegpunktsequenz
            
        Returns:
            Distanz in Metern
        """
        total_distance = 0.0
        
        # Distanz zwischen aufeinanderfolgenden Wegpunkten berechnen
        for i in range(len(sequence) - 1):
            wp1 = waypoints[sequence[i]]
            wp2 = waypoints[sequence[i + 1]]
            
            # Haversine-Formel für Distanz zwischen zwei Koordinaten
            lat1, lon1 = math.radians(wp1.latitude), math.radians(wp1.longitude)
            lat2, lon2 = math.radians(wp2.latitude), math.radians(wp2.longitude)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            # Erdradius in Metern
            R = 6371000
            
            # Horizontale Distanz
            horizontal_distance = R * c
            
            # Vertikale Distanz
            vertical_distance = abs(wp2.altitude - wp1.altitude)
            
            # Gesamtdistanz (Pythagoras)
            distance = math.sqrt(horizontal_distance**2 + vertical_distance**2)
            
            total_distance += distance
            
        return total_distance
        
    def _estimate_energy_consumption(self, waypoints: List[Waypoint], sequence: List[int]) -> float:
        """
        Schätzt den Energieverbrauch.
        
        Args:
            waypoints: Liste der Wegpunkte
            sequence: Wegpunktsequenz
            
        Returns:
            Geschätzter Energieverbrauch in Prozent
        """
        # TODO: Implementierung einer genaueren Schätzung
        # Für jetzt: Einfache Schätzung basierend auf Distanz und Höhenunterschied
        distance = self._calculate_distance(waypoints, sequence)
        return min(100, distance / 1000)  # Annahme: 1% pro km 