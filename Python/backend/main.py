"""
Hauptanwendung.
"""

import sys
import os
import logging
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QPushButton, QComboBox,
                              QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout,
                              QLineEdit, QTextEdit, QMessageBox, QTabWidget,
                              QTableWidget, QTableWidgetItem)

from flight_control.models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan
from flight_control.enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from flight_control.services import (FlightService, MissionService, AutonomousService,
                                   GeofenceService, CollisionService)
from flight_control.viewmodels import (FlightViewModel, MissionViewModel, AutonomousViewModel,
                                     GeofenceViewModel, CollisionViewModel)
from flight_control.views import (FlightView, MissionView, AutonomousView,
                                GeofenceView, CollisionView)
from telemetry.telemetry_manager import TelemetryManager
from connection.connection_manager import ConnectionManager

class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        """Initialisiert das Hauptfenster"""
        super().__init__()
        
        # Fenster-Eigenschaften
        self.setWindowTitle("RZGS2 Flugsteuerung")
        self.setGeometry(100, 100, 1200, 800)
        
        # Logger
        self._setup_logging()
        
        # Manager
        self._telemetry = TelemetryManager()
        self._connection = ConnectionManager()
        
        # Services
        self._flight_service = FlightService(self._telemetry, self._connection)
        self._mission_service = MissionService(self._telemetry, self._connection)
        self._autonomous_service = AutonomousService(self._telemetry, self._connection)
        self._geofence_service = GeofenceService(self._telemetry, self._connection)
        self._collision_service = CollisionService(self._telemetry, self._connection)
        
        # ViewModels
        self._flight_viewmodel = FlightViewModel(self._flight_service)
        self._mission_viewmodel = MissionViewModel(self._mission_service)
        self._autonomous_viewmodel = AutonomousViewModel(self._autonomous_service)
        self._geofence_viewmodel = GeofenceViewModel(self._geofence_service)
        self._collision_viewmodel = CollisionViewModel(self._collision_service)
        
        # Views
        self._flight_view = FlightView(self._flight_viewmodel)
        self._mission_view = MissionView(self._mission_viewmodel)
        self._autonomous_view = AutonomousView(self._autonomous_viewmodel)
        self._geofence_view = GeofenceView(self._geofence_viewmodel)
        self._collision_view = CollisionView(self._collision_viewmodel)
        
        # UI initialisieren
        self._init_ui()
        
        # Timer für Statusaktualisierungen
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(100)  # 100ms
        
    def _setup_logging(self) -> None:
        """Konfiguriert das Logging"""
        # Log-Verzeichnis erstellen
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Log-Datei
        log_file = os.path.join(log_dir, f"flight_control_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Logger konfigurieren
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _init_ui(self) -> None:
        """Initialisiert die Benutzeroberfläche"""
        # Hauptwidget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Hauptlayout
        layout = QVBoxLayout()
        
        # Tab-Widget
        tab_widget = QTabWidget()
        
        # Tabs hinzufügen
        tab_widget.addTab(self._flight_view, "Flug")
        tab_widget.addTab(self._mission_view, "Mission")
        tab_widget.addTab(self._autonomous_view, "Autonom")
        tab_widget.addTab(self._geofence_view, "Geofence")
        tab_widget.addTab(self._collision_view, "Kollisionsvermeidung")
        
        layout.addWidget(tab_widget)
        
        # Hauptlayout setzen
        central_widget.setLayout(layout)
        
    def _update_status(self) -> None:
        """Aktualisiert den Status"""
        # TODO: Status aktualisieren
        pass
        
    def closeEvent(self, event) -> None:
        """
        Event-Handler für das Schließen des Fensters.
        
        Args:
            event: Schließen-Event
        """
        # TODO: Aufräumarbeiten
        event.accept()

def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 