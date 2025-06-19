"""
MAVLink-Handler für die Flugsteuerung.
Verarbeitet MAVLink-Nachrichten für QGroundControl-Kompatibilität.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

from pymavlink import mavutil
from pymavlink.dialects.v20 import common as mavlink2

from .enums import FlightStatus, FlightMode, CommandType
from .flight_controller import FlightController
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

@dataclass
class MAVLinkMessage:
    """MAVLink-Nachricht"""
    msg_type: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.now()

class MAVLinkHandler:
    """Verarbeitet MAVLink-Nachrichten"""
    
    def __init__(self, flight_controller: FlightController,
                 telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den MAVLink-Handler.
        
        Args:
            flight_controller: Flugcontroller
            telemetry_manager: Optional: Telemetrie-Manager
            connection_manager: Optional: Verbindungs-Manager
        """
        self._flight_controller = flight_controller
        self._telemetry = telemetry_manager
        self._connection = connection_manager
        
        # MAVLink-System-ID und Komponenten-ID
        self._system_id = 1
        self._component_id = 1
        
        # MAVLink-Parameter
        self._parameters: Dict[str, float] = {}
        
        # MAVLink-Status
        self._armed = False
        self._mode = FlightMode.MANUAL
        self._status = FlightStatus.DISCONNECTED
        
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
        
    def process_message(self, message: MAVLinkMessage) -> Optional[MAVLinkMessage]:
        """
        Verarbeitet eine MAVLink-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht oder None
        """
        # Nachrichtentyp prüfen
        if message.msg_type == 'HEARTBEAT':
            return self._handle_heartbeat(message)
        elif message.msg_type == 'COMMAND_LONG':
            return self._handle_command(message)
        elif message.msg_type == 'PARAM_SET':
            return self._handle_param_set(message)
        elif message.msg_type == 'PARAM_REQUEST_READ':
            return self._handle_param_request(message)
        elif message.msg_type == 'MISSION_REQUEST':
            return self._handle_mission_request(message)
        elif message.msg_type == 'MISSION_SET_CURRENT':
            return self._handle_mission_set_current(message)
        elif message.msg_type == 'MISSION_CLEAR_ALL':
            return self._handle_mission_clear_all(message)
        elif message.msg_type == 'MISSION_COUNT':
            return self._handle_mission_count(message)
        elif message.msg_type == 'MISSION_ITEM':
            return self._handle_mission_item(message)
            
        return None
        
    def _handle_heartbeat(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine HEARTBEAT-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        # Status aktualisieren
        self._armed = message.data.get('base_mode', 0) & mavlink2.MAV_MODE_FLAG_SAFETY_ARMED != 0
        self._mode = self._convert_mavlink_mode(message.data.get('custom_mode', 0))
        
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='HEARTBEAT',
            data={
                'type': mavlink2.MAV_TYPE_FIXED_WING,
                'autopilot': mavlink2.MAV_AUTOPILOT_ARDUPILOTMEGA,
                'base_mode': message.data.get('base_mode', 0),
                'custom_mode': message.data.get('custom_mode', 0),
                'system_status': self._convert_flight_status(self._flight_controller._status)
            }
        )
        
    def _handle_command(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine COMMAND_LONG-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        command = message.data.get('command', 0)
        params = message.data.get('param', [0.0] * 7)
        
        # Befehl ausführen
        success = False
        if command == mavlink2.MAV_CMD_COMPONENT_ARM_DISARM:
            if params[0] > 0:
                success = self._flight_controller.arm()
            else:
                success = self._flight_controller.disarm()
        elif command == mavlink2.MAV_CMD_DO_SET_MODE:
            mode = self._convert_mavlink_mode(int(params[0]))
            success = self._flight_controller.set_mode(mode)
        elif command == mavlink2.MAV_CMD_MISSION_START:
            success = self._flight_controller.start_mission(self._flight_controller._waypoint_manager.get_current_mission())
        elif command == mavlink2.MAV_CMD_DO_SET_ROI:
            # TODO: ROI setzen
            pass
            
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='COMMAND_ACK',
            data={
                'command': command,
                'result': mavlink2.MAV_RESULT_ACCEPTED if success else mavlink2.MAV_RESULT_FAILED
            }
        )
        
    def _handle_param_set(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine PARAM_SET-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        param_id = message.data.get('param_id', '')
        param_value = message.data.get('param_value', 0.0)
        
        # Parameter setzen
        self._parameters[param_id] = param_value
        
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='PARAM_VALUE',
            data={
                'param_id': param_id,
                'param_value': param_value,
                'param_type': mavlink2.MAV_PARAM_TYPE_REAL32
            }
        )
        
    def _handle_param_request(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine PARAM_REQUEST_READ-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        param_id = message.data.get('param_id', '')
        
        # Parameter abrufen
        param_value = self._parameters.get(param_id, 0.0)
        
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='PARAM_VALUE',
            data={
                'param_id': param_id,
                'param_value': param_value,
                'param_type': mavlink2.MAV_PARAM_TYPE_REAL32
            }
        )
        
    def _handle_mission_request(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine MISSION_REQUEST-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        seq = message.data.get('seq', 0)
        mission = self._flight_controller._waypoint_manager.get_current_mission()
        
        if not mission or seq >= len(mission.waypoints):
            return MAVLinkMessage(
                msg_type='MISSION_ACK',
                data={
                    'type': mavlink2.MAV_MISSION_ERROR
                }
            )
            
        # Wegpunkt konvertieren
        waypoint = mission.waypoints[seq]
        mission_item = self._convert_waypoint_to_mission_item(waypoint, seq)
        
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='MISSION_ITEM',
            data=mission_item
        )
        
    def _handle_mission_set_current(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine MISSION_SET_CURRENT-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        seq = message.data.get('seq', 0)
        mission = self._flight_controller._waypoint_manager.get_current_mission()
        
        if not mission or seq >= len(mission.waypoints):
            return MAVLinkMessage(
                msg_type='MISSION_ACK',
                data={
                    'type': mavlink2.MAV_MISSION_ERROR
                }
            )
            
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='MISSION_CURRENT',
            data={
                'seq': seq
            }
        )
        
    def _handle_mission_clear_all(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine MISSION_CLEAR_ALL-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        # Mission löschen
        self._flight_controller._waypoint_manager.clear_data()
        
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='MISSION_ACK',
            data={
                'type': mavlink2.MAV_MISSION_ACCEPTED
            }
        )
        
    def _handle_mission_count(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine MISSION_COUNT-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        mission = self._flight_controller._waypoint_manager.get_current_mission()
        count = len(mission.waypoints) if mission else 0
        
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='MISSION_COUNT',
            data={
                'count': count
            }
        )
        
    def _handle_mission_item(self, message: MAVLinkMessage) -> MAVLinkMessage:
        """
        Verarbeitet eine MISSION_ITEM-Nachricht.
        
        Args:
            message: MAVLink-Nachricht
            
        Returns:
            Antwort-Nachricht
        """
        # Wegpunkt konvertieren
        waypoint = self._convert_mission_item_to_waypoint(message.data)
        
        # Wegpunkt hinzufügen
        if not self._flight_controller._waypoint_manager.add_waypoint(waypoint):
            return MAVLinkMessage(
                msg_type='MISSION_ACK',
                data={
                    'type': mavlink2.MAV_MISSION_ERROR
                }
            )
            
        # Antwort erstellen
        return MAVLinkMessage(
            msg_type='MISSION_ACK',
            data={
                'type': mavlink2.MAV_MISSION_ACCEPTED
            }
        )
        
    def _convert_mavlink_mode(self, custom_mode: int) -> FlightMode:
        """
        Konvertiert einen MAVLink-Modus in einen Flugmodus.
        
        Args:
            custom_mode: MAVLink-Modus
            
        Returns:
            Flugmodus
        """
        # TODO: Implementierung der Modus-Konvertierung
        return FlightMode.MANUAL
        
    def _convert_flight_status(self, status: FlightStatus) -> int:
        """
        Konvertiert einen Flugstatus in einen MAVLink-Status.
        
        Args:
            status: Flugstatus
            
        Returns:
            MAVLink-Status
        """
        # TODO: Implementierung der Status-Konvertierung
        return mavlink2.MAV_STATE_ACTIVE
        
    def _convert_waypoint_to_mission_item(self, waypoint: Waypoint, seq: int) -> Dict[str, Any]:
        """
        Konvertiert einen Wegpunkt in ein Mission-Item.
        
        Args:
            waypoint: Wegpunkt
            seq: Sequenznummer
            
        Returns:
            Mission-Item
        """
        # TODO: Implementierung der Wegpunkt-Konvertierung
        return {
            'seq': seq,
            'frame': mavlink2.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            'command': mavlink2.MAV_CMD_NAV_WAYPOINT,
            'current': 0,
            'autocontinue': 1,
            'param1': 0.0,
            'param2': 0.0,
            'param3': 0.0,
            'param4': 0.0,
            'x': waypoint.longitude,
            'y': waypoint.latitude,
            'z': waypoint.altitude
        }
        
    def _convert_mission_item_to_waypoint(self, mission_item: Dict[str, Any]) -> Waypoint:
        """
        Konvertiert ein Mission-Item in einen Wegpunkt.
        
        Args:
            mission_item: Mission-Item
            
        Returns:
            Wegpunkt
        """
        # TODO: Implementierung der Wegpunkt-Konvertierung
        return Waypoint(
            id=mission_item['seq'],
            type=WaypointType.NORMAL,
            latitude=mission_item['y'],
            longitude=mission_item['x'],
            altitude=mission_item['z'],
            parameters={}
        ) 