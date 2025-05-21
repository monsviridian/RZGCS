#!/usr/bin/env python
"""
Ultra-Simple 2D Map für RZGCS - Garantiert kompatibel mit allen Umgebungen
"""

import sys
import os
import math
import json
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QPointF, QRectF
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGridLayout)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
                          QLinearGradient, QPalette, QPolygonF)


class SimpleMapWidget(QWidget):
    """Einfache 2D-Karte ohne komplexe Abhängigkeiten"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        
        # Default Drohnenposition (Dortmund)
        self.drone_lat = 51.505600
        self.drone_lon = 7.452400
        self.drone_alt = 100.0
        self.drone_heading = 0.0
        self.drone_speed = 0.0
        self.drone_battery = 100.0
        
        # Pfad der Drohne
        self.path = []
        self.max_path_length = 100
        
        # Kartenparameter
        self.center_lat = self.drone_lat
        self.center_lon = self.drone_lon
        self.scale = 100000  # Skalierungsfaktor (höhere Werte = mehr Zoom)
        
        # Simulationsparameter
        self.sim_angle = 0.0
        self.simulation_timer = QTimer(self)
        self.simulation_timer.timeout.connect(self.simulate_drone)
        self.simulation_timer.start(100)  # 10 FPS
        
        # Layout für Statusinformationen
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Status-Label im oberen Bereich
        self.status_label = QLabel("RZGCS Karte - Aktiv")
        self.status_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: white; padding: 5px;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # Hinweis zur Navigation
        info_label = QLabel("Drag & Drop für Verschieben, Mausrad für Zoom")
        info_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 150); color: white; padding: 5px;"
        )
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        self.setMouseTracking(True)
        self.last_mouse_pos = None
    
    def update_drone(self, lat, lon, alt=None, heading=None, speed=None, battery=None):
        """Aktualisiert die Drohnenposition und andere Parameter"""
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
        
        # Karte neu zeichnen
        self.update()
    
    def simulate_drone(self):
        """Simuliert eine Drohnenbewegung für Test- und Demozwecke"""
        self.sim_angle = (self.sim_angle + 2) % 360
        rad = math.radians(self.sim_angle)
        
        # Kreisförmige Bewegung um Zentrum
        center_lat = 51.505600
        center_lon = 7.452400
        radius = 0.001  # ca. 100m
        
        lat = center_lat + radius * math.sin(rad)
        lon = center_lon + radius * math.cos(rad)
        alt = 100 + 50 * math.sin(rad * 2)  # Höhe variiert
        speed = 10 + 5 * math.sin(rad * 3)  # Geschwindigkeit variiert
        battery = max(0, 100 - self.sim_angle / 10)  # Batterie sinkt langsam
        
        self.update_drone(lat, lon, alt, self.sim_angle, speed, battery)
    
    def geo_to_screen(self, lat, lon):
        """Konvertiert geografische in Bildschirmkoordinaten"""
        dx = (lon - self.center_lon) * self.scale
        dy = (lat - self.center_lat) * self.scale
        
        # Bildschirmkoordinaten (Ursprung in der Mitte)
        x = self.width() / 2 + dx
        y = self.height() / 2 - dy  # Invertiert, da y nach unten zunimmt
        
        return QPointF(x, y)
    
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
        
        # Pfad zeichnen
        self.draw_path(painter)
        
        # Drohne zeichnen
        self.draw_drone(painter)
        
        # Information anzeigen
        self.draw_info_panel(painter)
    
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
            f"Heading: {int(self.drone_heading)}°",
            f"Speed: {self.drone_speed:.1f} m/s",
            f"Battery: {int(self.drone_battery)}%",
        ]
        
        for i, line in enumerate(info_lines):
            painter.drawText(text_x, text_y + i * line_height, line)
    
    def mousePressEvent(self, event):
        """Behandelt Mausklick-Ereignisse"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.position()
    
    def mouseMoveEvent(self, event):
        """Behandelt Mausbewegungen für Kartenverschiebung"""
        if self.last_mouse_pos and event.buttons() & Qt.LeftButton:
            delta = event.position() - self.last_mouse_pos
            # Umrechnung von Pixel zu Koordinaten
            self.center_lon -= delta.x() / self.scale
            self.center_lat += delta.y() / self.scale  # Y ist invertiert
            
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


class SimpleMapWindow(QMainWindow):
    """Hauptfenster für die eigenständige Kartenanwendung"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RZGCS Simple Map - 100% kompatibel")
        self.resize(800, 600)
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Haupt-Layout
        main_layout = QVBoxLayout(central_widget)
        
        # Map-Widget
        self.map_widget = SimpleMapWidget()
        main_layout.addWidget(self.map_widget)
        
        # Steuerungsbereich
        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)
        
        # Buttons
        reset_button = QPushButton("Karte zentrieren")
        reset_button.clicked.connect(self.reset_map)
        controls_layout.addWidget(reset_button)
        
        # Status-Bereich in der Statusleiste
        self.statusBar().showMessage("Karte bereit - Simulation aktiv")
    
    def reset_map(self):
        """Zentriert die Karte auf die Drohnenposition"""
        self.map_widget.center_lat = self.map_widget.drone_lat
        self.map_widget.center_lon = self.map_widget.drone_lon
        self.map_widget.scale = 100000  # Standardzoom
        self.map_widget.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style anpassen für bessere Lesbarkeit
    app.setStyle("Fusion")
    
    window = SimpleMapWindow()
    window.show()
    
    print("Einfache Karte gestartet - 100% kompatibel mit allen Umgebungen")
    print("Drohne wird in einer Kreisbewegung simuliert")
    print("Steuerung: Linke Maustaste zum Verschieben, Mausrad zum Zoomen")
    
    sys.exit(app.exec())
