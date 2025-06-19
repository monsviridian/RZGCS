#!/usr/bin/env python3
"""
COM Port Connection GUI
Eine einfache GUI-Anwendung für die Verbindung zur Drohne über COM-Port
"""

import os
import sys
import time
import asyncio
import threading
from pathlib import Path

# Project paths setup
project_root = str(Path(__file__).resolve().parent.parent)
python_dir = os.path.join(project_root, "Python")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

# Set up PySide6 style
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# Now import PySide6
import PySide6
from PySide6.QtCore import QObject, Signal, Slot, Property, Qt
from PySide6.QtGui import QGuiApplication, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QTextEdit, QLineEdit, QMessageBox,
    QFormLayout, QGroupBox
)
from PySide6.QtQuickControls2 import QQuickStyle

# Import required modules
from mavsdk import System
from backend.logger import Logger


class DroneConnectionHelper(QObject):
    """
    Helper-Klasse für die Verbindung zur Drohne via COM-Port
    """
    # Signals
    connectionStateChanged = Signal(bool)
    portsRefreshed = Signal(list)
    logMessage = Signal(str)
    telemetryUpdated = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ports = []
        self._selected_port = ""
        self._drone = System()
        self._is_connected = False
        self._stop_event = threading.Event()
    
    @Slot()
    def refreshPorts(self):
        """Aktualisiert die Liste der verfügbaren COM-Ports"""
        try:
            import serial.tools.list_ports
            self._ports = [port.device for port in serial.tools.list_ports.comports()]
            self.logMessage.emit(f"[INFO] {len(self._ports)} COM-Port(s) gefunden")
            self.portsRefreshed.emit(self._ports)
            return self._ports
        except Exception as e:
            self.logMessage.emit(f"[FEHLER] Konnte Ports nicht laden: {e}")
            self._ports = []
            return []
    
    @Slot(str)
    def setPort(self, port_name):
        """Setzt den ausgewählten COM-Port"""
        self._selected_port = port_name
        self.logMessage.emit(f"[INFO] Port ausgewählt: {port_name}")
    
    @Property(bool, notify=connectionStateChanged)
    def connected(self):
        """Gibt zurück, ob die Drohne verbunden ist"""
        return self._is_connected
    
    @Slot(str)
    def connectToDrone(self, connection_string=""):
        """
        Verbindet zur Drohne über den angegebenen Verbindungsstring
        
        :param connection_string: z.B. "COM3:115200" oder nur "COM3"
        """
        # Verwende ausgewählten Port, wenn kein Verbindungsstring angegeben
        if not connection_string and self._selected_port:
            connection_string = self._selected_port
        
        if not connection_string:
            self.logMessage.emit("[FEHLER] Kein Verbindungsstring oder Port angegeben")
            return
        
        self.logMessage.emit(f"[INFO] Verbinde mit: {connection_string}")
        
        # Verbindungsstring verarbeiten
        connection_url = connection_string
        baudrate = 57600  # Standardwert
        
        # COM-Port mit Baudrate (z.B. "COM3:115200")
        if ":" in connection_string and not connection_string.startswith(("udp:", "tcp:")):
            try:
                port, baudrate_str = connection_string.split(":", 1)
                baudrate = int(baudrate_str)
                # Format für MAVSDK: serial:///COM3:115200
                connection_url = f"serial:///{port}:{baudrate}"
            except (ValueError, TypeError):
                # Bei ungültigem Format Original-String verwenden
                connection_url = f"serial:///{connection_string}"
        
        # COM-Port ohne Baudrate (einfach nur "COM3")
        elif connection_string.startswith("COM"):
            connection_url = f"serial:///{connection_string}:{baudrate}"
        
        # Verbindung herstellen
        self.logMessage.emit(f"[INFO] Verbindungs-URL: {connection_url}")
        
        # Verbindung in einem separaten Thread herstellen
        threading.Thread(target=self._connect_async, args=(connection_url,), daemon=True).start()
    
    def _connect_async(self, connection_url):
        """
        Asynchrone Verbindung zur Drohne
        
        :param connection_url: Vollständige Verbindungs-URL (z.B. "serial:///COM3:115200")
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Verbindung herstellen
            loop.run_until_complete(self._connect_drone(connection_url))
        except Exception as e:
            self.logMessage.emit(f"[FEHLER] Verbindungsfehler: {e}")
            self._is_connected = False
            self.connectionStateChanged.emit(False)
        finally:
            loop.close()
    
    async def _connect_drone(self, connection_url):
        """
        Stellt die Verbindung zur Drohne her und wartet auf Verbindungsaufbau
        
        :param connection_url: Vollständige Verbindungs-URL
        """
        # Verbindung herstellen
        await self._drone.connect(connection_url)
        
        # Auf Verbindung warten
        timeout_seconds = 30
        start_time = time.time()
        
        while not self._drone.is_connected:
            if time.time() - start_time > timeout_seconds:
                self.logMessage.emit(f"[FEHLER] Timeout bei Verbindungsaufbau zu {connection_url}")
                self._is_connected = False
                self.connectionStateChanged.emit(False)
                return
            
            await asyncio.sleep(0.1)
        
        # Verbindung hergestellt
        self._is_connected = True
        self.connectionStateChanged.emit(True)
        self.logMessage.emit("[INFO] Verbindung zur Drohne hergestellt")
        
        # Telemetrie abonnieren und überwachen
        await self._subscribe_telemetry()
        await self._monitor_telemetry()
    
    async def _subscribe_telemetry(self):
        """Abonniert Telemetrie-Daten von der Drohne"""
        if self._is_connected:
            try:
                # Minimale Telemetrie-Subscriptions
                await self._drone.telemetry.armed_subscribe(lambda armed: None)
                await self._drone.telemetry.flight_mode_subscribe(lambda mode: None)
                await self._drone.telemetry.position_subscribe(lambda pos: None)
                await self._drone.telemetry.battery_subscribe(lambda bat: None)
                
                self.logMessage.emit("[INFO] Telemetrie-Subscriptions erfolgreich")
            except Exception as e:
                self.logMessage.emit(f"[FEHLER] Telemetrie-Subscription fehlgeschlagen: {e}")
    
    async def _monitor_telemetry(self):
        """Überwacht Telemetrie-Daten von der Drohne"""
        while self._is_connected and not self._stop_event.is_set():
            try:
                # Minimale Telemetrie-Abfrage
                armed = await self._drone.telemetry.armed()
                flight_mode = await self._drone.telemetry.flight_mode()
                battery = await self._drone.telemetry.battery()
                position = await self._drone.telemetry.position()
                
                # Telemetrie-Update senden
                telemetry = {
                    "armed": armed,
                    "flight_mode": str(flight_mode),
                    "battery_percent": battery.remaining_percent,
                    "battery_voltage": battery.voltage_v,
                    "latitude": position.latitude_deg,
                    "longitude": position.longitude_deg,
                    "altitude": position.absolute_altitude_m,
                    "relative_altitude": position.relative_altitude_m
                }
                self.telemetryUpdated.emit(telemetry)
                
                # Log wichtige Änderungen
                self.logMessage.emit(f"[INFO] Drohnenstatus: Armed={armed}, Mode={flight_mode}, Batterie={battery.remaining_percent:.1f}%")
                
                # Kurze Pause
                await asyncio.sleep(2.0)
            except Exception as e:
                self.logMessage.emit(f"[FEHLER] Telemetrie-Fehler: {e}")
                await asyncio.sleep(1.0)
    
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung zur Drohne"""
        if self._is_connected:
            self._stop_event.set()
            self._is_connected = False
            self.connectionStateChanged.emit(False)
            self.logMessage.emit("[INFO] Verbindung zur Drohne getrennt")


class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        super().__init__()
        
        # Fenstertitel und -größe
        self.setWindowTitle("RZGCS COM-Port-Verbindung")
        self.resize(800, 600)
        
        # Logger und Connection-Helper
        self.logger = Logger()
        self.connection_helper = DroneConnectionHelper()
        
        # Logger mit Helper verbinden
        self.connection_helper.logMessage.connect(self.add_log)
        self.connection_helper.connectionStateChanged.connect(self.update_connection_status)
        self.connection_helper.telemetryUpdated.connect(self.update_telemetry)
        
        # UI erstellen
        self.init_ui()
        
        # COM-Ports laden
        self.refresh_ports()
    
    def init_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Hauptlayout
        main_layout = QVBoxLayout(central_widget)
        
        # Verbindungsbereich
        connection_group = QGroupBox("Verbindung")
        connection_layout = QFormLayout(connection_group)
        
        # Port-Auswahl
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        self.refresh_button = QPushButton("Aktualisieren")
        self.refresh_button.clicked.connect(self.refresh_ports)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.refresh_button)
        connection_layout.addRow("COM-Port:", port_layout)
        
        # Baudrate
        self.baudrate_edit = QLineEdit("57600")
        connection_layout.addRow("Baudrate:", self.baudrate_edit)
        
        # Verbindungsbutton
        self.connect_button = QPushButton("Verbinden")
        self.connect_button.clicked.connect(self.toggle_connection)
        self.connect_button.setMinimumWidth(120)
        
        # Verbindungsstatus
        self.status_label = QLabel("Nicht verbunden")
        self.status_label.setStyleSheet("color: red;")
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.connect_button)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        connection_layout.addRow("", status_layout)
        
        # Verbindungsgruppe zum Hauptlayout hinzufügen
        main_layout.addWidget(connection_group)
        
        # Telemetrie-Bereich
        telemetry_group = QGroupBox("Telemetrie")
        telemetry_layout = QVBoxLayout(telemetry_group)
        
        # Telemetrie-Werte
        self.telemetry_labels = {}
        
        telemetry_form = QFormLayout()
        for name, label in [
            ("armed", "Armed:"),
            ("flight_mode", "Flugmodus:"),
            ("battery_percent", "Batterie:"),
            ("battery_voltage", "Spannung:"),
            ("latitude", "Breitengrad:"),
            ("longitude", "Längengrad:"),
            ("altitude", "Höhe (abs.):"),
            ("relative_altitude", "Höhe (rel.):")
        ]:
            self.telemetry_labels[name] = QLabel("-")
            telemetry_form.addRow(label, self.telemetry_labels[name])
        
        telemetry_layout.addLayout(telemetry_form)
        
        # Telemetriegruppe zum Hauptlayout hinzufügen
        main_layout.addWidget(telemetry_group)
        
        # Log-Bereich
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        # Log-Gruppe zum Hauptlayout hinzufügen
        main_layout.addWidget(log_group)
        
        # Statuszeile
        self.statusBar().showMessage("Bereit")
    
    def refresh_ports(self):
        """Aktualisiert die Liste der verfügbaren COM-Ports"""
        self.port_combo.clear()
        ports = self.connection_helper.refreshPorts()
        self.port_combo.addItems(ports)
        
        if ports:
            self.port_combo.setCurrentIndex(0)
            self.statusBar().showMessage(f"{len(ports)} COM-Port(s) gefunden")
        else:
            self.statusBar().showMessage("Keine COM-Ports gefunden")
    
    def toggle_connection(self):
        """Verbindet oder trennt die Verbindung zur Drohne"""
        if self.connection_helper.connected:
            # Trennen
            self.connection_helper.disconnect()
        else:
            # Verbinden
            port = self.port_combo.currentText()
            baudrate = self.baudrate_edit.text()
            
            if not port:
                QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen COM-Port aus")
                return
            
            # Verbindungsstring mit Baudrate
            connection_string = f"{port}:{baudrate}" if baudrate else port
            self.connection_helper.connectToDrone(connection_string)
    
    def update_connection_status(self, is_connected):
        """Aktualisiert den Verbindungsstatus in der UI"""
        if is_connected:
            self.status_label.setText("Verbunden")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.connect_button.setText("Trennen")
            self.statusBar().showMessage("Verbunden mit der Drohne")
        else:
            self.status_label.setText("Nicht verbunden")
            self.status_label.setStyleSheet("color: red;")
            self.connect_button.setText("Verbinden")
            self.statusBar().showMessage("Nicht verbunden")
            
            # Telemetrie zurücksetzen
            for label in self.telemetry_labels.values():
                label.setText("-")
    
    def update_telemetry(self, telemetry):
        """Aktualisiert die Telemetrie-Anzeige"""
        # Armed-Status
        self.telemetry_labels["armed"].setText(str(telemetry["armed"]))
        self.telemetry_labels["armed"].setStyleSheet("color: green; font-weight: bold;" if telemetry["armed"] else "color: red;")
        
        # Flugmodus
        self.telemetry_labels["flight_mode"].setText(telemetry["flight_mode"])
        
        # Batterie
        bat_text = f"{telemetry['battery_percent']:.1f}%"
        self.telemetry_labels["battery_percent"].setText(bat_text)
        
        # Batteriespannung
        volt_text = f"{telemetry['battery_voltage']:.2f}V"
        self.telemetry_labels["battery_voltage"].setText(volt_text)
        
        # Position
        self.telemetry_labels["latitude"].setText(f"{telemetry['latitude']:.6f}°")
        self.telemetry_labels["longitude"].setText(f"{telemetry['longitude']:.6f}°")
        
        # Höhen
        self.telemetry_labels["altitude"].setText(f"{telemetry['altitude']:.1f}m")
        self.telemetry_labels["relative_altitude"].setText(f"{telemetry['relative_altitude']:.1f}m")
    
    def add_log(self, message):
        """Fügt eine Nachricht zum Log hinzu"""
        # Neuen Text an das Ende des Logs anhängen
        self.log_text.append(message)
        
        # Log automatisch nach unten scrollen
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Log auch im Logger speichern
        self.logger.addLog(message)


def main():
    """Hauptfunktion der Anwendung"""
    # Versionsinfo ausgeben
    print(f"Python-Version: {sys.version}")
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # Arbeitsverzeichnis setzen
    os.chdir(project_root)
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # Material-Stil setzen
    QQuickStyle.setStyle("Material")
    
    # Anwendung erstellen
    app = QApplication(sys.argv)
    
    # Hauptfenster erstellen
    window = MainWindow()
    window.show()
    
    # Anwendung starten
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
