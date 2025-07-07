"""
Flight Navigation ViewModel.
Integrates flight control, mission planning, and telemetry for the flight navigation interface.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import math

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

from ..models.flight_data import Waypoint, Mission, MissionPlan
from ..enums import MissionStatus, WaypointType, FlightMode
from ..services.flight_control_service import FlightControlService
from ..services.mission_service import MissionService
from ...telemetry.telemetry_manager import TelemetryManager

class FlightNavigationViewModel(QObject):
    """Integrated ViewModel for flight navigation interface"""
    
    # Flight control signals
    connection_changed = Signal(bool)
    armed_changed = Signal(bool)
    flight_mode_changed = Signal(str)
    flight_state_changed = Signal()
    
    # Mission signals
    mission_created = Signal(object)  # Mission object
    mission_updated = Signal(object)
    mission_started = Signal(object)
    mission_completed = Signal(object)
    mission_aborted = Signal(object)
    waypoint_reached = Signal(object)  # Waypoint object
    waypoint_list_changed = Signal()
    
    # Telemetry signals
    altitude_changed = Signal(float)
    ground_speed_changed = Signal(float)
    heading_changed = Signal(float)
    battery_changed = Signal(float)
    position_changed = Signal(float, float)  # lat, lon
    attitude_changed = Signal(float, float)  # roll, pitch
    
    # Error signals
    error_occurred = Signal(str)
    
    def __init__(self):
        """Initialize the ViewModel"""
        super().__init__()
        
        # Services
        self._flight_control_service: Optional[FlightControlService] = None
        self._mission_service: Optional[MissionService] = None
        self._telemetry_manager: Optional[TelemetryManager] = None
        
        # State
        self._is_connected = False
        self._is_armed = False
        self._current_flight_mode = "STABILIZE"
        self._current_mission: Optional[Mission] = None
        self._current_waypoint_index = 0
        self._mission_active = False
        
        # Telemetry data
        self._current_altitude = 0.0
        self._current_ground_speed = 0.0
        self._current_heading = 0.0
        self._current_battery = 100.0
        self._current_latitude = 0.0
        self._current_longitude = 0.0
        self._current_roll = 0.0
        self._current_pitch = 0.0
        
        # Update timer
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_telemetry)
        self._update_timer.start(100)  # 10 Hz update rate
        
    def set_services(self, flight_control_service: FlightControlService, 
                    mission_service: MissionService, 
                    telemetry_manager: TelemetryManager) -> None:
        """Set all required services"""
        self._flight_control_service = flight_control_service
        self._mission_service = mission_service
        self._telemetry_manager = telemetry_manager
        
        # Connect service signals
        self._connect_service_signals()
        
    def _connect_service_signals(self) -> None:
        """Connect signals from services"""
        if self._flight_control_service:
            self._flight_control_service.state_changed.connect(self._on_flight_state_changed)
            self._flight_control_service.mode_changed.connect(self._on_flight_mode_changed)
            
        if self._mission_service:
            self._mission_service.mission_created.connect(self._on_mission_created)
            self._mission_service.mission_updated.connect(self._on_mission_updated)
            self._mission_service.mission_started.connect(self._on_mission_started)
            self._mission_service.mission_completed.connect(self._on_mission_completed)
            self._mission_service.mission_aborted.connect(self._on_mission_aborted)
            self._mission_service.waypoint_reached.connect(self._on_waypoint_reached)
            
        if self._telemetry_manager:
            self._telemetry_manager.telemetry_updated.connect(self._on_telemetry_updated)
    
    # Properties
    @Property(bool, notify=connection_changed)
    def is_connected(self) -> bool:
        """Connection status"""
        return self._is_connected
    
    @Property(bool, notify=armed_changed)
    def is_armed(self) -> bool:
        """Armed status"""
        return self._is_armed
    
    @Property(str, notify=flight_mode_changed)
    def current_flight_mode(self) -> str:
        """Current flight mode"""
        return self._current_flight_mode
    
    @Property(object, notify=mission_created)
    def current_mission(self) -> Optional[Mission]:
        """Current mission"""
        return self._current_mission
    
    @Property(int, notify=waypoint_list_changed)
    def current_waypoint_index(self) -> int:
        """Current waypoint index"""
        return self._current_waypoint_index
    
    @Property(int, notify=waypoint_list_changed)
    def total_waypoints(self) -> int:
        """Total number of waypoints"""
        if self._current_mission:
            return len(self._current_mission.waypoints)
        return 0
    
    @Property(bool, notify=mission_started)
    def mission_active(self) -> bool:
        """Mission active status"""
        return self._mission_active
    
    @Property(float, notify=altitude_changed)
    def current_altitude(self) -> float:
        """Current altitude"""
        return self._current_altitude
    
    @Property(float, notify=ground_speed_changed)
    def current_ground_speed(self) -> float:
        """Current ground speed"""
        return self._current_ground_speed
    
    @Property(float, notify=heading_changed)
    def current_heading(self) -> float:
        """Current heading"""
        return self._current_heading
    
    @Property(float, notify=battery_changed)
    def current_battery(self) -> float:
        """Current battery level"""
        return self._current_battery
    
    @Property(float, notify=attitude_changed)
    def current_roll(self) -> float:
        """Current roll angle"""
        return self._current_roll
    
    @Property(float, notify=attitude_changed)
    def current_pitch(self) -> float:
        """Current pitch angle"""
        return self._current_pitch
    
    # Flight control slots
    @Slot()
    def arm(self) -> None:
        """Arm the vehicle"""
        if not self._flight_control_service:
            self.error_occurred.emit("Flight control service not available")
            return
            
        try:
            self._flight_control_service.arm()
        except Exception as e:
            self.error_occurred.emit(f"Failed to arm: {str(e)}")
    
    @Slot()
    def disarm(self) -> None:
        """Disarm the vehicle"""
        if not self._flight_control_service:
            self.error_occurred.emit("Flight control service not available")
            return
            
        try:
            self._flight_control_service.disarm()
        except Exception as e:
            self.error_occurred.emit(f"Failed to disarm: {str(e)}")
    
    @Slot(str)
    def set_flight_mode(self, mode: str) -> None:
        """Set flight mode"""
        if not self._flight_control_service:
            self.error_occurred.emit("Flight control service not available")
            return
            
        try:
            self._flight_control_service.set_mode(FlightMode(mode))
        except Exception as e:
            self.error_occurred.emit(f"Failed to set flight mode: {str(e)}")
    
    @Slot()
    def takeoff(self) -> None:
        """Takeoff"""
        if not self._flight_control_service:
            self.error_occurred.emit("Flight control service not available")
            return
            
        try:
            self._flight_control_service.takeoff()
        except Exception as e:
            self.error_occurred.emit(f"Failed to takeoff: {str(e)}")
    
    @Slot()
    def land(self) -> None:
        """Land"""
        if not self._flight_control_service:
            self.error_occurred.emit("Flight control service not available")
            return
            
        try:
            self._flight_control_service.land()
        except Exception as e:
            self.error_occurred.emit(f"Failed to land: {str(e)}")
    
    @Slot()
    def return_to_launch(self) -> None:
        """Return to launch"""
        if not self._flight_control_service:
            self.error_occurred.emit("Flight control service not available")
            return
            
        try:
            self._flight_control_service.return_to_launch()
        except Exception as e:
            self.error_occurred.emit(f"Failed to return to launch: {str(e)}")
    
    @Slot()
    def hold_position(self) -> None:
        """Hold current position"""
        if not self._flight_control_service:
            self.error_occurred.emit("Flight control service not available")
            return
            
        try:
            self._flight_control_service.hold_position()
        except Exception as e:
            self.error_occurred.emit(f"Failed to hold position: {str(e)}")
    
    # Mission control slots
    @Slot(str, list)
    def create_mission(self, name: str, waypoints: List[Waypoint]) -> None:
        """Create a new mission"""
        if not self._mission_service:
            self.error_occurred.emit("Mission service not available")
            return
            
        try:
            mission = self._mission_service.create_mission(name, waypoints)
            if mission:
                self._current_mission = mission
                self.waypoint_list_changed.emit()
        except Exception as e:
            self.error_occurred.emit(f"Failed to create mission: {str(e)}")
    
    @Slot(str)
    def start_mission(self, mission_id: str) -> None:
        """Start a mission"""
        if not self._mission_service:
            self.error_occurred.emit("Mission service not available")
            return
            
        try:
            success = self._mission_service.start_mission(mission_id)
            if success:
                self._mission_active = True
                self._current_waypoint_index = 0
        except Exception as e:
            self.error_occurred.emit(f"Failed to start mission: {str(e)}")
    
    @Slot()
    def pause_mission(self) -> None:
        """Pause current mission"""
        if not self._mission_service:
            self.error_occurred.emit("Mission service not available")
            return
            
        try:
            success = self._mission_service.pause_mission()
            if success:
                self._mission_active = False
        except Exception as e:
            self.error_occurred.emit(f"Failed to pause mission: {str(e)}")
    
    @Slot()
    def resume_mission(self) -> None:
        """Resume current mission"""
        if not self._mission_service:
            self.error_occurred.emit("Mission service not available")
            return
            
        try:
            success = self._mission_service.resume_mission()
            if success:
                self._mission_active = True
        except Exception as e:
            self.error_occurred.emit(f"Failed to resume mission: {str(e)}")
    
    @Slot()
    def abort_mission(self) -> None:
        """Abort current mission"""
        if not self._mission_service:
            self.error_occurred.emit("Mission service not available")
            return
            
        try:
            success = self._mission_service.abort_mission()
            if success:
                self._mission_active = False
                self._current_waypoint_index = 0
        except Exception as e:
            self.error_occurred.emit(f"Failed to abort mission: {str(e)}")
    
    @Slot(object)
    def upload_mission(self, mission: Mission) -> None:
        """Upload mission to vehicle"""
        if not self._mission_service:
            self.error_occurred.emit("Mission service not available")
            return
            
        try:
            success = self._mission_service.upload_mission(mission)
            if not success:
                self.error_occurred.emit("Failed to upload mission")
        except Exception as e:
            self.error_occurred.emit(f"Failed to upload mission: {str(e)}")
    
    @Slot(str)
    def import_mission(self, file_path: str) -> None:
        """Import mission from file"""
        if not self._mission_service:
            self.error_occurred.emit("Mission service not available")
            return
            
        try:
            mission = self._mission_service.import_mission(file_path)
            if mission:
                self._current_mission = mission
                self.waypoint_list_changed.emit()
        except Exception as e:
            self.error_occurred.emit(f"Failed to import mission: {str(e)}")
    
    @Slot(object, str)
    def export_mission(self, mission: Mission, file_path: str) -> None:
        """Export mission to file"""
        if not self._mission_service:
            self.error_occurred.emit("Mission service not available")
            return
            
        try:
            success = self._mission_service.export_mission(mission, file_path)
            if not success:
                self.error_occurred.emit("Failed to export mission")
        except Exception as e:
            self.error_occurred.emit(f"Failed to export mission: {str(e)}")
    
    @Slot(float, float, float)
    def add_waypoint(self, latitude: float, longitude: float, altitude: float) -> None:
        """Add waypoint at specified position"""
        if not self._current_mission:
            self.error_occurred.emit("No active mission")
            return
            
        try:
            waypoint = Waypoint(
                id=len(self._current_mission.waypoints),
                type=WaypointType.WAYPOINT,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                parameters={}
            )
            
            self._current_mission.waypoints.append(waypoint)
            self.waypoint_list_changed.emit()
        except Exception as e:
            self.error_occurred.emit(f"Failed to add waypoint: {str(e)}")
    
    @Slot(int)
    def remove_waypoint(self, waypoint_index: int) -> None:
        """Remove waypoint at specified index"""
        if not self._current_mission:
            self.error_occurred.emit("No active mission")
            return
            
        if waypoint_index < 0 or waypoint_index >= len(self._current_mission.waypoints):
            self.error_occurred.emit("Invalid waypoint index")
            return
            
        try:
            del self._current_mission.waypoints[waypoint_index]
            # Update waypoint IDs
            for i, waypoint in enumerate(self._current_mission.waypoints):
                waypoint.id = i
            self.waypoint_list_changed.emit()
        except Exception as e:
            self.error_occurred.emit(f"Failed to remove waypoint: {str(e)}")
    
    @Slot(float, float, float)
    def set_current_position(self, lat, lon, alt):
        print(f"[FlightNavigationViewModel] set_current_position: lat={lat}, lon={lon}, alt={alt}")
        self._current_latitude = lat
        self._current_longitude = lon
        self._current_altitude = alt
        self.position_changed.emit(lat, lon)
        self.altitude_changed.emit(alt)

    @Slot(float, float, float)
    def set_current_attitude(self, roll, pitch, yaw):
        self._current_roll = roll
        self._current_pitch = pitch
        self._current_heading = yaw
        self.attitude_changed.emit(roll, pitch)
        self.heading_changed.emit(yaw)

    @Slot(float)
    def set_current_battery(self, voltage):
        self._current_battery = voltage
        self.battery_changed.emit(voltage)
    
    # Signal handlers
    def _on_flight_state_changed(self) -> None:
        """Handle flight state changes"""
        if self._flight_control_service:
            state = self._flight_control_service.get_state()
            if state:
                self._is_connected = state.is_connected
                self._is_armed = state.is_armed
                
                self.connection_changed.emit(self._is_connected)
                self.armed_changed.emit(self._is_armed)
                self.flight_state_changed.emit()
    
    def _on_flight_mode_changed(self, mode: FlightMode) -> None:
        """Handle flight mode changes"""
        self._current_flight_mode = mode.value
        self.flight_mode_changed.emit(self._current_flight_mode)
    
    def _on_mission_created(self, mission: Mission) -> None:
        """Handle mission creation"""
        self._current_mission = mission
        self.mission_created.emit(mission)
        self.waypoint_list_changed.emit()
    
    def _on_mission_updated(self, mission: Mission) -> None:
        """Handle mission updates"""
        self._current_mission = mission
        self.mission_updated.emit(mission)
        self.waypoint_list_changed.emit()
    
    def _on_mission_started(self, mission: Mission) -> None:
        """Handle mission start"""
        self._mission_active = True
        self._current_waypoint_index = 0
        self.mission_started.emit(mission)
    
    def _on_mission_completed(self, mission: Mission) -> None:
        """Handle mission completion"""
        self._mission_active = False
        self.mission_completed.emit(mission)
    
    def _on_mission_aborted(self, mission: Mission) -> None:
        """Handle mission abort"""
        self._mission_active = False
        self.mission_aborted.emit(mission)
    
    def _on_waypoint_reached(self, waypoint: Waypoint) -> None:
        """Handle waypoint reached"""
        self._current_waypoint_index += 1
        self.waypoint_reached.emit(waypoint)
        self.waypoint_list_changed.emit()
    
    def _on_telemetry_updated(self, telemetry_data: Dict[str, Any]) -> None:
        """Handle telemetry updates"""
        # Update telemetry values
        if 'altitude' in telemetry_data:
            self._current_altitude = telemetry_data['altitude']
            self.altitude_changed.emit(self._current_altitude)
            
        if 'ground_speed' in telemetry_data:
            self._current_ground_speed = telemetry_data['ground_speed']
            self.ground_speed_changed.emit(self._current_ground_speed)
            
        if 'heading' in telemetry_data:
            self._current_heading = telemetry_data['heading']
            self.heading_changed.emit(self._current_heading)
            
        if 'battery_remaining' in telemetry_data:
            self._current_battery = telemetry_data['battery_remaining']
            self.battery_changed.emit(self._current_battery)
            
        if 'latitude' in telemetry_data and 'longitude' in telemetry_data:
            self._current_latitude = telemetry_data['latitude']
            self._current_longitude = telemetry_data['longitude']
            self.position_changed.emit(self._current_latitude, self._current_longitude)
            
        if 'roll' in telemetry_data and 'pitch' in telemetry_data:
            self._current_roll = telemetry_data['roll']
            self._current_pitch = telemetry_data['pitch']
            self.attitude_changed.emit(self._current_roll, self._current_pitch)
    
    def _update_telemetry(self) -> None:
        """Update telemetry data"""
        if self._telemetry_manager:
            try:
                telemetry_data = self._telemetry_manager.get_latest_telemetry()
                if telemetry_data:
                    self._on_telemetry_updated(telemetry_data)
            except Exception as e:
                # Silently handle telemetry update errors
                pass 