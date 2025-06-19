"""
Mission Planner-Adapter für die Flugsteuerung.
Konvertiert zwischen Mission Planner- und internem Format.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import math

from .enums import WaypointType, FlightMode, MissionStatus
from .waypoint_manager import Waypoint, Mission
from .mission_planner import MissionPlan

@dataclass
class MissionPlannerWaypoint:
    """Wegpunkt im Mission Planner-Format"""
    index: int
    current: int
    coord_frame: int
    command: int
    param1: float
    param2: float
    param3: float
    param4: float
    param5: float
    param6: float
    param7: float
    autocontinue: int
    mission_type: int

class MissionPlannerAdapter:
    """Konvertiert zwischen Mission Planner- und internem Format"""
    
    # MAVLink-Befehle
    MAV_CMD_NAV_WAYPOINT = 16
    MAV_CMD_NAV_LOITER_UNLIM = 17
    MAV_CMD_NAV_LOITER_TURNS = 18
    MAV_CMD_NAV_LOITER_TIME = 19
    MAV_CMD_NAV_RETURN_TO_LAUNCH = 20
    MAV_CMD_NAV_LAND = 21
    MAV_CMD_NAV_TAKEOFF = 22
    MAV_CMD_NAV_FOLLOW = 33
    MAV_CMD_NAV_CONTINUE_AND_CHANGE_ALT = 30
    MAV_CMD_NAV_ORBIT = 34
    MAV_CMD_NAV_SPLINE_WAYPOINT = 82
    MAV_CMD_DO_CHANGE_SPEED = 178
    MAV_CMD_DO_SET_HOME = 179
    MAV_CMD_DO_SET_ROI = 201
    MAV_CMD_DO_SET_RELAY = 181
    MAV_CMD_DO_REPEAT_RELAY = 182
    MAV_CMD_DO_SET_SERVO = 183
    MAV_CMD_DO_REPEAT_SERVO = 184
    MAV_CMD_DO_FLIGHTTERMINATION = 185
    MAV_CMD_DO_CHANGE_ALTITUDE = 186
    MAV_CMD_DO_SET_ACTUATOR = 187
    MAV_CMD_DO_LAND_START = 189
    MAV_CMD_DO_GO_AROUND = 191
    MAV_CMD_DO_CONTROL_VIDEO = 200
    MAV_CMD_DO_SET_ROI_LOCATION = 195
    MAV_CMD_DO_SET_ROI_WPNEXT_OFFSET = 196
    MAV_CMD_DO_SET_ROI_NONE = 197
    MAV_CMD_DO_SET_ROI_SYSID = 198
    MAV_CMD_DO_SET_ROI_WPNEXT_OFFSET = 196
    MAV_CMD_DO_SET_ROI_NONE = 197
    MAV_CMD_DO_SET_ROI_SYSID = 198
    MAV_CMD_DO_SET_ROI_WPNEXT_OFFSET = 196
    MAV_CMD_DO_SET_ROI_NONE = 197
    MAV_CMD_DO_SET_ROI_SYSID = 198
    
    def __init__(self):
        """Initialisiert den Mission Planner-Adapter"""
        # Befehl-Mapping
        self._command_to_type = {
            self.MAV_CMD_NAV_WAYPOINT: WaypointType.NORMAL,
            self.MAV_CMD_NAV_LOITER_UNLIM: WaypointType.LOITER,
            self.MAV_CMD_NAV_LOITER_TURNS: WaypointType.LOITER,
            self.MAV_CMD_NAV_LOITER_TIME: WaypointType.LOITER,
            self.MAV_CMD_NAV_RETURN_TO_LAUNCH: WaypointType.RTL,
            self.MAV_CMD_NAV_LAND: WaypointType.LAND,
            self.MAV_CMD_NAV_TAKEOFF: WaypointType.TAKEOFF,
            self.MAV_CMD_NAV_FOLLOW: WaypointType.NORMAL,
            self.MAV_CMD_NAV_CONTINUE_AND_CHANGE_ALT: WaypointType.NORMAL,
            self.MAV_CMD_NAV_ORBIT: WaypointType.NORMAL,
            self.MAV_CMD_NAV_SPLINE_WAYPOINT: WaypointType.NORMAL
        }
        
        self._type_to_command = {
            WaypointType.NORMAL: self.MAV_CMD_NAV_WAYPOINT,
            WaypointType.LOITER: self.MAV_CMD_NAV_LOITER_UNLIM,
            WaypointType.RTL: self.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            WaypointType.LAND: self.MAV_CMD_NAV_LAND,
            WaypointType.TAKEOFF: self.MAV_CMD_NAV_TAKEOFF,
            WaypointType.EMERGENCY: self.MAV_CMD_NAV_RETURN_TO_LAUNCH
        }
        
    def import_mission(self, file_path: str) -> Optional[Mission]:
        """
        Importiert eine Mission aus einer Mission Planner-Datei.
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Mission oder None
        """
        try:
            # JSON aus Datei lesen
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Wegpunkte konvertieren
            waypoints = []
            for wp_data in data.get('waypoints', []):
                waypoint = self._convert_to_waypoint(wp_data)
                if waypoint:
                    waypoints.append(waypoint)
                    
            # Mission erstellen
            mission = Mission(
                id=0,
                name=data.get('name', 'Imported Mission'),
                waypoints=waypoints,
                status=MissionStatus.NOT_STARTED,
                parameters=data.get('parameters', {})
            )
            
            return mission
            
        except Exception as e:
            print(f"Fehler beim Importieren der Mission: {e}")
            return None
            
    def export_mission(self, mission: Mission, file_path: str) -> bool:
        """
        Exportiert eine Mission in eine Mission Planner-Datei.
        
        Args:
            mission: Mission
            file_path: Pfad zur Datei
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Wegpunkte konvertieren
            waypoints = []
            for waypoint in mission.waypoints:
                wp_data = self._convert_from_waypoint(waypoint)
                if wp_data:
                    waypoints.append(wp_data)
                    
            # Daten erstellen
            data = {
                'name': mission.name,
                'waypoints': waypoints,
                'parameters': mission.parameters
            }
            
            # JSON in Datei schreiben
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            return True
            
        except Exception as e:
            print(f"Fehler beim Exportieren der Mission: {e}")
            return False
            
    def _convert_to_waypoint(self, wp_data: Dict[str, Any]) -> Optional[Waypoint]:
        """
        Konvertiert einen Wegpunkt aus dem Mission Planner-Format.
        
        Args:
            wp_data: Wegpunkt-Daten
            
        Returns:
            Wegpunkt oder None
        """
        try:
            # Typ bestimmen
            wp_type = self._get_waypoint_type(wp_data['command'])
            
            # Parameter extrahieren
            params = {
                'param1': wp_data['param1'],
                'param2': wp_data['param2'],
                'param3': wp_data['param3'],
                'param4': wp_data['param4'],
                'param5': wp_data['param5'],
                'param6': wp_data['param6'],
                'param7': wp_data['param7']
            }
            
            # Wegpunkt erstellen
            return Waypoint(
                id=wp_data['index'],
                type=wp_type,
                latitude=wp_data['param5'],
                longitude=wp_data['param6'],
                altitude=wp_data['param7'],
                parameters=params
            )
            
        except Exception as e:
            print(f"Fehler beim Konvertieren des Wegpunkts: {e}")
            return None
            
    def _convert_from_waypoint(self, waypoint: Waypoint) -> Optional[Dict[str, Any]]:
        """
        Konvertiert einen Wegpunkt in das Mission Planner-Format.
        
        Args:
            waypoint: Wegpunkt
            
        Returns:
            Wegpunkt-Daten oder None
        """
        try:
            # Befehl bestimmen
            command = self._get_mission_planner_command(waypoint.type)
            
            # Wegpunkt-Daten erstellen
            return {
                'index': waypoint.id,
                'current': 0,
                'coord_frame': 3,  # MAV_FRAME_GLOBAL_RELATIVE_ALT
                'command': command,
                'param1': waypoint.parameters.get('param1', 0.0),
                'param2': waypoint.parameters.get('param2', 0.0),
                'param3': waypoint.parameters.get('param3', 0.0),
                'param4': waypoint.parameters.get('param4', 0.0),
                'param5': waypoint.latitude,
                'param6': waypoint.longitude,
                'param7': waypoint.altitude,
                'autocontinue': 1,
                'mission_type': 0
            }
            
        except Exception as e:
            print(f"Fehler beim Konvertieren des Wegpunkts: {e}")
            return None
            
    def _get_waypoint_type(self, command: int) -> WaypointType:
        """
        Bestimmt den Wegpunkttyp aus dem Befehl.
        
        Args:
            command: Befehl
            
        Returns:
            Wegpunkttyp
        """
        return self._command_to_type.get(command, WaypointType.NORMAL)
        
    def _get_mission_planner_command(self, wp_type: WaypointType) -> int:
        """
        Bestimmt den Befehl aus dem Wegpunkttyp.
        
        Args:
            wp_type: Wegpunkttyp
            
        Returns:
            Befehl
        """
        return self._type_to_command.get(wp_type, self.MAV_CMD_NAV_WAYPOINT) 