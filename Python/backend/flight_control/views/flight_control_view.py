"""Flugsteuerungs-View.

Diese View implementiert die Benutzeroberfläche für die Flugsteuerung.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QFormLayout,
    QTextEdit,
    QMessageBox
)

from ..models.flight_control_data import (
    FlightMode,
    ControlMode,
    ControlAxis,
    ControlCommand,
    ControlStatus,
    ControlInput,
    ControlOutput,
    ControlState,
    ControlEvent,
    ControlLog,
    FlightControlError,
    FlightControlValidationError,
    FlightControlCommandError,
    FlightControlStateError
)
from ..viewmodels.flight_control_viewmodel import FlightControlViewModel

class FlightControlView(QWidget):
    """Flugsteuerungs-View.
    
    Diese View implementiert die Benutzeroberfläche für die Flugsteuerung.
    
    Attributes:
        _viewmodel: Flugsteuerungs-ViewModel
        _mode_combo: ComboBox für den Flugmodus
        _control_mode_combo: ComboBox für den Steuerungsmodus
        _status_label: Label für den Steuerungsstatus
        _log_text: TextEdit für das Log
        _position_group: GroupBox für die Positionssteuerung
        _velocity_group: GroupBox für die Geschwindigkeitssteuerung
        _attitude_group: GroupBox für die Attitudensteuerung
        _rate_group: GroupBox für die Ratensteuerung
        _thrust_group: GroupBox für die Schubsteuerung
        _emergency_button: Button für den Notstopp
    """
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._viewmodel = None
        self._init_ui()
    
    def set_viewmodel(self, viewmodel: FlightControlViewModel):
        """ViewModel setzen.
        
        Args:
            viewmodel: Flugsteuerungs-ViewModel
        """
        self._viewmodel = viewmodel
        
        # ViewModel-Signale verbinden
        self._viewmodel.state_changed.connect(self._update_ui)
        self._viewmodel.log_changed.connect(self._update_log)
        
        # UI aktualisieren
        self._update_ui()
        self._update_log()
    
    def _init_ui(self):
        """UI initialisieren."""
        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Modus-Gruppe
        mode_group = QGroupBox("Modus")
        mode_layout = QFormLayout()
        
        # Flugmodus
        self._mode_combo = QComboBox()
        self._mode_combo.addItems([mode.value for mode in FlightMode])
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addRow("Flugmodus:", self._mode_combo)
        
        # Steuerungsmodus
        self._control_mode_combo = QComboBox()
        self._control_mode_combo.addItems([mode.value for mode in ControlMode])
        self._control_mode_combo.currentTextChanged.connect(self._on_control_mode_changed)
        mode_layout.addRow("Steuerungsmodus:", self._control_mode_combo)
        
        # Status
        self._status_label = QLabel()
        mode_layout.addRow("Status:", self._status_label)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Positions-Gruppe
        self._position_group = QGroupBox("Positionssteuerung")
        position_layout = QFormLayout()
        
        # Latitude
        self._latitude_spin = QDoubleSpinBox()
        self._latitude_spin.setRange(-90, 90)
        self._latitude_spin.setDecimals(6)
        position_layout.addRow("Latitude:", self._latitude_spin)
        
        # Longitude
        self._longitude_spin = QDoubleSpinBox()
        self._longitude_spin.setRange(-180, 180)
        self._longitude_spin.setDecimals(6)
        position_layout.addRow("Longitude:", self._longitude_spin)
        
        # Altitude
        self._altitude_spin = QDoubleSpinBox()
        self._altitude_spin.setRange(0, 1000)
        self._altitude_spin.setDecimals(2)
        position_layout.addRow("Altitude:", self._altitude_spin)
        
        # Position-Button
        self._position_button = QPushButton("Position ansteuern")
        self._position_button.clicked.connect(self._on_position_clicked)
        position_layout.addRow(self._position_button)
        
        # Hold-Button
        self._hold_button = QPushButton("Position halten")
        self._hold_button.clicked.connect(self._on_hold_clicked)
        position_layout.addRow(self._hold_button)
        
        self._position_group.setLayout(position_layout)
        layout.addWidget(self._position_group)
        
        # Geschwindigkeits-Gruppe
        self._velocity_group = QGroupBox("Geschwindigkeitssteuerung")
        velocity_layout = QFormLayout()
        
        # vx
        self._vx_spin = QDoubleSpinBox()
        self._vx_spin.setRange(-10, 10)
        self._vx_spin.setDecimals(2)
        velocity_layout.addRow("vx:", self._vx_spin)
        
        # vy
        self._vy_spin = QDoubleSpinBox()
        self._vy_spin.setRange(-10, 10)
        self._vy_spin.setDecimals(2)
        velocity_layout.addRow("vy:", self._vy_spin)
        
        # vz
        self._vz_spin = QDoubleSpinBox()
        self._vz_spin.setRange(-10, 10)
        self._vz_spin.setDecimals(2)
        velocity_layout.addRow("vz:", self._vz_spin)
        
        # Geschwindigkeits-Button
        self._velocity_button = QPushButton("Geschwindigkeit setzen")
        self._velocity_button.clicked.connect(self._on_velocity_clicked)
        velocity_layout.addRow(self._velocity_button)
        
        self._velocity_group.setLayout(velocity_layout)
        layout.addWidget(self._velocity_group)
        
        # Attitude-Gruppe
        self._attitude_group = QGroupBox("Attitudensteuerung")
        attitude_layout = QFormLayout()
        
        # Roll
        self._roll_spin = QDoubleSpinBox()
        self._roll_spin.setRange(-180, 180)
        self._roll_spin.setDecimals(2)
        attitude_layout.addRow("Roll:", self._roll_spin)
        
        # Pitch
        self._pitch_spin = QDoubleSpinBox()
        self._pitch_spin.setRange(-90, 90)
        self._pitch_spin.setDecimals(2)
        attitude_layout.addRow("Pitch:", self._pitch_spin)
        
        # Yaw
        self._yaw_spin = QDoubleSpinBox()
        self._yaw_spin.setRange(-180, 180)
        self._yaw_spin.setDecimals(2)
        attitude_layout.addRow("Yaw:", self._yaw_spin)
        
        # Attitude-Button
        self._attitude_button = QPushButton("Attitude ansteuern")
        self._attitude_button.clicked.connect(self._on_attitude_clicked)
        attitude_layout.addRow(self._attitude_button)
        
        self._attitude_group.setLayout(attitude_layout)
        layout.addWidget(self._attitude_group)
        
        # Rate-Gruppe
        self._rate_group = QGroupBox("Ratensteuerung")
        rate_layout = QFormLayout()
        
        # Roll-Rate
        self._roll_rate_spin = QDoubleSpinBox()
        self._roll_rate_spin.setRange(-180, 180)
        self._roll_rate_spin.setDecimals(2)
        rate_layout.addRow("Roll-Rate:", self._roll_rate_spin)
        
        # Pitch-Rate
        self._pitch_rate_spin = QDoubleSpinBox()
        self._pitch_rate_spin.setRange(-180, 180)
        self._pitch_rate_spin.setDecimals(2)
        rate_layout.addRow("Pitch-Rate:", self._pitch_rate_spin)
        
        # Yaw-Rate
        self._yaw_rate_spin = QDoubleSpinBox()
        self._yaw_rate_spin.setRange(-180, 180)
        self._yaw_rate_spin.setDecimals(2)
        rate_layout.addRow("Yaw-Rate:", self._yaw_rate_spin)
        
        # Rate-Button
        self._rate_button = QPushButton("Rate setzen")
        self._rate_button.clicked.connect(self._on_rate_clicked)
        rate_layout.addRow(self._rate_button)
        
        self._rate_group.setLayout(rate_layout)
        layout.addWidget(self._rate_group)
        
        # Schub-Gruppe
        self._thrust_group = QGroupBox("Schubsteuerung")
        thrust_layout = QFormLayout()
        
        # Schub
        self._thrust_spin = QDoubleSpinBox()
        self._thrust_spin.setRange(0, 1)
        self._thrust_spin.setDecimals(2)
        thrust_layout.addRow("Schub:", self._thrust_spin)
        
        # Schub-Button
        self._thrust_button = QPushButton("Schub setzen")
        self._thrust_button.clicked.connect(self._on_thrust_clicked)
        thrust_layout.addRow(self._thrust_button)
        
        self._thrust_group.setLayout(thrust_layout)
        layout.addWidget(self._thrust_group)
        
        # Notstopp-Button
        self._emergency_button = QPushButton("NOTSTOPP")
        self._emergency_button.setStyleSheet("background-color: red; color: white;")
        self._emergency_button.clicked.connect(self._on_emergency_clicked)
        layout.addWidget(self._emergency_button)
        
        # Log-Gruppe
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        
        # Log-Text
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        log_layout.addWidget(self._log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
    
    def _update_ui(self):
        """UI aktualisieren."""
        if not self._viewmodel:
            return
        
        # Modus
        self._mode_combo.setCurrentText(self._viewmodel.flight_mode)
        self._control_mode_combo.setCurrentText(self._viewmodel.control_mode)
        self._status_label.setText(self._viewmodel.control_status)
        
        # Gruppen aktivieren/deaktivieren
        self._position_group.setEnabled(not self._viewmodel.is_manual_mode)
        self._velocity_group.setEnabled(not self._viewmodel.is_manual_mode)
        self._attitude_group.setEnabled(not self._viewmodel.is_manual_mode)
        self._rate_group.setEnabled(not self._viewmodel.is_manual_mode)
        self._thrust_group.setEnabled(not self._viewmodel.is_manual_mode)
        
        # Buttons aktivieren/deaktivieren
        self._position_button.setEnabled(not self._viewmodel.is_manual_mode)
        self._hold_button.setEnabled(not self._viewmodel.is_manual_mode)
        self._velocity_button.setEnabled(not self._viewmodel.is_manual_mode)
        self._attitude_button.setEnabled(not self._viewmodel.is_manual_mode)
        self._rate_button.setEnabled(not self._viewmodel.is_manual_mode)
        self._thrust_button.setEnabled(not self._viewmodel.is_manual_mode)
        
        # Notstopp-Button aktivieren/deaktivieren
        self._emergency_button.setEnabled(not self._viewmodel.is_emergency_mode)
    
    def _update_log(self):
        """Log aktualisieren."""
        if not self._viewmodel:
            return
        
        # Log-Text aktualisieren
        self._log_text.setText("\n".join(self._viewmodel.log_events))
    
    def _on_mode_changed(self, mode: str):
        """Flugmodus geändert.
        
        Args:
            mode: Neuer Flugmodus
        """
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.set_mode(mode)
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_control_mode_changed(self, control_mode: str):
        """Steuerungsmodus geändert.
        
        Args:
            control_mode: Neuer Steuerungsmodus
        """
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.set_control_mode(control_mode)
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_position_clicked(self):
        """Position-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            position = {
                "latitude": self._latitude_spin.value(),
                "longitude": self._longitude_spin.value(),
                "altitude": self._altitude_spin.value()
            }
            self._viewmodel.move_to_position(position)
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_hold_clicked(self):
        """Hold-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.hold_position()
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_velocity_clicked(self):
        """Geschwindigkeits-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            velocity = {
                "vx": self._vx_spin.value(),
                "vy": self._vy_spin.value(),
                "vz": self._vz_spin.value()
            }
            self._viewmodel.set_velocity(velocity)
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_attitude_clicked(self):
        """Attitude-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            attitude = {
                "roll": self._roll_spin.value(),
                "pitch": self._pitch_spin.value(),
                "yaw": self._yaw_spin.value()
            }
            self._viewmodel.rotate_to_attitude(attitude)
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_rate_clicked(self):
        """Rate-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            rate = {
                "roll_rate": self._roll_rate_spin.value(),
                "pitch_rate": self._pitch_rate_spin.value(),
                "yaw_rate": self._yaw_rate_spin.value()
            }
            self._viewmodel.set_rate(rate)
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_thrust_clicked(self):
        """Schub-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.set_thrust(self._thrust_spin.value())
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_emergency_clicked(self):
        """Notstopp-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.emergency_stop()
        except FlightControlError as e:
            QMessageBox.critical(self, "Fehler", str(e)) 