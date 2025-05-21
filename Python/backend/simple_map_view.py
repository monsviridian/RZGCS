#!/usr/bin/env python
"""
Simple Map View für RZGCS - Garantiert funktionierendes Kartenmodul ohne externe Abhängigkeiten
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
    """Einfache Kartenansicht für die Integration in RZGCS
    
    Diese Klasse stellt eine basic 2D-Karte bereit, die keine WebEngine benötigt
    und in jeder Umgebung garantiert funktioniert.
    """
    
    # Signale für Interaktion mit anderen Komponenten
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
        
        # Kartenparameter
        self.center_lat = self.drone_lat
        self.center_lon = self.drone_lon
        self.scale = 100000  # Skalierungsfaktor (höhere Werte = mehr Zoom)
        self.follow_drone = True  # Automatische Verfolgung der Drohne
        
        # Layout für UI-Elemente
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Status-Label oben
        self.status_label = QLabel("RZGCS 2D-Karte - Aktiv")
        self.status_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: white; padding: 5px;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # Control-Panel unten
        control_panel = QWidget()
        control_panel.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: white; padding: 5px;"
        )
        control_layout = QHBoxLayout(control_panel)
        
        # Buttons für Kartensteuerung
        center_button = QPushButton("Zentrieren")
        center_button.clicked.connect(self.center_on_drone)
        control_layout.addWidget(center_button)
        
        self.follow_button = QPushButton("Verfolgen: Ein")
        self.follow_button.clicked.connect(self.toggle_follow)
        control_layout.addWidget(self.follow_button)
        
        self.path_button = QPushButton("Pfad: Ein")
        self.path_button.clicked.connect(self.toggle_path)
        control_layout.addWidget(self.path_button)
        
        layout.addWidget(control_panel)
        
        # Für Mausinteraktion
        self.setMouseTracking(True)
        self.last_mouse_pos = None
    
    def center_on_drone(self):
        """Zentriert die Karte auf die aktuelle Drohnenposition"""
        self.center_lat = self.drone_lat
        self.center_lon = self.drone_lon
        self.update()
    
    def toggle_follow(self):
        """Schaltet die automatische Verfolgung der Drohne ein/aus"""
        self.follow_drone = not self.follow_drone
        self.follow_button.setText(f"Verfolgen: {'Ein' if self.follow_drone else 'Aus'}")
        if self.follow_drone:
            self.center_on_drone()
        self.update()
    
    def toggle_path(self):
        """Schaltet die Anzeige des Flugpfads ein/aus"""
        self.show_path = not self.show_path
        self.path_button.setText(f"Pfad: {'Ein' if self.show_path else 'Aus'}")
        self.update()
    
    def update_drone_position(self, lat, lon, alt=None, heading=None, speed=None, battery=None):
        """Aktualisiert die Drohnenposition und andere Parameter
        
        Diese Methode wird von außen aufgerufen, um die Drohnendaten zu aktualisieren.
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
        
        # Zur Pfadhistorie hinzufügen
        self.path.append((lat, lon))
        if len(self.path) > self.max_path_length:
            self.path = self.path[-self.max_path_length:]
        
        # Wenn Verfolgung aktiviert ist, Karte auf Drohne zentrieren
        if self.follow_drone:
            self.center_lat = lat
            self.center_lon = lon
        
        # Karte neu zeichnen
        self.update()
    
    def clear_path(self):
        """Löscht den bisherigen Flugpfad"""
        self.path = []
        self.update()
    
    def geo_to_screen(self, lat, lon):
        """Konvertiert geografische in Bildschirmkoordinaten"""
        dx = (lon - self.center_lon) * self.scale
        dy = (lat - self.center_lat) * self.scale
        
        # Bildschirmkoordinaten (Ursprung in der Mitte)
        x = self.width() / 2 + dx
        y = self.height() / 2 - dy  # Invertiert, da y nach unten zunimmt
        
        return QPointF(x, y)
    
    def screen_to_geo(self, x, y):
        """Konvertiert Bildschirm- in geografische Koordinaten"""
        dx = x - self.width() / 2
        dy = self.height() / 2 - y  # Invertiert, da y nach unten zunimmt
        
        lon = self.center_lon + dx / self.scale
        lat = self.center_lat + dy / self.scale
        
        return lat, lon
    
    def paintEvent(self, event):
        """Zeichnet die Karte und Drohne"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Hintergrund - einfacher Farbverlauf (Himmel/Boden)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(135, 206, 250))  # Hellblau oben
        gradient.setColorAt(1, QColor(34, 139, 34))    # Grün unten
        painter.fillRect(self.rect(), gradient)
        
        # Gitter zeichnen
        self.draw_grid(painter)
        
        # Pfad zeichnen wenn aktiviert
        if self.show_path:
            self.draw_path(painter)
        
        # Drohne zeichnen
        self.draw_drone(painter)
        
        # Information anzeigen
        self.draw_info_panel(painter)
        
        # Kompass zeichnen
        self.draw_compass(painter)
    
    def draw_grid(self, painter):
        """Zeichnet ein einfaches Koordinatengitter"""
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
        
        # Grid-Abstand in geografischen Koordinaten
        grid_spacing = 0.001  # ca. 100m
        
        # Sichtbarer Bereich berechnen
        width_deg = self.width() / self.scale
        height_deg = self.height() / self.scale
        
        min_lon = self.center_lon - width_deg / 2
        max_lon = self.center_lon + width_deg / 2
        min_lat = self.center_lat - height_deg / 2
        max_lat = self.center_lat + height_deg / 2
        
        # Gridlinien abrunden/aufrunden für saubere Darstellung
        min_lon_grid = math.floor(min_lon / grid_spacing) * grid_spacing
        max_lon_grid = math.ceil(max_lon / grid_spacing) * grid_spacing
        min_lat_grid = math.floor(min_lat / grid_spacing) * grid_spacing
        max_lat_grid = math.ceil(max_lat / grid_spacing) * grid_spacing
        
        # Horizontale Linien
        lat = min_lat_grid
        while lat <= max_lat_grid:
            start = self.geo_to_screen(lat, min_lon_grid)
            end = self.geo_to_screen(lat, max_lon_grid)
            painter.drawLine(start, end)
            lat += grid_spacing
        
        # Vertikale Linien
        lon = min_lon_grid
        while lon <= max_lon_grid:
            start = self.geo_to_screen(min_lat_grid, lon)
            end = self.geo_to_screen(max_lat_grid, lon)
            painter.drawLine(start, end)
            lon += grid_spacing
    
    def draw_path(self, painter):
        """Zeichnet den Flugpfad der Drohne"""
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
        """Zeichnet die Drohne als Pfeil in Bewegungsrichtung"""
        drone_pos = self.geo_to_screen(self.drone_lat, self.drone_lon)
        
        # Drohne als farbiger Kreis mit Pfeil
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 200)))
        
        # Größe der Drohne, abhängig vom Zoom
        drone_size = 10
        
        painter.drawEllipse(drone_pos, drone_size, drone_size)
        
        # Pfeil für Heading
        rad_heading = math.radians(self.drone_heading)
        arrow_end = QPointF(
            drone_pos.x() + math.sin(rad_heading) * drone_size * 1.5,
            drone_pos.y() - math.cos(rad_heading) * drone_size * 1.5
        )
        
        painter.drawLine(drone_pos, arrow_end)
    
    def draw_info_panel(self, painter):
        """Zeigt Informationen zur Drohne an"""
        panel_width = 180
        panel_height = 140
        margin = 10
        
        # Panel in der linken unteren Ecke
        panel_rect = QRectF(
            margin, 
            self.height() - panel_height - margin,
            panel_width,
            panel_height
        )
        
        # Hintergrund mit Transparenz
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRect(panel_rect)
        
        # Text anzeigen
        painter.setPen(QPen(Qt.white))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        
        # Textpositionen berechnen
        text_x = panel_rect.left() + 10
        text_y = panel_rect.top() + 20
        line_height = 18
        
        # Drohneninformationen
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
        """Zeichnet einen einfachen Kompass"""
        compass_size = 60
        margin = 10
        compass_x = self.width() - compass_size - margin
        compass_y = margin + compass_size / 2
        
        # Kompass-Hintergrund
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawEllipse(QPointF(compass_x, compass_y), compass_size / 2, compass_size / 2)
        
        # Himmelsrichtungen
        painter.setPen(QPen(Qt.white, 1))
        
        directions = [("N", 0), ("O", 90), ("S", 180), ("W", 270)]
        for label, angle in directions:
            rad = math.radians(angle)
            dir_x = compass_x + math.sin(rad) * (compass_size / 2 - 15)
            dir_y = compass_y - math.cos(rad) * (compass_size / 2 - 15)
            
            painter.drawText(dir_x - 5, dir_y + 5, label)
        
        # Nordpfeil
        painter.setPen(QPen(Qt.red, 2))
        north_x = compass_x
        north_y = compass_y - compass_size / 3
        painter.drawLine(compass_x, compass_y, north_x, north_y)
        
        # Drohnenpfeil
        painter.setPen(QPen(QColor(50, 180, 255), 2))
        rad_heading = math.radians(self.drone_heading)
        drone_dir_x = compass_x + math.sin(rad_heading) * (compass_size / 3)
        drone_dir_y = compass_y - math.cos(rad_heading) * (compass_size / 3)
        painter.drawLine(compass_x, compass_y, drone_dir_x, drone_dir_y)
    
    def mousePressEvent(self, event):
        """Behandelt Mausklick-Ereignisse"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.position()
            
            # Wenn mit Shift geklickt wird, Position als Ziel auswählen
            if event.modifiers() & Qt.ShiftModifier:
                lat, lon = self.screen_to_geo(event.position().x(), event.position().y())
                alt = 50.0  # Default-Höhe für Ziele
                self.positionClicked.emit(lat, lon, alt)
    
    def mouseMoveEvent(self, event):
        """Behandelt Mausbewegungen für Kartenverschiebung"""
        if self.last_mouse_pos and event.buttons() & Qt.LeftButton:
            delta = event.position() - self.last_mouse_pos
            # Umrechnung von Pixel zu Koordinaten
            self.center_lon -= delta.x() / self.scale
            self.center_lat += delta.y() / self.scale  # Y ist invertiert
            
            # Deaktiviere Drohnenverfolgung bei manueller Bewegung
            if self.follow_drone and (delta.x() != 0 or delta.y() != 0):
                self.follow_drone = False
                self.follow_button.setText("Verfolgen: Aus")
            
            self.last_mouse_pos = event.position()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Behandelt Mausloslassen"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None
    
    def wheelEvent(self, event):
        """Behandelt Mausrad für Zoom"""
        zoom_factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
        self.scale *= zoom_factor
        self.update()
