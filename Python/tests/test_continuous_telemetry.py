#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfacher visueller Test für die kontinuierliche Telemetrie-Datenübertragung
"""

import os
import sys
import time
import random
from threading import Thread

# Pfad für die Importe hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Importiere die benötigten Module aus dem Projekt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtWidgets import QPushButton, QLabel, QCheckBox, QGroupBox, QGridLayout
from PySide6.QtCore import QTimer, Signal, Slot, QObject
from PySide6.QtGui import QColor

try:
    # Versuche das MissionPlannerStyle-Modul zu importieren
    from rzgcs.viewmodel.mission_planner_style import MissionPlannerStyle
except ImportError:
    print("FEHLER: MissionPlannerStyle konnte nicht importiert werden.")
    sys.exit(-1)


class TelemetryMonitor(QObject):
    """Überwacht die Telemetriedaten und gibt Statusupdates"""
    
    telemetry_received = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self._last_values = {}
        self._counter = 0
        self._receive_count = 0
        
    @Slot(dict)
    def on_telemetry_update(self, data):
        """Wird aufgerufen, wenn Telemetriedaten empfangen werden"""
        self._receive_count += 1
        self._last_values = data
        self.telemetry_received.emit(data)
        
    def get_receive_count(self):
        """Gibt die Anzahl der empfangenen Telemetrie-Updates zurück"""
        return self._receive_count
        
    def get_last_values(self):
        """Gibt die letzten empfangenen Telemetriedaten zurück"""
        return self._last_values


class TelemetryTestWindow(QMainWindow):
    """Einfaches Testfenster für die Telemetriedaten"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test: Kontinuierliche Telemetrie")
        self.resize(800, 600)
        
        # Mission Planner Style und Telemetrie-Monitor erstellen
        self.mission_planner = MissionPlannerStyle()
        self.monitor = TelemetryMonitor()
        
        # Verbinde das Telemetrie-Signal
        self.mission_planner.telemetryUpdated.connect(self.monitor.on_telemetry_update)
        self.monitor.telemetry_received.connect(self.update_display)
        
        # Hauptwidget und Layout erstellen
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Status-Layout
        self.status_group = QGroupBox("Verbindungsstatus")
        self.status_layout = QGridLayout()
        self.status_group.setLayout(self.status_layout)
        
        # Status-Labels
        self.connected_label = QLabel("Verbunden: Nein")
        self.armed_label = QLabel("Armed: Nein")
        self.mode_label = QLabel("Modus: -")
        self.updates_label = QLabel("Updates empfangen: 0")
        self.updates_armed_label = QLabel("Updates seit Arming: 0")
        self.status_layout.addWidget(self.connected_label, 0, 0)
        self.status_layout.addWidget(self.armed_label, 0, 1)
        self.status_layout.addWidget(self.mode_label, 1, 0)
        self.status_layout.addWidget(self.updates_label, 1, 1)
        self.status_layout.addWidget(self.updates_armed_label, 2, 0, 1, 2)
        
        self.main_layout.addWidget(self.status_group)
        
        # Telemetrie-Daten-Anzeige
        self.telemetry_group = QGroupBox("Telemetrie-Daten")
        self.telemetry_layout = QGridLayout()
        self.telemetry_group.setLayout(self.telemetry_layout)
        
        # Telemetriedaten-Labels
        self.roll_label = QLabel("Roll: -")
        self.pitch_label = QLabel("Pitch: -")
        self.yaw_label = QLabel("Yaw: -")
        self.altitude_label = QLabel("Höhe: -")
        self.airspeed_label = QLabel("Airspeed: -")
        self.groundspeed_label = QLabel("Groundspeed: -")
        self.battery_label = QLabel("Batterie: -")
        
        self.telemetry_layout.addWidget(self.roll_label, 0, 0)
        self.telemetry_layout.addWidget(self.pitch_label, 0, 1)
        self.telemetry_layout.addWidget(self.yaw_label, 0, 2)
        self.telemetry_layout.addWidget(self.altitude_label, 1, 0)
        self.telemetry_layout.addWidget(self.airspeed_label, 1, 1)
        self.telemetry_layout.addWidget(self.groundspeed_label, 1, 2)
        self.telemetry_layout.addWidget(self.battery_label, 2, 0, 1, 3)
        
        self.main_layout.addWidget(self.telemetry_group)
        
        # Hinweistext zur Neuimplementierung
        info_text = """
        <b>Test der kontinuierlichen Telemetrie-Datenübertragung</b><br>
        Dieser Test zeigt, dass Telemetriedaten auch im disarmed-Zustand<br>
        kontinuierlich gesendet werden. Die Neuerungen sind:<br>
        - Sensordaten werden immer aktualisiert, unabhängig vom Armed-Status<br>
        - Roll, Pitch und Yaw zeigen kleine Bewegungen auch im disarmed-Zustand<br>
        - Batterie und GPS-Daten werden immer übertragen<br>
        """
        self.info_label = QLabel(info_text)
        self.main_layout.addWidget(self.info_label)
        
        # Steuerungspanel
        self.control_group = QGroupBox("Steuerung")
        self.control_layout = QHBoxLayout()
        self.control_group.setLayout(self.control_layout)
        
        self.connect_button = QPushButton("Verbinden")
        self.disconnect_button = QPushButton("Trennen")
        self.arm_button = QPushButton("ARM")
        self.disarm_button = QPushButton("DISARM")
        
        self.connect_button.clicked.connect(self.connect_drone)
        self.disconnect_button.clicked.connect(self.disconnect_drone)
        self.arm_button.clicked.connect(self.arm_drone)
        self.disarm_button.clicked.connect(self.disarm_drone)
        
        self.control_layout.addWidget(self.connect_button)
        self.control_layout.addWidget(self.disconnect_button)
        self.control_layout.addWidget(self.arm_button)
        self.control_layout.addWidget(self.disarm_button)
        
        self.main_layout.addWidget(self.control_group)
        
        # Statistik und Hilfsvariablen
        self.updates_count = 0
        self.armed_updates_count = 0
        self.armed_time = None
        
        # Timer für UI-Updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.refresh_ui)
        self.update_timer.start(500)  # alle 500ms UI aktualisieren
    
    def connect_drone(self):
        """Verbindung zum simulierten Drone herstellen"""
        try:
            # UDP SITL-Verbindung herstellen
            self.mission_planner.connect("udp://:14550")
            self.connected_label.setText("Verbunden: Ja")
            self.connected_label.setStyleSheet("color: green; font-weight: bold")
            print("Verbindung hergestellt")
        except Exception as e:
            print(f"Fehler bei der Verbindung: {e}")
    
    def disconnect_drone(self):
        """Verbindung trennen"""
        try:
            self.mission_planner.disconnect()
            self.connected_label.setText("Verbunden: Nein")
            self.connected_label.setStyleSheet("color: black")
            self.armed_label.setText("Armed: Nein")
            self.armed_label.setStyleSheet("color: black")
            print("Verbindung getrennt")
        except Exception as e:
            print(f"Fehler beim Trennen: {e}")
    
    def arm_drone(self):
        """Drone armieren"""
        try:
            self.mission_planner.arm()
            self.armed_label.setText("Armed: Ja")
            self.armed_label.setStyleSheet("color: red; font-weight: bold")
            self.armed_time = time.time()
            self.armed_updates_count = 0
            print("Drone armiert")
        except Exception as e:
            print(f"Fehler beim Armieren: {e}")
    
    def disarm_drone(self):
        """Drone disarmieren"""
        try:
            self.mission_planner.disarm()
            self.armed_label.setText("Armed: Nein")
            self.armed_label.setStyleSheet("color: black")
            self.armed_time = None
            print("Drone disarmiert")
        except Exception as e:
            print(f"Fehler beim Disarmieren: {e}")
    
    @Slot(dict)
    def update_display(self, data):
        """Aktualisiert die Anzeige mit den empfangenen Telemetriedaten"""
        self.updates_count += 1
        
        if self.armed_time is not None:
            self.armed_updates_count += 1
        
        # Aktualisiere die Telemetriedaten-Labels
        try:
            if 'roll' in data:
                self.roll_label.setText(f"Roll: {data['roll']:.1f}°")
            if 'pitch' in data:
                self.pitch_label.setText(f"Pitch: {data['pitch']:.1f}°")
            if 'yaw' in data:
                self.yaw_label.setText(f"Yaw: {data['yaw']:.1f}°")
            if 'relative_alt' in data:
                self.altitude_label.setText(f"Höhe: {data['relative_alt']:.1f}m")
            if 'airspeed' in data:
                self.airspeed_label.setText(f"Airspeed: {data['airspeed']:.1f}m/s")
            if 'groundspeed' in data:
                self.groundspeed_label.setText(f"Groundspeed: {data['groundspeed']:.1f}m/s")
            if 'battery' in data:
                self.battery_label.setText(f"Batterie: {data['battery']:.1f}%")
        except (KeyError, TypeError) as e:
            print(f"Fehler beim Verarbeiten der Telemetriedaten: {e}")
    
    def refresh_ui(self):
        """Aktualisiert die UI-Elemente"""
        self.updates_label.setText(f"Updates empfangen: {self.updates_count}")
        self.updates_armed_label.setText(f"Updates seit Arming: {self.armed_updates_count}")
        
        # Aktualisiere Modusanzeige
        try:
            self.mode_label.setText(f"Modus: {self.mission_planner.mode}")
        except:
            pass
    
    def closeEvent(self, event):
        """Wird beim Schließen des Fensters aufgerufen"""
        try:
            # Verbindung trennen und Timer stoppen
            self.disconnect_drone()
            self.update_timer.stop()
        except:
            pass
        event.accept()


def main():
    """Hauptfunktion zum Starten des Tests"""
    app = QApplication(sys.argv)
    window = TelemetryTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
