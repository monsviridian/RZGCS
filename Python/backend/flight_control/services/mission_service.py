"""
Mission-Service für die Flugsteuerung.
Implementiert die Geschäftslogik für Missionsverwaltung.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import math

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ..models.flight_data import Waypoint, Mission, MissionPlan, Position, FlightState, ControlCommand
from ..enums import MissionStatus, WaypointType, FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from .flight_service import FlightService
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

class MissionService(QObject):
    """Implementiert die Geschäftslogik für Missionsverwaltung"""
    
    # Signale
    mission_created = Signal(Mission)
    mission_updated = Signal(Mission)
    mission_deleted = Signal(str)  # Mission ID
    mission_plan_created = Signal(MissionPlan)
    mission_plan_updated = Signal(MissionPlan)
    mission_plan_deleted = Signal(str)  # Plan ID
    error_occurred = Signal(str)
    state_changed = Signal(FlightState)
    mode_changed = Signal(FlightMode)
    command_executed = Signal(ControlCommand)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    waypoint_reached = Signal(Waypoint)  # Neues Signal für erreichte Wegpunkte
    mission_paused = Signal(Mission)  # Neues Signal für pausierte Missionen
    mission_resumed = Signal(Mission)  # Neues Signal für fortgesetzte Missionen
    
    def __init__(self, flight_service: Optional[FlightService] = None,
                 telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den Mission-Service.
        
        Args:
            flight_service: Optional: Flug-Service
            telemetry_manager: Optional: Telemetrie-Manager
            connection_manager: Optional: Verbindungs-Manager
        """
        super().__init__()
        
        # Service setzen
        self._flight_service = flight_service
        
        # Manager setzen
        self._telemetry = telemetry_manager
        self._connection = connection_manager
        
        # Missionen und Pläne
        self._missions: Dict[str, Mission] = {}
        self._mission_plans: Dict[str, MissionPlan] = {}
        
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
        
        # Missions-Parameter
        self._current_mission: Optional[Mission] = None
        self._mission_active = False
        self._mission_paused = False
        self._current_waypoint_index = -1
        self._waypoint_reached_distance = 1.0  # Distanz in Metern
        self._waypoint_reached_time = 2.0  # Zeit in Sekunden
        
        # Timer für Statusaktualisierungen
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(100)  # 100ms
        
    def set_flight_service(self, flight_service: FlightService) -> None:
        """
        Setzt den Flug-Service.
        
        Args:
            flight_service: Flug-Service
        """
        self._flight_service = flight_service
        
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
        
    def create_mission(self, name: str, waypoints: List[Waypoint]) -> Optional[Mission]:
        """
        Erstellt eine neue Mission.
        
        Args:
            name: Missionsname
            waypoints: Liste der Wegpunkte
            
        Returns:
            Erstellte Mission oder None bei Fehler
        """
        # Mission erstellen
        mission = Mission(
            id=str(len(self._missions) + 1),
            name=name,
            waypoints=waypoints,
            status=MissionStatus.CREATED,
            parameters={}
        )
        
        # Mission speichern
        self._missions[mission.id] = mission
        self.mission_created.emit(mission)
        
        return mission
        
    def update_mission(self, mission: Mission) -> bool:
        """
        Aktualisiert eine Mission.
        
        Args:
            mission: Zu aktualisierende Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if mission.id not in self._missions:
            self._set_error(f"Mission {mission.id} nicht gefunden")
            return False
            
        # Mission aktualisieren
        self._missions[mission.id] = mission
        self.mission_updated.emit(mission)
        
        return True
        
    def delete_mission(self, mission_id: str) -> bool:
        """
        Löscht eine Mission.
        
        Args:
            mission_id: ID der zu löschenden Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if mission_id not in self._missions:
            self._set_error(f"Mission {mission_id} nicht gefunden")
            return False
            
        # Mission löschen
        del self._missions[mission_id]
        self.mission_deleted.emit(mission_id)
        
        return True
        
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """
        Gibt eine Mission zurück.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            Mission oder None wenn nicht gefunden
        """
        return self._missions.get(mission_id)
        
    def get_all_missions(self) -> List[Mission]:
        """
        Gibt alle Missionen zurück.
        
        Returns:
            Liste aller Missionen
        """
        return list(self._missions.values())
        
    def create_mission_plan(self, mission: Mission) -> Optional[MissionPlan]:
        """
        Erstellt einen neuen Missionsplan.
        
        Args:
            mission: Mission
            
        Returns:
            Erstellter Plan oder None bei Fehler
        """
        # Plan erstellen
        plan = MissionPlan(
            mission=mission,
            estimated_duration=0.0,
            estimated_distance=0.0,
            estimated_energy=0.0,
            waypoint_sequence=mission.waypoints,
            parameters={},
            timestamp=datetime.now()
        )
        
        # Plan optimieren
        if not self._optimize_plan(plan):
            self._set_error("Planoptimierung fehlgeschlagen")
            return None
            
        # Plan speichern
        self._mission_plans[plan.mission.id] = plan
        self.mission_plan_created.emit(plan)
        
        return plan
        
    def update_mission_plan(self, plan: MissionPlan) -> bool:
        """
        Aktualisiert einen Missionsplan.
        
        Args:
            plan: Zu aktualisierender Plan
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if plan.mission.id not in self._mission_plans:
            self._set_error(f"Plan für Mission {plan.mission.id} nicht gefunden")
            return False
            
        # Plan optimieren
        if not self._optimize_plan(plan):
            self._set_error("Planoptimierung fehlgeschlagen")
            return False
            
        # Plan aktualisieren
        self._mission_plans[plan.mission.id] = plan
        self.mission_plan_updated.emit(plan)
        
        return True
        
    def delete_mission_plan(self, mission_id: str) -> bool:
        """
        Löscht einen Missionsplan.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if mission_id not in self._mission_plans:
            self._set_error(f"Plan für Mission {mission_id} nicht gefunden")
            return False
            
        # Plan löschen
        del self._mission_plans[mission_id]
        self.mission_plan_deleted.emit(mission_id)
        
        return True
        
    def get_mission_plan(self, mission_id: str) -> Optional[MissionPlan]:
        """
        Gibt einen Missionsplan zurück.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            Plan oder None wenn nicht gefunden
        """
        return self._mission_plans.get(mission_id)
        
    def get_all_mission_plans(self) -> List[MissionPlan]:
        """
        Gibt alle Missionspläne zurück.
        
        Returns:
            Liste aller Pläne
        """
        return list(self._mission_plans.values())
        
    def export_mission(self, mission: Mission, file_path: str) -> bool:
        """
        Exportiert eine Mission.
        
        Args:
            mission: Zu exportierende Mission
            file_path: Dateipfad
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Mission in JSON konvertieren
            data = {
                "id": mission.id,
                "name": mission.name,
                "waypoints": [
                    {
                        "id": wp.id,
                        "type": wp.type.value,
                        "position": {
                            "latitude": wp.position.latitude,
                            "longitude": wp.position.longitude,
                            "altitude": wp.position.altitude
                        },
                        "parameters": wp.parameters
                    }
                    for wp in mission.waypoints
                ],
                "status": mission.status.value,
                "parameters": mission.parameters
            }
            
            # JSON in Datei schreiben
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
                
            return True
            
        except Exception as e:
            self._set_error(f"Export fehlgeschlagen: {str(e)}")
            return False
            
    def import_mission(self, file_path: str) -> Optional[Mission]:
        """
        Importiert eine Mission.
        
        Args:
            file_path: Dateipfad
            
        Returns:
            Importierte Mission oder None bei Fehler
        """
        try:
            # JSON aus Datei lesen
            with open(file_path, "r") as f:
                data = json.load(f)
                
            # Wegpunkte konvertieren
            waypoints = []
            for wp_data in data["waypoints"]:
                waypoint = Waypoint(
                    id=wp_data["id"],
                    type=WaypointType(wp_data["type"]),
                    position=Position(
                        latitude=wp_data["position"]["latitude"],
                        longitude=wp_data["position"]["longitude"],
                        altitude=wp_data["position"]["altitude"]
                    ),
                    parameters=wp_data["parameters"]
                )
                waypoints.append(waypoint)
                
            # Mission erstellen
            mission = Mission(
                id=data["id"],
                name=data["name"],
                waypoints=waypoints,
                status=MissionStatus(data["status"]),
                parameters=data["parameters"]
            )
            
            # Mission speichern
            self._missions[mission.id] = mission
            self.mission_created.emit(mission)
            
            return mission
            
        except Exception as e:
            self._set_error(f"Import fehlgeschlagen: {str(e)}")
            return None
            
    def _optimize_plan(self, plan: MissionPlan) -> bool:
        """
        Optimiert einen Missionsplan.
        
        Args:
            plan: Zu optimierender Plan
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # TODO: Implementierung der Planoptimierung
            
            # Beispiel: Distanz berechnen
            total_distance = 0.0
            for i in range(len(plan.waypoint_sequence) - 1):
                wp1 = plan.waypoint_sequence[i]
                wp2 = plan.waypoint_sequence[i + 1]
                total_distance += wp1.position.distance_to(wp2.position)
                
            plan.estimated_distance = total_distance
            
            # Beispiel: Dauer schätzen
            # Annahme: 10 m/s Geschwindigkeit
            plan.estimated_duration = total_distance / 10.0
            
            # Beispiel: Energie schätzen
            # Annahme: 100 W Leistung
            plan.estimated_energy = plan.estimated_duration * 100.0
            
            return True
            
        except Exception as e:
            self._set_error(f"Planoptimierung fehlgeschlagen: {str(e)}")
            return False
            
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
        
    def set_mission_parameters(self, waypoint_reached_distance: float,
                             waypoint_reached_time: float) -> None:
        """
        Setzt die Missions-Parameter.
        
        Args:
            waypoint_reached_distance: Distanz in Metern
            waypoint_reached_time: Zeit in Sekunden
        """
        self._waypoint_reached_distance = waypoint_reached_distance
        self._waypoint_reached_time = waypoint_reached_time
        
    def add_mission_plan(self, plan: MissionPlan) -> None:
        """
        Fügt einen Missionsplan hinzu.
        
        Args:
            plan: Missionsplan
        """
        self._mission_plans[plan.id] = plan
        
    def remove_mission_plan(self, plan_id: str) -> None:
        """
        Entfernt einen Missionsplan.
        
        Args:
            plan_id: ID des Missionsplans
        """
        if plan_id in self._mission_plans:
            del self._mission_plans[plan_id]
            
    def get_mission_plans(self) -> List[MissionPlan]:
        """
        Gibt die verfügbaren Missionspläne zurück.
        
        Returns:
            Liste der Missionspläne
        """
        return list(self._mission_plans.values())
        
    @Slot(Mission)
    def start_mission(self, mission: Mission) -> bool:
        """
        Startet eine Mission.
        
        Args:
            mission: Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._mission_active:
            self._set_error("Mission bereits aktiv")
            return False
            
        if not mission.waypoints:
            self._set_error("Mission hat keine Wegpunkte")
            return False
            
        # Mission starten
        self._current_mission = mission
        self._mission_active = True
        self._mission_paused = False
        self._current_waypoint_index = 0
        
        # Status aktualisieren
        self._set_state(FlightStatus.FLYING)
        self.mission_started.emit(mission)
        
        # Ersten Wegpunkt ansteuern
        return self._navigate_to_waypoint(mission.waypoints[0])
        
    @Slot()
    def pause_mission(self) -> bool:
        """
        Pausiert die aktuelle Mission.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._mission_active:
            self._set_error("Keine aktive Mission")
            return False
            
        if self._mission_paused:
            self._set_error("Mission bereits pausiert")
            return False
            
        # Mission pausieren
        self._mission_paused = True
        
        # Hover-Befehl senden
        command = ControlCommand(
            type=CommandType.HOVER,
            parameters={
                "altitude": self._state.position.z
            }
        )
        
        success = self.execute_command(command)
        
        if success:
            self.mission_paused.emit(self._current_mission)
            
        return success
        
    @Slot()
    def resume_mission(self) -> bool:
        """
        Setzt die aktuelle Mission fort.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._mission_active:
            self._set_error("Keine aktive Mission")
            return False
            
        if not self._mission_paused:
            self._set_error("Mission nicht pausiert")
            return False
            
        # Mission fortsetzen
        self._mission_paused = False
        
        # Aktuellen Wegpunkt ansteuern
        if self._current_mission and 0 <= self._current_waypoint_index < len(self._current_mission.waypoints):
            success = self._navigate_to_waypoint(self._current_mission.waypoints[self._current_waypoint_index])
            
            if success:
                self.mission_resumed.emit(self._current_mission)
                
            return success
            
        return False
        
    @Slot()
    def abort_mission(self) -> bool:
        """
        Bricht die aktuelle Mission ab.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._mission_active:
            self._set_error("Keine aktive Mission")
            return False
            
        # Mission abbrechen
        self._mission_active = False
        self._mission_paused = False
        mission = self._current_mission
        self._current_mission = None
        self._current_waypoint_index = -1
        
        # Status aktualisieren
        self._set_state(FlightStatus.ARMED)
        self.mission_aborted.emit(mission)
        
        return True
        
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
            return
            
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
        
        # Mission prüfen
        if self._mission_active and not self._mission_paused:
            self._check_mission()
            
    def _check_mission(self) -> None:
        """
        Prüft den Status der aktuellen Mission.
        """
        if not self._current_mission:
            return
            
        # Aktuellen Wegpunkt prüfen
        if 0 <= self._current_waypoint_index < len(self._current_mission.waypoints):
            waypoint = self._current_mission.waypoints[self._current_waypoint_index]
            
            # Distanz zum Wegpunkt
            dx = self._state.position.x - waypoint.position.x
            dy = self._state.position.y - waypoint.position.y
            dz = self._state.position.z - waypoint.position.z
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Wenn Wegpunkt erreicht
            if distance < self._waypoint_reached_distance:
                self._handle_waypoint_reached(waypoint)
                
    def _handle_waypoint_reached(self, waypoint: Waypoint) -> None:
        """
        Behandelt einen erreichten Wegpunkt.
        
        Args:
            waypoint: Erreichter Wegpunkt
        """
        # Wegpunkt signalisieren
        self.waypoint_reached.emit(waypoint)
        
        # Nächsten Wegpunkt ansteuern
        self._current_waypoint_index += 1
        
        if self._current_mission and self._current_waypoint_index < len(self._current_mission.waypoints):
            self._navigate_to_waypoint(self._current_mission.waypoints[self._current_waypoint_index])
        else:
            self._handle_mission_completed()
            
    def _handle_mission_completed(self) -> None:
        """
        Behandelt eine abgeschlossene Mission.
        """
        # Mission beenden
        self._mission_active = False
        mission = self._current_mission
        self._current_mission = None
        self._current_waypoint_index = -1
        
        # Status aktualisieren
        self._set_state(FlightStatus.ARMED)
        self.mission_completed.emit(mission)
        
    def _navigate_to_waypoint(self, waypoint: Waypoint) -> bool:
        """
        Steuert einen Wegpunkt an.
        
        Args:
            waypoint: Ziel-Wegpunkt
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Navigations-Befehl erstellen
        command = ControlCommand(
            type=CommandType.MOVE_TO,
            parameters={
                "x": waypoint.position.x,
                "y": waypoint.position.y,
                "z": waypoint.position.z
            }
        )
        
        # Befehl ausführen
        return self.execute_command(command)
        
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