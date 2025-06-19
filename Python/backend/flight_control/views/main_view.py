"""
Hauptansicht für die Flugsteuerung.
Implementiert die Benutzeroberfläche für die Flugsteuerung.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox,
    QDoubleSpinBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, Slot, Signal

from ..viewmodels.main_viewmodel import MainViewModel
from ..enums import FlightStatus, FlightMode, ConnectionStatus, ConnectionType

class MainView(QMainWindow):
    """Implementiert die Hauptansicht für die Flugsteuerung"""
    
    def __init__(self, viewmodel: MainViewModel):
        """
        Initialisiert die Ansicht.
        
        Args:
            viewmodel: Haupt-ViewModel
        """
        super().__init__()
        
        # ViewModel
        self._viewmodel = viewmodel
        
        # UI initialisieren
        self._init_ui()
        
        # Signale verbinden
        self._connect_signals()
        
    def _init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        # Hauptwidget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Verbindungssteuerung
        connection_group = QWidget()
        connection_layout = QHBoxLayout()
        connection_group.setLayout(connection_layout)
        
        # Verbindungstyp
        self._connection_type = QComboBox()
        self._connection_type.addItems([t.name for t in ConnectionType])
        connection_layout.addWidget(QLabel("Verbindungstyp:"))
        connection_layout.addWidget(self._connection_type)
        
        # Verbindungsstatus
        self._connection_status = QLabel("Nicht verbunden")
        connection_layout.addWidget(self._connection_status)
        
        # Verbindungsbuttons
        self._connect_button = QPushButton("Verbinden")
        self._disconnect_button = QPushButton("Trennen")
        self._disconnect_button.setEnabled(False)
        connection_layout.addWidget(self._connect_button)
        connection_layout.addWidget(self._disconnect_button)
        
        layout.addWidget(connection_group)
        
        # Flugsteuerung
        flight_group = QWidget()
        flight_layout = QHBoxLayout()
        flight_group.setLayout(flight_layout)
        
        # Flugmodus
        self._flight_mode = QComboBox()
        self._flight_mode.addItems([m.name for m in FlightMode])
        flight_layout.addWidget(QLabel("Flugmodus:"))
        flight_layout.addWidget(self._flight_mode)
        
        # Flugstatus
        self._flight_status = QLabel("Nicht bereit")
        flight_layout.addWidget(self._flight_status)
        
        # Flugbuttons
        self._arm_button = QPushButton("Scharf")
        self._disarm_button = QPushButton("Entscharfen")
        self._disarm_button.setEnabled(False)
        flight_layout.addWidget(self._arm_button)
        flight_layout.addWidget(self._disarm_button)
        
        layout.addWidget(flight_group)
        
        # Missionssteuerung
        mission_group = QWidget()
        mission_layout = QHBoxLayout()
        mission_group.setLayout(mission_layout)
        
        # Mission
        self._mission = QComboBox()
        mission_layout.addWidget(QLabel("Mission:"))
        mission_layout.addWidget(self._mission)
        
        # Missionsbuttons
        self._start_button = QPushButton("Starten")
        self._pause_button = QPushButton("Pause")
        self._resume_button = QPushButton("Fortsetzen")
        self._abort_button = QPushButton("Abbrechen")
        self._start_button.setEnabled(False)
        self._pause_button.setEnabled(False)
        self._resume_button.setEnabled(False)
        self._abort_button.setEnabled(False)
        mission_layout.addWidget(self._start_button)
        mission_layout.addWidget(self._pause_button)
        mission_layout.addWidget(self._resume_button)
        mission_layout.addWidget(self._abort_button)
        
        layout.addWidget(mission_group)
        
        # Telemetrie
        telemetry_group = QWidget()
        telemetry_layout = QVBoxLayout()
        telemetry_group.setLayout(telemetry_layout)
        
        # Position
        position_layout = QHBoxLayout()
        self._position_x = QDoubleSpinBox()
        self._position_y = QDoubleSpinBox()
        self._position_z = QDoubleSpinBox()
        position_layout.addWidget(QLabel("Position:"))
        position_layout.addWidget(QLabel("X:"))
        position_layout.addWidget(self._position_x)
        position_layout.addWidget(QLabel("Y:"))
        position_layout.addWidget(self._position_y)
        position_layout.addWidget(QLabel("Z:"))
        position_layout.addWidget(self._position_z)
        telemetry_layout.addLayout(position_layout)
        
        # Parameter
        parameter_layout = QHBoxLayout()
        self._parameter_name = QLineEdit()
        self._parameter_value = QLineEdit()
        parameter_layout.addWidget(QLabel("Parameter:"))
        parameter_layout.addWidget(self._parameter_name)
        parameter_layout.addWidget(QLabel("Wert:"))
        parameter_layout.addWidget(self._parameter_value)
        self._set_parameter_button = QPushButton("Setzen")
        parameter_layout.addWidget(self._set_parameter_button)
        telemetry_layout.addLayout(parameter_layout)
        
        layout.addWidget(telemetry_group)
        
        # Fenster
        self.setWindowTitle("Flugsteuerung")
        self.resize(800, 600)
        
    def _connect_signals(self):
        """Verbindet die Signale"""
        # Verbindung
        self._connection_type.currentTextChanged.connect(self._on_connection_type_changed)
        self._connect_button.clicked.connect(self._on_connect)
        self._disconnect_button.clicked.connect(self._on_disconnect)
        
        # Flug
        self._flight_mode.currentTextChanged.connect(self._on_flight_mode_changed)
        self._arm_button.clicked.connect(self._on_arm)
        self._disarm_button.clicked.connect(self._on_disarm)
        
        # Mission
        self._mission.currentTextChanged.connect(self._on_mission_changed)
        self._start_button.clicked.connect(self._on_start_mission)
        self._pause_button.clicked.connect(self._on_pause_mission)
        self._resume_button.clicked.connect(self._on_resume_mission)
        self._abort_button.clicked.connect(self._on_abort_mission)
        
        # Telemetrie
        self._set_parameter_button.clicked.connect(self._on_set_parameter)
        
        # ViewModel
        self._viewmodel.error_occurred.connect(self._on_error)
        
    # Slots
    @Slot(str)
    def _on_connection_type_changed(self, type: str):
        """
        Handler für Änderungen des Verbindungstyps.
        
        Args:
            type: Neuer Verbindungstyp
        """
        self._viewmodel.connection_viewmodel.set_parameter("type", ConnectionType[type])
        
    @Slot()
    def _on_connect(self):
        """Handler für Verbindungsaufbau"""
        if self._viewmodel.connection_viewmodel.connect():
            self._connect_button.setEnabled(False)
            self._disconnect_button.setEnabled(True)
            self._connection_status.setText("Verbunden")
            
    @Slot()
    def _on_disconnect(self):
        """Handler für Verbindungsabbau"""
        if self._viewmodel.connection_viewmodel.disconnect():
            self._connect_button.setEnabled(True)
            self._disconnect_button.setEnabled(False)
            self._connection_status.setText("Nicht verbunden")
            
    @Slot(str)
    def _on_flight_mode_changed(self, mode: str):
        """
        Handler für Änderungen des Flugmodus.
        
        Args:
            mode: Neuer Flugmodus
        """
        self._viewmodel.flight_viewmodel.set_mode(FlightMode[mode])
        
    @Slot()
    def _on_arm(self):
        """Handler für Scharfschaltung"""
        if self._viewmodel.flight_viewmodel.arm():
            self._arm_button.setEnabled(False)
            self._disarm_button.setEnabled(True)
            self._flight_status.setText("Scharf")
            
    @Slot()
    def _on_disarm(self):
        """Handler für Entscharfung"""
        if self._viewmodel.flight_viewmodel.disarm():
            self._arm_button.setEnabled(True)
            self._disarm_button.setEnabled(False)
            self._flight_status.setText("Nicht scharf")
            
    @Slot(str)
    def _on_mission_changed(self, mission: str):
        """
        Handler für Änderungen der Mission.
        
        Args:
            mission: Neue Mission
        """
        self._start_button.setEnabled(True)
        
    @Slot()
    def _on_start_mission(self):
        """Handler für Missionsstart"""
        if self._viewmodel.flight_viewmodel.start_mission():
            self._start_button.setEnabled(False)
            self._pause_button.setEnabled(True)
            self._abort_button.setEnabled(True)
            
    @Slot()
    def _on_pause_mission(self):
        """Handler für Missionspause"""
        if self._viewmodel.flight_viewmodel.pause_mission():
            self._pause_button.setEnabled(False)
            self._resume_button.setEnabled(True)
            
    @Slot()
    def _on_resume_mission(self):
        """Handler für Missionsfortsetzung"""
        if self._viewmodel.flight_viewmodel.resume_mission():
            self._resume_button.setEnabled(False)
            self._pause_button.setEnabled(True)
            
    @Slot()
    def _on_abort_mission(self):
        """Handler für Missionsabbruch"""
        if self._viewmodel.flight_viewmodel.abort_mission():
            self._start_button.setEnabled(True)
            self._pause_button.setEnabled(False)
            self._resume_button.setEnabled(False)
            self._abort_button.setEnabled(False)
            
    @Slot()
    def _on_set_parameter(self):
        """Handler für Parameteränderung"""
        name = self._parameter_name.text()
        value = self._parameter_value.text()
        
        if self._viewmodel.telemetry_viewmodel.set_parameter(name, value):
            self._parameter_name.clear()
            self._parameter_value.clear()
            
    @Slot(str)
    def _on_error(self, message: str):
        """
        Handler für Fehlermeldungen.
        
        Args:
            message: Fehlermeldung
        """
        QMessageBox.critical(self, "Fehler", message) 