#!/usr/bin/env python
"""
Native 3D Karte für RZGCS - Keine WebEngine-Abhängigkeit
"""

import sys
import os
import math
import socket
import json
import threading
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, Slot, QObject
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QSlider, QGroupBox)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
                         QLinearGradient, QTransform, QPalette, QPolygon)


class DroneData:
    """Datenklasse für die Drohneninformationen"""
    def __init__(self):
        self.lat = 51.505600
        self.lon = 7.452400
        self.alt = 100.0
        self.heading = 0.0
        self.speed = 0.0
        self.battery = 100.0
        self.path = []
        # Maximale Pfadlänge
        self.max_path_length = 1000
        
    def update_position(self, lat, lon, alt, heading=None, speed=None, battery=None):
        """Aktualisiert die Position der Drohne und fügt sie zum Pfad hinzu"""
        self.lat = lat
        self.lon = lon
        self.alt = alt
        if heading is not None:
            self.heading = heading
        if speed is not None:
            self.speed = speed
        if battery is not None:
            self.battery = battery
            
        # Position zum Pfad hinzufügen
        self.path.append((lat, lon, alt))
        # Pfad beschränken
        if len(self.path) > self.max_path_length:
            self.path = self.path[-self.max_path_length:]
            

class MapView(QWidget):
    """Widget zur Darstellung der 3D-Karte"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drone = DroneData()
        self.center_lat = self.drone.lat
        self.center_lon = self.drone.lon
        self.scale = 80000  # Skalierungsfaktor für die Kartenansicht
        self.zoom = 1.0
        self.pitch = 30.0  # Neigungswinkel in Grad (0=Draufsicht, 90=horizontale Ansicht)
        self.heading = 0.0  # Kamerarichtung in Grad
        self.follow_drone = True
        self.show_grid = True
        self.grid_spacing = 0.001  # ca. 100m Rasterabstand
        self.show_path = True
        self.path_color = QColor(255, 255, 0, 150)
        
        # Letzte Mausposition für Drag-Operationen
        self.last_mouse_pos = None
        
        # Setze Eigenschaften für besseres Rendering
        self.setMinimumSize(600, 400)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Timer für Animation
        self.simulation_active = False
        self.sim_angle = 0.0
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.simulate_drone)
        
    def initiate_simulation(self):
        """Startet eine Simulation für Testzwecke"""
        self.simulation_active = True
        self.timer.start()
        
    def stop_simulation(self):
        """Stoppt die Simulation"""
        self.simulation_active = False
        self.timer.stop()
        
    def simulate_drone(self):
        """Simuliert eine Drohnenbewegung für Testzwecke"""
        if not self.simulation_active:
            return
            
        self.sim_angle = (self.sim_angle + 2) % 360
        radius = 0.001  # ca. 100m Radius
        center_lat = 51.505600
        center_lon = 7.452400
        
        # Kreisförmige Bewegung
        rad = math.radians(self.sim_angle)
        new_lat = center_lat + radius * math.sin(rad)
        new_lon = center_lon + radius * math.cos(rad)
        new_alt = 100.0 + 50.0 * math.sin(rad * 2)
        
        # Drohne auf Kreisbahn bewegen und in Bewegungsrichtung ausrichten
        self.drone.update_position(
            new_lat, 
            new_lon, 
            new_alt, 
            heading=(self.sim_angle + 90) % 360,
            speed=10.0 + 5.0 * math.sin(rad * 3),
            battery=max(0.0, 100.0 - self.sim_angle / 10.0)
        )
        self.update()
        
    def geo_to_screen(self, lat, lon, alt):
        """Konvertiert geografische in Bildschirmkoordinaten"""
        # Mittelpunkt
        center_lat = self.drone.lat if self.follow_drone else self.center_lat
        center_lon = self.drone.lon if self.follow_drone else self.center_lon
        
        # Berechne relative Position in Metern
        x = (lon - center_lon) * self.scale * self.zoom
        y = (lat - center_lat) * self.scale * self.zoom
        z = alt
        
        # Rotation um z-Achse (Heading)
        rad_heading = math.radians(-self.heading)
        x_rot = x * math.cos(rad_heading) - y * math.sin(rad_heading)
        y_rot = x * math.sin(rad_heading) + y * math.cos(rad_heading)
        
        # Rotation um x-Achse (Pitch)
        rad_pitch = math.radians(self.pitch)
        y_rot2 = y_rot * math.cos(rad_pitch) - z * math.sin(rad_pitch)
        z_rot = y_rot * math.sin(rad_pitch) + z * math.cos(rad_pitch)
        
        # Perspektivischer Effekt
        perspective = 1000
        scale_factor = perspective / (perspective + z_rot)
        screen_x = self.width() / 2 + x_rot * scale_factor
        screen_y = self.height() / 2 - y_rot2 * scale_factor
        
        return QPoint(int(screen_x), int(screen_y)), z_rot
        
    def draw_grid(self, painter):
        """Zeichnet ein Koordinatengitter auf die Karte"""
        if not self.show_grid:
            return
            
        center_lat = self.drone.lat if self.follow_drone else self.center_lat
        center_lon = self.drone.lon if self.follow_drone else self.center_lon
        
        # Gitterparameter
        grid_extent = 0.02  # ca. 2km Ausdehnung
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
        
        # Horizontale Linien
        for lat in [center_lat + self.grid_spacing * i for i in range(-20, 21)]:
            points = []
            for lon in [center_lon + self.grid_spacing * i / 5 for i in range(-100, 101)]:
                screen_point, z = self.geo_to_screen(lat, lon, 0)
                # Nur zeichnen, wenn der Punkt sichtbar ist (über dem Horizont)
                if z < 0:
                    continue
                points.append(screen_point)
            
            if len(points) > 1:
                for i in range(len(points) - 1):
                    painter.drawLine(points[i], points[i + 1])
        
        # Vertikale Linien
        for lon in [center_lon + self.grid_spacing * i for i in range(-20, 21)]:
            points = []
            for lat in [center_lat + self.grid_spacing * i / 5 for i in range(-100, 101)]:
                screen_point, z = self.geo_to_screen(lat, lon, 0)
                # Nur zeichnen, wenn der Punkt sichtbar ist
                if z < 0:
                    continue
                points.append(screen_point)
            
            if len(points) > 1:
                for i in range(len(points) - 1):
                    painter.drawLine(points[i], points[i + 1])
    
    def draw_drone(self, painter):
        """Zeichnet die Drohne und ihren Schatten"""
        # Drohnenposition
        drone_point, drone_z = self.geo_to_screen(self.drone.lat, self.drone.lon, self.drone.alt)
        shadow_point, _ = self.geo_to_screen(self.drone.lat, self.drone.lon, 0)
        
        if drone_z < 0:  # Drohne befindet sich hinter der Kamera
            return
        
        # Schatten zeichnen
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.drawEllipse(shadow_point, 8, 4)
        
        # Verbindungslinie zum Boden
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1, Qt.DotLine))
        painter.drawLine(drone_point, shadow_point)
        
        # Drohne zeichnen
        drone_size = 10
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QBrush(QColor(255, 50, 50)))
        painter.drawEllipse(drone_point, drone_size, drone_size)
        
        # Richtungspfeil
        rad_heading = math.radians(self.drone.heading)
        arrow_end = QPoint(
            drone_point.x() + int(math.sin(rad_heading) * drone_size * 1.5),
            drone_point.y() - int(math.cos(rad_heading) * drone_size * 1.5)
        )
        painter.drawLine(drone_point, arrow_end)
    
    def draw_path(self, painter):
        """Zeichnet den Flugpfad der Drohne"""
        if not self.show_path or len(self.drone.path) < 2:
            return
            
        painter.setPen(QPen(self.path_color, 2))
        
        path_points = []
        for lat, lon, alt in self.drone.path:
            screen_point, z = self.geo_to_screen(lat, lon, alt)
            if z < 0:  # Punkt ist hinter der Kamera
                continue
            path_points.append(screen_point)
        
        if len(path_points) < 2:
            return
            
        for i in range(len(path_points) - 1):
            painter.drawLine(path_points[i], path_points[i + 1])
    
    def draw_info_panel(self, painter):
        """Zeichnet ein Infopanel mit Drohnendaten"""
        panel_width = 200
        panel_height = 120
        panel_x = 10
        panel_y = 10
        
        # Panel-Hintergrund
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRect(panel_x, panel_y, panel_width, panel_height)
        
        # Text-Einstellungen
        painter.setPen(QPen(Qt.white))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        
        # Informationen anzeigen
        lines = [
            f"Lat: {self.drone.lat:.6f}",
            f"Lon: {self.drone.lon:.6f}",
            f"Alt: {self.drone.alt:.1f} m",
            f"Heading: {self.drone.heading:.1f}°",
            f"Speed: {self.drone.speed:.1f} m/s",
            f"Battery: {self.drone.battery:.0f}%"
        ]
        
        for i, line in enumerate(lines):
            painter.drawText(panel_x + 10, panel_y + 20 + i * 16, line)
    
    def draw_compass(self, painter):
        """Zeichnet einen Kompass"""
        compass_radius = 40
        compass_x = self.width() - compass_radius - 20
        compass_y = compass_radius + 20
        
        # Kompass-Hintergrund
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawEllipse(QPoint(compass_x, compass_y), compass_radius, compass_radius)
        
        # Hauptrichtungen
        painter.setPen(QPen(Qt.white, 2))
        directions = [("N", 0), ("O", 90), ("S", 180), ("W", 270)]
        
        for label, angle in directions:
            # Berücksichtige aktuelle Kartenausrichtung
            adjusted_angle = angle - self.heading
            rad = math.radians(adjusted_angle)
            text_x = compass_x + int(math.sin(rad) * (compass_radius - 15))
            text_y = compass_y - int(math.cos(rad) * (compass_radius - 15))
            
            font = painter.font()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            
            # Text zentrieren
            text_rect = painter.fontMetrics().boundingRect(label)
            painter.drawText(
                text_x - text_rect.width() / 2,
                text_y + text_rect.height() / 2,
                label
            )
        
        # Nordpfeil zeichnen
        painter.setPen(QPen(Qt.red, 2))
        north_angle = -self.heading  # Nordrichtung relativ zur Kameraausrichtung
        rad_north = math.radians(north_angle)
        north_end = QPoint(
            compass_x + int(math.sin(rad_north) * compass_radius * 0.7),
            compass_y - int(math.cos(rad_north) * compass_radius * 0.7)
        )
        painter.drawLine(QPoint(compass_x, compass_y), north_end)
        
        # Drohnenausrichtung
        painter.setPen(QPen(QColor(50, 180, 255), 2))
        drone_angle = self.drone.heading - self.heading
        rad_drone = math.radians(drone_angle)
        drone_end = QPoint(
            compass_x + int(math.sin(rad_drone) * compass_radius * 0.6),
            compass_y - int(math.cos(rad_drone) * compass_radius * 0.6)
        )
        painter.drawLine(QPoint(compass_x, compass_y), drone_end)
    
    def paintEvent(self, event):
        """Zeichnet die Kartenansicht"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        
        # Hintergrund (Himmel-Gradient)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(100, 181, 246))  # Himmelblau oben
        gradient.setColorAt(0.7, QColor(144, 202, 249))  # Hellblau Horizont
        gradient.setColorAt(1, QColor(0, 121, 107))  # Grün unten (Boden)
        painter.fillRect(self.rect(), gradient)
        
        # Karte zeichnen
        self.draw_grid(painter)
        self.draw_path(painter)
        self.draw_drone(painter)
        
        # Überlagerungen
        self.draw_info_panel(painter)
        self.draw_compass(painter)
    
    def mousePressEvent(self, event):
        """Behandelt Mausklick-Ereignisse"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.position().toPoint()
    
    def mouseMoveEvent(self, event):
        """Behandelt Mausbewegungen für die Kamerasteuerung"""
        if self.last_mouse_pos is not None and event.buttons() & Qt.LeftButton:
            delta = event.position().toPoint() - self.last_mouse_pos
            self.heading = (self.heading - delta.x() * 0.5) % 360
            self.pitch = max(0, min(90, self.pitch + delta.y() * 0.5))
            self.last_mouse_pos = event.position().toPoint()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Behandelt Mausloslassen"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None
    
    def wheelEvent(self, event):
        """Behandelt Mausrad-Ereignisse für Zoom"""
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.zoom = max(0.1, min(10.0, self.zoom * zoom_factor))
        self.update()
    
    def keyPressEvent(self, event):
        """Behandelt Tastatureingaben"""
        if event.key() == Qt.Key_F:
            # F-Taste wechselt den Drohnen-Verfolgungsmodus
            self.follow_drone = not self.follow_drone
            self.update()
        elif event.key() == Qt.Key_G:
            # G-Taste blendet das Gitter ein/aus
            self.show_grid = not self.show_grid
            self.update()
        elif event.key() == Qt.Key_P:
            # P-Taste blendet den Pfad ein/aus
            self.show_path = not self.show_path
            self.update()
        elif event.key() == Qt.Key_R:
            # R-Taste setzt die Ansicht zurück
            self.reset_view()
        elif event.key() == Qt.Key_T:
            # T-Taste schaltet Draufsicht ein
            self.set_top_view()

    def reset_view(self):
        """Setzt die Kartenansicht zurück"""
        self.pitch = 30.0
        self.heading = 0.0
        self.zoom = 1.0
        self.update()
        
    def set_top_view(self):
        """Stellt die Karte auf Draufsicht ein"""
        self.pitch = 0.0
        self.heading = 0.0
        self.update()


class MapServerThread(threading.Thread):
    """Socket-Server zum Empfangen von Positionsdaten"""
    def __init__(self, map_view, host='127.0.0.1', port=65432):
        super().__init__(daemon=True)
        self.map_view = map_view
        self.host = host
        self.port = port
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(0.5)  # Timeout für nicht-blockierendes Verhalten
        print(f"Socket-Server gestartet auf {self.host}:{self.port}")
    
    def run(self):
        """Hauptschleife des Servers"""
        while self.running:
            try:
                data, _ = self.socket.recvfrom(1024)
                self._process_data(data)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Fehler im Socket-Server: {str(e)}")
    
    def _process_data(self, data):
        """Verarbeitet empfangene Daten"""
        try:
            message = json.loads(data.decode('utf-8'))
            if message['type'] == 'position':
                lat = message.get('lat')
                lon = message.get('lon')
                alt = message.get('alt')
                heading = message.get('heading')
                speed = message.get('speed')
                battery = message.get('battery')
                
                if None not in [lat, lon, alt]:
                    # Aktualisiere die Drohnenposition im UI-Thread
                    QApplication.instance().postEvent(
                        self.map_view,
                        UpdateDroneEvent(lat, lon, alt, heading, speed, battery)
                    )
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Nachricht: {str(e)}")
    
    def stop(self):
        """Stoppt den Server"""
        self.running = False


class UpdateDroneEvent(QObject):
    """Event für Thread-sichere Aktualisierung der Drohnenposition"""
    def __init__(self, lat, lon, alt, heading=None, speed=None, battery=None):
        super().__init__()
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.heading = heading
        self.speed = speed
        self.battery = battery


class MapWindow(QMainWindow):
    """Hauptfenster für die eigenständige Kartenanwendung"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RZGCS 3D-Karte (Native)")
        self.resize(1024, 768)
        
        # Zentrale Widget und Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Kartenansicht erstellen
        self.map_view = MapView()
        main_layout.addWidget(self.map_view)
        
        # Steuerelemente
        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)
        
        # Buttons
        self.follow_button = QPushButton("Drohne folgen")
        self.follow_button.clicked.connect(self._toggle_follow)
        controls_layout.addWidget(self.follow_button)
        
        self.top_view_button = QPushButton("Draufsicht")
        self.top_view_button.clicked.connect(self.map_view.set_top_view)
        controls_layout.addWidget(self.top_view_button)
        
        self.reset_button = QPushButton("Ansicht zurücksetzen")
        self.reset_button.clicked.connect(self.map_view.reset_view)
        controls_layout.addWidget(self.reset_button)
        
        controls_layout.addStretch(1)
        
        # Status-Label
        self.status_label = QLabel("Status: Bereit")
        controls_layout.addWidget(self.status_label)
        
        # Socket-Server starten
        self.server = MapServerThread(self.map_view)
        self.server.start()
        
        # Simulation starten für Stand-Alone-Modus
        print("Starte Demo-Simulation für die 3D-Karte...")
        self.map_view.initiate_simulation()
        
        # Statusbar aktualisieren
        self.statusBar().showMessage("Karte geladen. Verwende die Maus zum Navigieren.")
    
    def _toggle_follow(self):
        """Schaltet den Drohnen-Verfolgungsmodus um"""
        self.map_view.follow_drone = not self.map_view.follow_drone
        self.follow_button.setText(
            "Kamera fixieren" if self.map_view.follow_drone else "Drohne folgen"
        )
        self.map_view.update()
    
    def closeEvent(self, event):
        """Behandelt das Schließen des Fensters"""
        print("Beende Socket-Server...")
        self.server.stop()
        self.map_view.stop_simulation()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style anpassen
    app.setStyle("Fusion")
    
    # Dunkles Thema
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    # Starte Anwendung
    window = MapWindow()
    window.show()
    
    sys.exit(app.exec())
