#!/usr/bin/env python3
"""
Einfache Testanwendung für die MAVSDK-Integration über serielle Verbindung
"""

import os
import sys
import time
import asyncio
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit, QSpinBox,
    QGroupBox, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Slot, Signal, QThread

# Pfade einrichten
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import von eigenen Modulen
from backend.logger import Logger
from backend.mavsdk_server_controller import MAVSDKServerController

# MAVSDK und MAVSDK-Server prüfen
try:
    import mavsdk
    print("MAVSDK erfolgreich importiert")
except ImportError:
    print("FEHLER: MAVSDK nicht installiert.")
    print("Installiere mit: pip install mavsdk")
    sys.exit(1)


class LogWidget(QWidget):
    """Widget für die Anzeige von Logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setLayout(QVBoxLayout())
        
        # Titel
        self.title_label = QLabel("Log-Ausgabe")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Text-Bereich für reguläre Logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # Titel für Systeminformationen
        self.system_info_title = QLabel("Systeminformationen")
        self.system_info_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Text-Bereich für Systeminformationen (größer und mit fetter Schrift)
        self.system_info_text = QTextEdit()
        self.system_info_text.setReadOnly(True)
        self.system_info_text.setStyleSheet("font-size: 16px;")
        self.system_info_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.system_info_text.setMinimumHeight(200)  # 30% der Höhe
        
        # Layout
        self.layout().addWidget(self.title_label)
        self.layout().addWidget(self.log_text)
        self.layout().addWidget(self.system_info_title)
        self.layout().addWidget(self.system_info_text)
        
    def add_log(self, message):
        """Fügt eine Log-Meldung hinzu"""
        # Prüfen, ob es sich um eine Systeminformation handelt
        if "[SYSTEM INFO]" in message:
            # Hervorheben und in Systeminformationen anzeigen
            self.system_info_text.append(f"<b>{message}</b>")
            self.system_info_text.ensureCursorVisible()
        else:
            # Normale Log-Meldung
            self.log_text.append(message)
            self.log_text.ensureCursorVisible()
    
    def clear(self):
        """Löscht alle Logs"""
        self.log_text.clear()
        self.system_info_text.clear()


class SerialConnectionWidget(QGroupBox):
    """Widget für die serielle Verbindung"""
    
    connect_clicked = Signal(str, int)
    disconnect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Serielle Verbindung", parent)
        
        self.setLayout(QVBoxLayout())
        
        # Port-Auswahl
        port_layout = QHBoxLayout()
        port_label = QLabel("COM-Port:")
        self.port_combo = QComboBox()
        self.refresh_ports_button = QPushButton("Aktualisieren")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.refresh_ports_button)
        
        # Baudrate
        baudrate_layout = QHBoxLayout()
        baudrate_label = QLabel("Baudrate:")
        self.baudrate_spin = QSpinBox()
        self.baudrate_spin.setRange(9600, 921600)
        self.baudrate_spin.setValue(57600)
        self.baudrate_spin.setSingleStep(9600)
        baudrate_layout.addWidget(baudrate_label)
        baudrate_layout.addWidget(self.baudrate_spin)
        
        # Verbindungs-Buttons
        connection_layout = QHBoxLayout()
        self.connect_button = QPushButton("Verbinden")
        self.disconnect_button = QPushButton("Trennen")
        self.disconnect_button.setEnabled(False)
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(self.disconnect_button)
        
        # Layout
        self.layout().addLayout(port_layout)
        self.layout().addLayout(baudrate_layout)
        self.layout().addLayout(connection_layout)
        
        # Signale verbinden
        self.refresh_ports_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self._on_connect_clicked)
        self.disconnect_button.clicked.connect(self._on_disconnect_clicked)
        
        # Ports beim Start aktualisieren
        self.refresh_ports()
    
    def refresh_ports(self):
        """Aktualisiert die Liste der verfügbaren COM-Ports"""
        import serial.tools.list_ports
        
        self.port_combo.clear()
        
        # Liste der verfügbaren Ports abrufen
        ports = list(serial.tools.list_ports.comports())
        
        # Simulator hinzufügen
        self.port_combo.addItem("Simulator")
        
        # COM-Ports hinzufügen
        for port in ports:
            self.port_combo.addItem(port.device)
    
    def _on_connect_clicked(self):
        """Wird aufgerufen, wenn der Verbinden-Button geklickt wird"""
        port = self.port_combo.currentText()
        baudrate = self.baudrate_spin.value()
        
        self.connect_clicked.emit(port, baudrate)
        
        # UI-Status aktualisieren
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        self.port_combo.setEnabled(False)
        self.baudrate_spin.setEnabled(False)
    
    def _on_disconnect_clicked(self):
        """Wird aufgerufen, wenn der Trennen-Button geklickt wird"""
        self.disconnect_clicked.emit()
        
        # UI-Status aktualisieren
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.port_combo.setEnabled(True)
        self.baudrate_spin.setEnabled(True)


class DroneControlWidget(QGroupBox):
    """Widget für die Steuerung der Drohne"""
    
    arm_clicked = Signal()
    disarm_clicked = Signal()
    takeoff_clicked = Signal()
    land_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Drohnen-Steuerung", parent)
        
        self.setLayout(QVBoxLayout())
        
        # Status-Anzeige
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        self.status_value = QLabel("Nicht verbunden")
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_value)
        
        # ARM/DISARM-Buttons
        arm_layout = QHBoxLayout()
        self.arm_button = QPushButton("ARM")
        self.disarm_button = QPushButton("DISARM")
        arm_layout.addWidget(self.arm_button)
        arm_layout.addWidget(self.disarm_button)
        
        # Takeoff/Land-Buttons
        flight_layout = QHBoxLayout()
        self.takeoff_button = QPushButton("TAKEOFF")
        self.land_button = QPushButton("LAND")
        flight_layout.addWidget(self.takeoff_button)
        flight_layout.addWidget(self.land_button)
        
        # Layout
        self.layout().addLayout(status_layout)
        self.layout().addLayout(arm_layout)
        self.layout().addLayout(flight_layout)
        
        # Signale verbinden
        self.arm_button.clicked.connect(self.arm_clicked)
        self.disarm_button.clicked.connect(self.disarm_clicked)
        self.takeoff_button.clicked.connect(self.takeoff_clicked)
        self.land_button.clicked.connect(self.land_clicked)
        
        # Buttons deaktivieren
        self.set_enabled(False)
    
    def set_enabled(self, enabled):
        """Aktiviert oder deaktiviert die Steuerungselemente"""
        self.arm_button.setEnabled(enabled)
        self.disarm_button.setEnabled(enabled)
        self.takeoff_button.setEnabled(enabled)
        self.land_button.setEnabled(enabled)
    
    def set_status(self, connected, armed=False, flight_mode="UNBEKANNT"):
        """Aktualisiert die Status-Anzeige"""
        if connected:
            status_text = f"Verbunden | {'ARMED' if armed else 'DISARMED'} | {flight_mode}"
            self.status_value.setText(status_text)
            self.set_enabled(True)
        else:
            self.status_value.setText("Nicht verbunden")
            self.set_enabled(False)


class MAVSDKTestApp(QMainWindow):
    """Hauptfenster für die MAVSDK-Testanwendung"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MAVSDK Serial Test")
        self.resize(800, 600)
        
        # Logger initialisieren
        self.logger = Logger()
        
        # MAVSDK-Server-Controller initialisieren
        self.server_controller = MAVSDKServerController(self.logger)
        
        # Haupt-Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        main_layout = QVBoxLayout(central_widget)
        
        # Verbindungs-Widget
        self.connection_widget = SerialConnectionWidget()
        
        # Drohnen-Steuerungs-Widget
        self.control_widget = DroneControlWidget()
        
        # Log-Widget
        self.log_widget = LogWidget()
        
        # Splitter für die rechte Seite (Steuerung und Log)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(self.control_widget)
        right_layout.addWidget(self.log_widget)
        
        # Haupt-Layout
        main_layout.addWidget(self.connection_widget)
        main_layout.addWidget(right_widget)
        
        # Signale verbinden
        self.connection_widget.connect_clicked.connect(self.connect_to_drone)
        self.connection_widget.disconnect_clicked.connect(self.disconnect_from_drone)
        self.control_widget.arm_clicked.connect(self.arm_drone)
        self.control_widget.disarm_clicked.connect(self.disarm_drone)
        self.control_widget.takeoff_clicked.connect(self.takeoff_drone)
        self.control_widget.land_clicked.connect(self.land_drone)
        self.logger.logAdded.connect(self.log_widget.add_log)
        
        # Timer für die UI-Aktualisierung
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(500)  # 500 ms
        
        # MAVSDK-System
        self.drone = None
        self.is_connected = False
        self.is_armed = False
        self.flight_mode = "UNBEKANNT"
        
        # Event-Loop für MAVSDK
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Verbindungs-Task
        self.connection_task = None
        
        self.logger.addLog("MAVSDK-Testanwendung gestartet")
        self.logger.addLog("Wähle einen COM-Port und klicke auf 'Verbinden'")
    
    def update_ui(self):
        """Aktualisiert die UI basierend auf dem aktuellen Status"""
        self.control_widget.set_status(self.is_connected, self.is_armed, self.flight_mode)
    
    @Slot(str, int)
    def connect_to_drone(self, port, baudrate):
        """Verbindet mit der Drohne über den angegebenen COM-Port"""
        self.logger.addLog(f"Verbinde mit {port} bei {baudrate} Baud...")
        
        if port == "Simulator":
            # Mit Simulator verbinden
            connection_string = "udp://:14540"
            self.logger.addLog(f"Verbinde mit SITL-Simulator über {connection_string}")
            self.connect_mavsdk(connection_string)
        else:
            # MAVSDK-Server starten
            if self.server_controller.start_server(port, baudrate):
                self.logger.addLog("[INFO] MAVSDK-Server erfolgreich gestartet")
                
                # Kurz warten, bis der Server gestartet ist
                time.sleep(1.5)
                
                # Mit lokalem MAVSDK-Server verbinden
                connection_string = "tcp://localhost:50051"
                self.connect_mavsdk(connection_string)
            else:
                self.logger.addLog("[FEHLER] MAVSDK-Server konnte nicht gestartet werden")
                self.connection_widget._on_disconnect_clicked()  # UI zurücksetzen
    
    def connect_mavsdk(self, connection_string):
        """Verbindet mit MAVSDK über den angegebenen Verbindungsstring"""
        # Neues System erstellen
        self.drone = mavsdk.System()
        
        # Verbindungs-Task starten
        self.connection_task = asyncio.run_coroutine_threadsafe(
            self.connect_and_monitor(connection_string),
            self.loop
        )
    
    async def connect_and_monitor(self, connection_string):
        """Verbindet mit dem Drone-System und überwacht den Status"""
        try:
            # Verbindung herstellen
            await self.drone.connect(system_address=connection_string)
            
            # Auf Verbindung warten
            self.logger.addLog("[INFO] Warte auf Heartbeat...")
            async for state in self.drone.core.connection_state():
                if state.is_connected:
                    self.logger.addLog("[INFO] Verbindung hergestellt")
                    self.is_connected = True
                    
                    # Telemetrie-Subscriptions starten
                    self.start_telemetry()
                    break
            
            # Verbindungsstatus anzeigen
            self.logger.addLog("[SYSTEM INFO] Verbindung hergestellt. Warte auf Systeminformationen...")
            
            # Automatisch nach Systeminformationen fragen
            # Dies entspricht dem Verhalten der echten RZGCS-Implementierung mit der Preflight-View
            self.logger.addLog("[INFO] Frage Systeminformationen ab...")
            
            # Status überwachen, solange verbunden
            while self.is_connected:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.addLog(f"[FEHLER] MAVSDK-Fehler: {str(e)}")
            self.is_connected = False
        finally:
            self.logger.addLog("[INFO] Verbindung beendet")
    
    def start_telemetry(self):
        """Startet die Telemetrie-Subscriptions"""
        # Armed-Status
        asyncio.run_coroutine_threadsafe(
            self.monitor_armed_status(),
            self.loop
        )
        
        # Flight Mode
        asyncio.run_coroutine_threadsafe(
            self.monitor_flight_mode(),
            self.loop
        )
        
        # Status Text
        asyncio.run_coroutine_threadsafe(
            self.monitor_status_text(),
            self.loop
        )
    
    async def monitor_armed_status(self):
        """Überwacht den Armed-Status"""
        try:
            async for armed in self.drone.telemetry.armed():
                self.is_armed = armed
        except Exception as e:
            self.logger.addLog(f"[FEHLER] Fehler beim Überwachen des Armed-Status: {str(e)}")
    
    async def monitor_flight_mode(self):
        """Überwacht den Flugmodus"""
        try:
            async for flight_mode in self.drone.telemetry.flight_mode():
                self.flight_mode = str(flight_mode)
        except Exception as e:
            self.logger.addLog(f"[FEHLER] Fehler beim Überwachen des Flugmodus: {str(e)}")
    
    async def monitor_status_text(self):
        """Überwacht Status-Texte"""
        try:
            async for status_text in self.drone.telemetry.status_text():
                text = status_text.text
                
                # Auf Systeminformationen prüfen
                is_system_info = False
                system_info_patterns = [
                    "Frame", "ArduCopter", "MicoAir743", "ChibiOS", 
                    "PreArm", "RCOut", "Firmware", "Version"
                ]
                
                for pattern in system_info_patterns:
                    if pattern in text:
                        is_system_info = True
                        break
                
                # Systeminformationen markieren
                if is_system_info and not text.startswith("[SYSTEM INFO]"):
                    text = f"[SYSTEM INFO] {text}"
                
                self.logger.addLog(text)
                
        except Exception as e:
            self.logger.addLog(f"[FEHLER] Fehler beim Überwachen der Status-Texte: {str(e)}")
    
    @Slot()
    def disconnect_from_drone(self):
        """Trennt die Verbindung zur Drohne"""
        self.logger.addLog("[INFO] Trenne Verbindung...")
        
        # Verbindung beenden
        self.is_connected = False
        
        # MAVSDK-Server stoppen
        self.server_controller.stop_server()
        
        self.logger.addLog("[INFO] Verbindung getrennt")
    
    @Slot()
    def arm_drone(self):
        """Armiert die Drohne"""
        if not self.is_connected or not self.drone:
            self.logger.addLog("[FEHLER] Nicht verbunden")
            return
        
        self.logger.addLog("[INFO] Armiere Drohne...")
        asyncio.run_coroutine_threadsafe(self.drone.action.arm(), self.loop)
    
    @Slot()
    def disarm_drone(self):
        """Disarmiert die Drohne"""
        if not self.is_connected or not self.drone:
            self.logger.addLog("[FEHLER] Nicht verbunden")
            return
        
        self.logger.addLog("[INFO] Disarmiere Drohne...")
        asyncio.run_coroutine_threadsafe(self.drone.action.disarm(), self.loop)
    
    @Slot()
    def takeoff_drone(self):
        """Lässt die Drohne starten"""
        if not self.is_connected or not self.drone:
            self.logger.addLog("[FEHLER] Nicht verbunden")
            return
        
        if not self.is_armed:
            self.logger.addLog("[FEHLER] Drohne ist nicht armiert")
            return
        
        self.logger.addLog("[INFO] Starte Drohne...")
        asyncio.run_coroutine_threadsafe(self.drone.action.takeoff(), self.loop)
    
    @Slot()
    def land_drone(self):
        """Lässt die Drohne landen"""
        if not self.is_connected or not self.drone:
            self.logger.addLog("[FEHLER] Nicht verbunden")
            return
        
        self.logger.addLog("[INFO] Lande Drohne...")
        asyncio.run_coroutine_threadsafe(self.drone.action.land(), self.loop)
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        # Verbindung trennen
        self.disconnect_from_drone()
        
        # Event-Loop beenden
        self.loop.stop()
        
        event.accept()


class AsyncioThread(QThread):
    """Thread für die asyncio Event-Loop"""
    
    def run(self):
        """Hauptmethode des Threads"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()


def main():
    """Hauptfunktion"""
    try:
        # Prüfen, ob benötigte Module verfügbar sind
        import serial
    except ImportError:
        print("FEHLER: PySerial nicht installiert.")
        print("Installiere mit: pip install pyserial")
        sys.exit(1)
        
    app = QApplication(sys.argv)
    window = MAVSDKTestApp()
    window.show()
    
    # Event-Loop für MAVSDK im Hintergrund starten
    asyncio_thread = AsyncioThread()
    asyncio_thread.start()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
