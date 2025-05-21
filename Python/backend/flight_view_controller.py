# -*- coding: utf-8 -*-
"""
FlightViewController - Controller for the 3D Flight View
Connects the QML UI with the map view and the backend
"""

import os
import sys
import math
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, QTimer, Qt
from PySide6.QtWidgets import QWidget, QMainWindow, QVBoxLayout
from PySide6.QtGui import QPainter, QPen, QBrush, QColor

# Simplified 2D map widget for embedding
class SimpleMapWidget(QWidget):
    """Simple 2D map display with drone position"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #1e1e1e;")
        
        # Map attributes
        self.drone_lat = 51.505600  # Standard position
        self.drone_lon = 7.452400
        self.drone_alt = 100.0
        self.drone_heading = 0.0
        self.drone_speed = 0.0
        self.drone_battery = 100.0
        self.drone_path = []
        self.max_path_length = 100
        
        # Map view properties
        self.center_lat = self.drone_lat
        self.center_lon = self.drone_lon
        self.zoom = 1.0
        self.show_grid = True
        self.show_path = True
        
    def paintEvent(self, event):
        """Draws the 2D map view"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QBrush(QColor(30, 30, 30)))
        
        # Draw grid
        if self.show_grid:
            self.draw_grid(painter)
            
        # Draw drone path
        if self.show_path and len(self.drone_path) > 1:
            self.draw_path(painter)
            
        # Draw drone
        x, y = self.geo_to_screen(self.drone_lat, self.drone_lon)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QBrush(QColor(255, 50, 50)))
        painter.drawEllipse(x - 10, y - 10, 20, 20)
        
        # Draw direction arrow
        rad_heading = math.radians(self.drone_heading)
        arrow_x = x + int(math.sin(rad_heading) * 20)
        arrow_y = y - int(math.cos(rad_heading) * 20)
        painter.drawLine(x, y, arrow_x, arrow_y)
        
        # Draw info panel
        self.draw_info_panel(painter)
    
    def update_drone_position(self, lat, lon, alt, heading=0, speed=0, battery=100):
        """Updates the drone position on the map"""
        self.drone_lat = lat
        self.drone_lon = lon
        self.drone_alt = alt
        self.drone_heading = heading
        self.drone_speed = speed
        self.drone_battery = battery
        
        # Add position to path
        self.drone_path.append((lat, lon, alt))
        # Limit path length
        if len(self.drone_path) > self.max_path_length:
            self.drone_path = self.drone_path[-self.max_path_length:]
            
        self.update()
    
    def geo_to_screen(self, lat, lon):
        """Converts geographic coordinates to screen coordinates"""
        scale = 10000 * self.zoom
        x = (lon - self.center_lon) * scale
        y = (self.center_lat - lat) * scale
        screen_x = self.width() / 2 + x
        screen_y = self.height() / 2 + y
        return int(screen_x), int(screen_y)
        
    def draw_grid(self, painter):
        """Draws a simple coordinate grid"""
        width, height = self.width(), self.height()
        
        # Draw grid lines
        painter.setPen(QPen(QColor(60, 60, 60)))
        
        # Horizontal lines
        for y in range(0, height, 50):
            painter.drawLine(0, y, width, y)
            
        # Vertical lines
        for x in range(0, width, 50):
            painter.drawLine(x, 0, x, height)
    
    def draw_path(self, painter):
        """Draws the drone path"""
        painter.setPen(QPen(QColor(255, 255, 0, 150), 2))
        
        prev_point = None
        for lat, lon, _ in self.drone_path:
            x, y = self.geo_to_screen(lat, lon)
            if prev_point:
                painter.drawLine(prev_point[0], prev_point[1], x, y)
            prev_point = (x, y)
            
    def draw_info_panel(self, painter):
        """Draws an info panel with drone data"""
        panel_x, panel_y = 10, 10
        panel_width, panel_height = 180, 100
        
        # Panel background
        painter.setPen(QPen(QColor(255, 255, 255, 100)))
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRect(panel_x, panel_y, panel_width, panel_height)
        
        # Display information
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        
        texts = [
            f"Lat: {self.drone_lat:.6f}",
            f"Lon: {self.drone_lon:.6f}",
            f"Alt: {self.drone_alt:.1f} m",
            f"Speed: {self.drone_speed:.1f} m/s",
            f"Battery: {self.drone_battery:.0f}%"
        ]
        
        for i, text in enumerate(texts):
            painter.drawText(panel_x + 10, panel_y + 20 + i * 15, text)


class FlightViewController(QObject):
    """Controller for the Flight View and the 3D map view"""
    
    # Signal for position changes
    dronePositionChanged = Signal()
    
    # Signal for map type switching
    mapTypeChanged = Signal(int)  # 0 = 2D view, 1 = 3D view
    
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.map_widget = None
        
        # Drone status
        self._drone_lat = 51.5056
        self._drone_lon = 7.4524
        self._drone_alt = 100.0
        self._drone_speed = 0.0
        self._drone_battery = 100.0
        
        # Map mode (0 = 2D view, 1 = 3D view)
        self._map_type = 1  # Standard: 3D view
        
        # Timer for simulation purposes
        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(1000)
        self.sim_timer.timeout.connect(self.simulate_drone_movement)
    
    def initialize(self, root_item):
        """Initializes the Flight View and connects it to the QML UI."""
        try:
            print("[DEBUG] Initializing FlightViewController")
            # Find the map3DContainer item in QML
            flight_view = root_item.findChild(QObject, "flightView")
            map_container = None
            
            if flight_view:
                print("[INFO] FlightView found")
                map_container = flight_view.findChild(QObject, "map3DContainer")
                
                # Connect signal for map type change
                if hasattr(flight_view, "mapTypeChanged"):
                    flight_view.mapTypeChanged.connect(self.set_map_type)
                    print("[INFO] MapType-Changed signal connected")
                else:
                    print("[WARNING] mapTypeChanged signal not found")
                
                # Connect signal to open external 3D map
                if hasattr(flight_view, "openExternalMap"):
                    flight_view.openExternalMap.connect(self.open_external_map)
                    print("[INFO] Open-External-Map signal connected")
                else:
                    print("[WARNING] openExternalMap signal not found")
            else:
                print("[ERROR] FlightView not found")
                return False
            
            if map_container:
                print("[INFO] Map3DContainer found, creating simplified 2D map")
                
                # Create the simplified map widget
                self.map_widget = SimpleMapWidget()
                
                # Get the Win-ID for embedding in QML - very important for embedding!
                win_id = int(self.map_widget.winId())  # Explicit conversion to integer for QML
                print(f"[DEBUG] Win-ID for 2D map: {win_id}")
                
                # Share the Win-ID with the QML container so that the widget is correctly embedded
                if hasattr(map_container, "setNativeWindowId"):
                    # Call the QML function to embed the native container
                    map_container.setNativeWindowId(win_id)
                    print("[INFO] Map successfully embedded in QML")
                    
                    # Activate the widget immediately so that it becomes visible
                    self.map_widget.show()
                    self.map_widget.setFocus()
                    
                    # Initialize map with current drone data
                    lat, lon = self._drone_lat, self._drone_lon
                    self.update_drone_position(lat, lon, self._drone_alt, 0, self._drone_speed, self._drone_battery)
                else:
                    print("[ERROR] Container has no setNativeWindowId method")
            else:
                print("[WARNING] Map3DContainer not found, map cannot be embedded")
                return False
                
            # Start simulation
            print("[INFO] Starting simulation timer")
            self.sim_timer.start()
            
            print("[INFO] FlightViewController successfully initialized")
            return True
        except Exception as e:
            print(f"[ERROR] During initialization of FlightViewController: {str(e)}")
            return False
    
    def simulate_drone_movement(self):
        """Simulates drone movement for testing purposes."""
        try:
            # Static factor for simulation
            self.sim_angle = getattr(self, 'sim_angle', 0.0) + 0.1
            
            # Simulate circular movement
            radius = 0.001
            angle = self.sim_angle
            
            lat = self._drone_lat + radius * math.sin(angle)
            lon = self._drone_lon + radius * math.cos(angle)
            alt = 100.0 + 20.0 * math.sin(angle * 2)
            heading = (angle * 180 / math.pi) % 360  # Convert radians to degrees
            
            # Update drone position
            self.update_drone_position(lat, lon, alt, heading, 5.0, 75)
            
            # Center map on drone if follow mode is active
            if hasattr(self, 'should_follow_drone') and self.should_follow_drone:
                self.center_on_drone()
            
        except Exception as e:
            print(f"Error sending updates: {str(e)}")
    
    def update_drone_position(self, lat, lon, alt, heading=0, speed=0, battery=100):
        """Updates the drone position on the map"""
        self._drone_lat = lat
        self._drone_lon = lon
        self._drone_alt = alt
        self._drone_speed = speed
        self._drone_battery = battery
        
        # Update widget if available
        if self.map_widget:
            self.map_widget.update_drone_position(lat, lon, alt, heading, speed, battery)
            
        # Send signal for UI update
        self.dronePositionChanged.emit()
    
    def set_map_type(self, map_type):
        """Sets the map type (0=2D, 1=3D)"""
        print(f"[INFO] Map type changed: {map_type}")
        self._map_type = map_type
        
        if self.map_widget:
            if map_type == 1:  # 3D view
                self.map_widget.zoom = 2.0
            else:  # 2D view
                self.map_widget.zoom = 1.0
                
            self.map_widget.update()
            return True
        return False
    
    @Slot()
    def open_external_map(self):
        """Opens the external 3D map in a separate window."""
        print("\n\n[DEBUG] open_external_map() was called!\n\n")
        
        try:
            script_path = Path(__file__).parent.parent / "standalone_map.py"
            parent_dir = script_path.parent.absolute()
            
            os.system(f'start cmd /k "{sys.executable}" "{script_path}"')
            print("External 3D map application was started")
        except Exception as e:
            print(f"[ERROR] When starting the external 3D map: {str(e)}")
    
    @Slot()
    def center_on_drone(self):
        """Centers the map on the current drone position."""
        if self.map_widget:
            self.map_widget.center_lat = self._drone_lat
            self.map_widget.center_lon = self._drone_lon
            self.map_widget.update()
    
    @Slot()
    def add_waypoint(self):
        """Adds a waypoint at the current drone position."""
        print(f"[NAVIGATION] Waypoint added at Lat: {self._drone_lat}, Lon: {self._drone_lon}")
        # In a real implementation, a waypoint would be added to the flight route here
        
    @Slot()
    def start_mission(self):
        """Starts the mission and follows the waypoints."""
        print("[NAVIGATION] Mission started")
        # In a real implementation, a command to start the mission would be sent here
        
    @Slot()
    def land(self):
        """Performs an automatic landing procedure."""
        print(f"[NAVIGATION] Landing initiated at Lat: {self._drone_lat}, Lon: {self._drone_lon}")
        # In a real implementation, a landing command would be sent to the drone
        
    @Slot()
    def return_to_home(self):
        """Commands the drone to return to the starting point."""
        print("[NAVIGATION] Return to home point initiated")
        # In a real implementation, an RTH command would be sent to the drone
        
    @Slot()
    def emergency_stop(self):
        """Performs an emergency stop of the drone."""
        print("[NAVIGATION] !!! EMERGENCY STOP TRIGGERED !!!")
        # In a real implementation, an emergency command would be sent to the drone
