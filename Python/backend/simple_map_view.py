#!/usr/bin/env python
"""
Simple Map View for RZGCS - Guaranteed working map module without external dependencies
"""

import sys
import os
import math
import json
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QPointF, QRectF, QObject
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QGridLayout)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
                          QLinearGradient, QPalette, QPolygonF)


class SimpleMapView(QWidget):
    """Simple map view for integration into RZGCS
    
    This class provides a basic 2D map that doesn't require a WebEngine
    and is guaranteed to work in any environment.
    """
    
    # Signals for interaction with other components
    positionClicked = Signal(float, float, float)  # lat, lon, alt
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        
        # Drohnenposition und Eigenschaften
        self.drone_lat = 51.505600
        self.drone_lon = 7.452400
        self.drone_alt = 100.0
        self.drone_heading = 0.0
        self.drone_speed = 0.0
        self.drone_battery = 100.0
        
        # Pfad der Drohne
        self.path = []
        self.max_path_length = 100
        self.show_path = True
        
        # Map parameters
        self.center_lat = self.drone_lat
        self.center_lon = self.drone_lon
        self.scale = 100000  # Scaling factor (higher values = more zoom)
        self.follow_drone = True  # Automatic drone tracking
        
        # Layout for UI elements
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Status label at the top
        self.status_label = QLabel("RZGCS 2D Map - Active")
        self.status_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: white; padding: 5px;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # Control panel at the bottom
        control_panel = QWidget()
        control_panel.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: white; padding: 5px;"
        )
        control_layout = QHBoxLayout(control_panel)
        
        # Buttons for map control
        center_button = QPushButton("Center")
        center_button.clicked.connect(self.center_on_drone)
        control_layout.addWidget(center_button)
        
        self.follow_button = QPushButton("Follow: On")
        self.follow_button.clicked.connect(self.toggle_follow)
        control_layout.addWidget(self.follow_button)
        
        self.path_button = QPushButton("Path: On")
        self.path_button.clicked.connect(self.toggle_path)
        control_layout.addWidget(self.path_button)
        
        layout.addWidget(control_panel)
        
        # Für Mausinteraktion
        self.setMouseTracking(True)
        self.last_mouse_pos = None
    
    def center_on_drone(self):
        """Centers the map on the current drone position"""
        self.center_lat = self.drone_lat
        self.center_lon = self.drone_lon
        self.update()
    
    def toggle_follow(self):
        """Toggles automatic drone tracking on/off"""
        self.follow_drone = not self.follow_drone
        self.follow_button.setText(f"Follow: {'On' if self.follow_drone else 'Off'}")
        if self.follow_drone:
            self.center_on_drone()
        self.update()
    
    def toggle_path(self):
        """Toggles the display of the flight path on/off"""
        self.show_path = not self.show_path
        self.path_button.setText(f"Path: {'On' if self.show_path else 'Off'}")
        self.update()
    
    def update_drone_position(self, lat, lon, alt=None, heading=None, speed=None, battery=None):
        """Updates the drone position and other parameters
        
        This method is called from outside to update the drone data.
        """
        self.drone_lat = lat
        self.drone_lon = lon
        if alt is not None:
            self.drone_alt = alt
        if heading is not None:
            self.drone_heading = heading
        if speed is not None:
            self.drone_speed = speed
        if battery is not None:
            self.drone_battery = battery
        
        # Add to path history
        self.path.append((lat, lon))
        if len(self.path) > self.max_path_length:
            self.path = self.path[-self.max_path_length:]
        
        # If tracking is enabled, center map on drone
        if self.follow_drone:
            self.center_lat = lat
            self.center_lon = lon
        
        # Redraw map
        self.update()
    
    def clear_path(self):
        """Clears the previous flight path"""
        self.path = []
        self.update()
    
    def geo_to_screen(self, lat, lon):
        """Converts geographic coordinates to screen coordinates"""
        dx = (lon - self.center_lon) * self.scale
        dy = (lat - self.center_lat) * self.scale
        
        # Screen coordinates (origin in the center)
        x = self.width() / 2 + dx
        y = self.height() / 2 - dy  # Inverted, as y increases downward
        
        return QPointF(x, y)
    
    def screen_to_geo(self, x, y):
        """Converts screen coordinates to geographic coordinates"""
        dx = x - self.width() / 2
        dy = self.height() / 2 - y  # Inverted, as y increases downward
        
        lon = self.center_lon + dx / self.scale
        lat = self.center_lat + dy / self.scale
        
        return lat, lon
    
    def paintEvent(self, event):
        """Draws the map and drone"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background - simple gradient (sky/ground)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(135, 206, 250))  # Light blue top
        gradient.setColorAt(1, QColor(34, 139, 34))    # Green bottom
        painter.fillRect(self.rect(), gradient)
        
        # Draw grid
        self.draw_grid(painter)
        
        # Draw path if enabled
        if self.show_path:
            self.draw_path(painter)
        
        # Draw drone
        self.draw_drone(painter)
        
        # Display information
        self.draw_info_panel(painter)
        
        # Draw compass
        self.draw_compass(painter)
    
    def draw_grid(self, painter):
        """Draws a simple coordinate grid"""
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
        
        # Grid spacing in geographic coordinates
        grid_spacing = 0.001  # approx. 100m
        
        # Calculate visible area
        width_deg = self.width() / self.scale
        height_deg = self.height() / self.scale
        
        min_lon = self.center_lon - width_deg / 2
        max_lon = self.center_lon + width_deg / 2
        min_lat = self.center_lat - height_deg / 2
        max_lat = self.center_lat + height_deg / 2
        
        # Round grid lines down/up for clean display
        min_lon_grid = math.floor(min_lon / grid_spacing) * grid_spacing
        max_lon_grid = math.ceil(max_lon / grid_spacing) * grid_spacing
        min_lat_grid = math.floor(min_lat / grid_spacing) * grid_spacing
        max_lat_grid = math.ceil(max_lat / grid_spacing) * grid_spacing
        
        # Horizontal lines
        lat = min_lat_grid
        while lat <= max_lat_grid:
            start = self.geo_to_screen(lat, min_lon_grid)
            end = self.geo_to_screen(lat, max_lon_grid)
            painter.drawLine(start, end)
            lat += grid_spacing
        
        # Vertical lines
        lon = min_lon_grid
        while lon <= max_lon_grid:
            start = self.geo_to_screen(min_lat_grid, lon)
            end = self.geo_to_screen(max_lat_grid, lon)
            painter.drawLine(start, end)
            lon += grid_spacing
    
    def draw_path(self, painter):
        """Draws the flight path of the drone"""
        if len(self.path) < 2:
            return
        
        painter.setPen(QPen(QColor(255, 255, 0, 180), 2))
        
        path = QPainterPath()
        first_point = self.geo_to_screen(*self.path[0])
        path.moveTo(first_point)
        
        for lat, lon in self.path[1:]:
            point = self.geo_to_screen(lat, lon)
            path.lineTo(point)
        
        painter.drawPath(path)
    
    def draw_drone(self, painter):
        """Draws the drone as an arrow in the direction of movement"""
        drone_pos = self.geo_to_screen(self.drone_lat, self.drone_lon)
        
        # Drone as a colored circle with arrow
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 200)))
        
        # Size of the drone, dependent on zoom
        drone_size = 10
        
        painter.drawEllipse(drone_pos, drone_size, drone_size)
        
        # Arrow for heading
        rad_heading = math.radians(self.drone_heading)
        arrow_end = QPointF(
            drone_pos.x() + math.sin(rad_heading) * drone_size * 1.5,
            drone_pos.y() - math.cos(rad_heading) * drone_size * 1.5
        )
        
        painter.drawLine(drone_pos, arrow_end)
    
    def draw_info_panel(self, painter):
        """Displays information about the drone"""
        panel_width = 180
        panel_height = 140
        margin = 10
        
        # Panel in the bottom left corner
        panel_rect = QRectF(
            margin, 
            self.height() - panel_height - margin,
            panel_width,
            panel_height
        )
        
        # Background with transparency
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRect(panel_rect)
        
        # Display text
        painter.setPen(QPen(Qt.white))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        
        # Calculate text positions
        text_x = panel_rect.left() + 10
        text_y = panel_rect.top() + 20
        line_height = 18
        
        # Drone information
        info_lines = [
            f"Lat: {self.drone_lat:.6f}",
            f"Lon: {self.drone_lon:.6f}",
            f"Alt: {self.drone_alt:.1f} m",
            f"Heading: {int(self.drone_heading)}u00b0",
            f"Speed: {self.drone_speed:.1f} m/s",
            f"Battery: {int(self.drone_battery)}%",
        ]
        
        for i, line in enumerate(info_lines):
            painter.drawText(text_x, text_y + i * line_height, line)
    
    def draw_compass(self, painter):
        """Draws a simple compass"""
        compass_size = 60
        margin = 10
        compass_x = self.width() - compass_size - margin
        compass_y = margin + compass_size / 2
        
        # Compass background
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawEllipse(QPointF(compass_x, compass_y), compass_size / 2, compass_size / 2)
        
        # Cardinal directions
        painter.setPen(QPen(Qt.white, 1))
        
        directions = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
        for label, angle in directions:
            rad = math.radians(angle)
            dir_x = compass_x + math.sin(rad) * (compass_size / 2 - 15)
            dir_y = compass_y - math.cos(rad) * (compass_size / 2 - 15)
            
            painter.drawText(dir_x - 5, dir_y + 5, label)
        
        # North arrow
        painter.setPen(QPen(Qt.red, 2))
        north_x = compass_x
        north_y = compass_y - compass_size / 3
        painter.drawLine(compass_x, compass_y, north_x, north_y)
        
        # Drone arrow
        painter.setPen(QPen(QColor(50, 180, 255), 2))
        rad_heading = math.radians(self.drone_heading)
        drone_dir_x = compass_x + math.sin(rad_heading) * (compass_size / 3)
        drone_dir_y = compass_y - math.cos(rad_heading) * (compass_size / 3)
        painter.drawLine(compass_x, compass_y, drone_dir_x, drone_dir_y)
    
    def mousePressEvent(self, event):
        """Handles mouse click events"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.position()
            
            # When clicked with Shift, select position as target
            if event.modifiers() & Qt.ShiftModifier:
                lat, lon = self.screen_to_geo(event.position().x(), event.position().y())
                alt = 50.0  # Default altitude for targets
                self.positionClicked.emit(lat, lon, alt)
    
    def mouseMoveEvent(self, event):
        """Handles mouse movements for map panning"""
        if self.last_mouse_pos and event.buttons() & Qt.LeftButton:
            delta = event.position() - self.last_mouse_pos
            # Convert from pixels to coordinates
            self.center_lon -= delta.x() / self.scale
            self.center_lat += delta.y() / self.scale  # Y is inverted
            
            # Deactivate drone tracking when manually moving
            if self.follow_drone and (delta.x() != 0 or delta.y() != 0):
                self.follow_drone = False
                self.follow_button.setText("Follow: Off")
            
            self.last_mouse_pos = event.position()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handles mouse release"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None
    
    def wheelEvent(self, event):
        """Handles mouse wheel for zoom"""
        zoom_factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
        self.scale *= zoom_factor
        self.update()
