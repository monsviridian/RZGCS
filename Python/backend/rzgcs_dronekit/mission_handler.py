"""
DroneKit Mission Handler - Verwaltet Mission-Upload, -Download und -Ausführung
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal

# DroneKit-Imports
# External DroneKit import - fixed to avoid circular imports
import dronekit as dronekit_external  # Externe DroneKit-Bibliothek
Vehicle = dronekit_external.Vehicle  # Aus externer DroneKit-Bibliothek
VehicleMode = dronekit_external.VehicleMode  # Aus externer DroneKit-Bibliothek
Command = dronekit_external.Command  # Aus externer DroneKit-Bibliothek

from pymavlink import mavutil

from .utils import DroneKitUtils

class DroneKitMissionHandler(QObject):
    """Verwaltet Mission-Upload, -Download und -Ausführung"""
    
    # Signals
    mission_uploaded = Signal(int)  # number of waypoints
    mission_downloaded = Signal(int)  # number of waypoints
    mission_started = Signal()
    mission_paused = Signal()
    mission_resumed = Signal()
    mission_completed = Signal()
    waypoint_reached = Signal(int)  # waypoint index
    mission_error = Signal(str)
    mission_log = Signal(str)
    
    def __init__(self, vehicle: Vehicle, connector, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.connector = connector
        self.current_mission = []
        self.mission_uploaded = False
        self.mission_running = False
        self.current_waypoint = 0
        self.total_waypoints = 0
        
    async def upload_mission(self, waypoints: List[Dict[str, Any]]) -> bool:
        """Lädt Mission hoch"""
        try:
            # Bestehende Mission löschen
            cmds = self.vehicle.commands
            cmds.clear()
            
            # Waypoints zu Commands konvertieren
            for i, wp in enumerate(waypoints):
                cmd = Command(
                    0, 0, 0,  # target_system, target_component, frame
                    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,  # command
                    0, 0,     # current, autocontinue
                    wp.get('param1', 0),  # param1: acceptance radius
                    wp.get('param2', 0),  # param2: pass radius
                    wp.get('param3', 0),  # param3: yaw
                    wp.get('param4', 0),  # param4: loiter radius
                    wp['lat'], wp['lon'], wp['alt']  # param5, param6, param7
                )
                cmds.add(cmd)
            
            # Mission hochladen
            cmds.upload()
            
            # Warten auf Upload-Abschluss
            timeout = time.time() + 30
            while not cmds.count > 0 and time.time() < timeout:
                await asyncio.sleep(0.1)
            
            if cmds.count > 0:
                self.current_mission = waypoints
                self.mission_uploaded = True
                self.total_waypoints = len(waypoints)
                self.mission_uploaded.emit(len(waypoints))
                self.mission_log.emit(f"Mission uploaded: {len(waypoints)} waypoints")
                return True
            else:
                raise TimeoutError("Mission upload timeout")
            
        except Exception as e:
            error_msg = f"Mission upload failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return False
    
    async def download_mission(self) -> List[Dict[str, Any]]:
        """Lädt aktuelle Mission herunter"""
        try:
            cmds = self.vehicle.commands
            cmds.download()
            
            # Warten auf Download-Abschluss
            timeout = time.time() + 30
            while cmds.count == 0 and time.time() < timeout:
                await asyncio.sleep(0.1)
            
            if cmds.count == 0:
                raise TimeoutError("Mission download timeout")
            
            cmds.wait_ready()
            
            waypoints = []
            for cmd in cmds:
                if cmd.command == mavutil.mavlink.MAV_CMD_NAV_WAYPOINT:
                    waypoint = {
                        'lat': cmd.x,
                        'lon': cmd.y,
                        'alt': cmd.z,
                        'param1': cmd.param1,  # acceptance radius
                        'param2': cmd.param2,  # pass radius
                        'param3': cmd.param3,  # yaw
                        'param4': cmd.param4   # loiter radius
                    }
                    waypoints.append(waypoint)
            
            self.current_mission = waypoints
            self.total_waypoints = len(waypoints)
            self.mission_downloaded.emit(len(waypoints))
            self.mission_log.emit(f"Mission downloaded: {len(waypoints)} waypoints")
            return waypoints
            
        except Exception as e:
            error_msg = f"Mission download failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return []
    
    async def start_mission(self) -> bool:
        """Startet Mission"""
        try:
            if not self.mission_uploaded:
                raise ValueError("No mission uploaded")
            
            # AUTO-Modus aktivieren
            self.vehicle.mode = VehicleMode("AUTO")
            
            # Warten auf AUTO-Modus
            timeout = time.time() + 10
            while self.vehicle.mode.name != "AUTO" and time.time() < timeout:
                await asyncio.sleep(0.1)
            
            if self.vehicle.mode.name == "AUTO":
                self.mission_running = True
                self.current_waypoint = 0
                self.mission_started.emit()
                self.mission_log.emit("Mission started")
                
                # Mission-Monitoring starten
                asyncio.create_task(self._monitor_mission())
                return True
            else:
                raise TimeoutError("Failed to set AUTO mode")
                
        except Exception as e:
            error_msg = f"Mission start failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return False
    
    async def pause_mission(self) -> bool:
        """Pausiert Mission"""
        try:
            # LOITER-Modus für Pause
            self.vehicle.mode = VehicleMode("LOITER")
            self.mission_running = False
            self.mission_paused.emit()
            self.mission_log.emit("Mission paused")
            return True
        except Exception as e:
            error_msg = f"Mission pause failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return False
    
    async def resume_mission(self) -> bool:
        """Setzt Mission fort"""
        try:
            # Zurück zu AUTO-Modus
            self.vehicle.mode = VehicleMode("AUTO")
            self.mission_running = True
            self.mission_resumed.emit()
            self.mission_log.emit("Mission resumed")
            
            # Mission-Monitoring fortsetzen
            asyncio.create_task(self._monitor_mission())
            return True
        except Exception as e:
            error_msg = f"Mission resume failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return False
    
    async def stop_mission(self) -> bool:
        """Stoppt Mission"""
        try:
            # GUIDED-Modus für Stopp
            self.vehicle.mode = VehicleMode("GUIDED")
            self.mission_running = False
            self.mission_log.emit("Mission stopped")
            return True
        except Exception as e:
            error_msg = f"Mission stop failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return False
    
    async def _monitor_mission(self):
        """Überwacht Mission-Fortschritt"""
        try:
            while self.mission_running:
                # Aktuellen Waypoint prüfen
                cmds = self.vehicle.commands
                current_seq = cmds.next
                
                if current_seq != self.current_waypoint:
                    self.current_waypoint = current_seq
                    self.waypoint_reached.emit(current_seq)
                    self.mission_log.emit(f"Reached waypoint {current_seq + 1}/{self.total_waypoints}")
                
                # Mission-Abschluss prüfen
                if current_seq >= self.total_waypoints - 1:
                    self.mission_running = False
                    self.mission_completed.emit()
                    self.mission_log.emit("Mission completed")
                    break
                
                await asyncio.sleep(1)  # 1 Hz Monitoring
                
        except Exception as e:
            error_msg = f"Mission monitoring error: {str(e)}"
            self.mission_error.emit(error_msg)
    
    def get_mission_status(self) -> Dict[str, Any]:
        """Gibt aktuellen Mission-Status zurück"""
        try:
            cmds = self.vehicle.commands
            current_waypoint = cmds.next
            
            return {
                'total_waypoints': self.total_waypoints,
                'current_waypoint': current_waypoint,
                'mission_uploaded': self.mission_uploaded,
                'mission_running': self.mission_running,
                'in_mission': self.vehicle.mode.name == "AUTO",
                'progress': (current_waypoint / max(self.total_waypoints, 1)) * 100
            }
        except:
            return {
                'total_waypoints': 0,
                'current_waypoint': 0,
                'mission_uploaded': False,
                'mission_running': False,
                'in_mission': False,
                'progress': 0
            }
    
    def get_current_mission(self) -> List[Dict[str, Any]]:
        """Gibt aktuelle Mission zurück"""
        return self.current_mission.copy()
    
    async def clear_mission(self) -> bool:
        """Löscht aktuelle Mission"""
        try:
            cmds = self.vehicle.commands
            cmds.clear()
            cmds.upload()
            
            self.current_mission = []
            self.mission_uploaded = False
            self.mission_running = False
            self.current_waypoint = 0
            self.total_waypoints = 0
            
            self.mission_log.emit("Mission cleared")
            return True
            
        except Exception as e:
            error_msg = f"Mission clear failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return False
    
    async def create_survey_mission(self, center_lat: float, center_lon: float, 
                                  altitude: float, spacing: float, 
                                  rows: int, cols: int) -> List[Dict[str, Any]]:
        """Erstellt Survey-Mission (Raster-Flug)"""
        try:
            waypoints = []
            
            # Startpunkt (Takeoff)
            waypoints.append({
                'lat': center_lat,
                'lon': center_lon,
                'alt': altitude,
                'command': mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
            })
            
            # Raster-Waypoints berechnen
            lat_offset = spacing / 111320.0  # Ungefähre Konvertierung zu Grad
            lon_offset = spacing / (111320.0 * math.cos(math.radians(center_lat)))
            
            start_lat = center_lat - (rows - 1) * lat_offset / 2
            start_lon = center_lon - (cols - 1) * lon_offset / 2
            
            for row in range(rows):
                for col in range(cols):
                    lat = start_lat + row * lat_offset
                    lon = start_lon + col * lon_offset
                    
                    waypoints.append({
                        'lat': lat,
                        'lon': lon,
                        'alt': altitude,
                        'command': mavutil.mavlink.MAV_CMD_NAV_WAYPOINT
                    })
            
            # Return to Launch
            waypoints.append({
                'lat': center_lat,
                'lon': center_lon,
                'alt': altitude,
                'command': mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH
            })
            
            self.mission_log.emit(f"Survey mission created: {len(waypoints)} waypoints")
            return waypoints
            
        except Exception as e:
            error_msg = f"Survey mission creation failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return []
    
    async def create_circle_mission(self, center_lat: float, center_lon: float,
                                  altitude: float, radius: float, 
                                  points: int = 8) -> List[Dict[str, Any]]:
        """Erstellt Kreis-Mission"""
        try:
            waypoints = []
            
            # Startpunkt (Takeoff)
            waypoints.append({
                'lat': center_lat,
                'lon': center_lon,
                'alt': altitude,
                'command': mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
            })
            
            # Kreis-Waypoints berechnen
            for i in range(points):
                angle = 2 * math.pi * i / points
                lat_offset = radius * math.cos(angle) / 111320.0
                lon_offset = radius * math.sin(angle) / (111320.0 * math.cos(math.radians(center_lat)))
                
                waypoints.append({
                    'lat': center_lat + lat_offset,
                    'lon': center_lon + lon_offset,
                    'alt': altitude,
                    'command': mavutil.mavlink.MAV_CMD_NAV_WAYPOINT
                })
            
            # Return to Launch
            waypoints.append({
                'lat': center_lat,
                'lon': center_lon,
                'alt': altitude,
                'command': mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH
            })
            
            self.mission_log.emit(f"Circle mission created: {len(waypoints)} waypoints")
            return waypoints
            
        except Exception as e:
            error_msg = f"Circle mission creation failed: {str(e)}"
            self.mission_error.emit(error_msg)
            return [] 