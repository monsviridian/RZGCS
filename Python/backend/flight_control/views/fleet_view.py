"""Flotten-View.

Diese View implementiert die Benutzeroberfläche für die Flottensteuerung.
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
    QMessageBox,
    QTableWidget,
    QTableWidgetItem
)

from ..models.fleet_data import (
    FleetStatus,
    FleetMode,
    UAVStatus,
    UAVMode,
    NetworkTopology,
    EncryptionStatus,
    PositionData,
    VelocityData,
    AttitudeData,
    SensorData,
    ResourceData,
    RoutingTable,
    BandwidthAllocation,
    CommunicationData,
    UAVData,
    FleetData,
    FleetError,
    FleetValidationError,
    FleetCommandError,
    FleetStateError
)
from ..viewmodels.fleet_viewmodel import FleetViewModel

class FleetView(QWidget):
    """Flotten-View.
    
    Diese View implementiert die Benutzeroberfläche für die Flottensteuerung.
    
    Attributes:
        _viewmodel: Flotten-ViewModel
        _fleet_group: GroupBox für die Flottensteuerung
        _uav_table: Tabelle für die UAVs
        _resources_group: GroupBox für die Ressourcen
        _communication_group: GroupBox für die Kommunikation
    """
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._viewmodel = None
        self._init_ui()
    
    def set_viewmodel(self, viewmodel: FleetViewModel):
        """ViewModel setzen.
        
        Args:
            viewmodel: Flotten-ViewModel
        """
        self._viewmodel = viewmodel
        
        # ViewModel-Signale verbinden
        self._viewmodel.fleet_changed.connect(self._update_ui)
        self._viewmodel.uav_changed.connect(self._update_uav)
        
        # UI aktualisieren
        self._update_ui()
    
    def _init_ui(self):
        """UI initialisieren."""
        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Flotten-Gruppe
        self._fleet_group = QGroupBox("Flotte")
        fleet_layout = QFormLayout()
        
        # Flotten-ID
        self._fleet_id_label = QLabel()
        fleet_layout.addRow("Flotten-ID:", self._fleet_id_label)
        
        # Flotten-Name
        self._fleet_name_label = QLabel()
        fleet_layout.addRow("Flotten-Name:", self._fleet_name_label)
        
        # Flotten-Status
        self._fleet_status_label = QLabel()
        fleet_layout.addRow("Flotten-Status:", self._fleet_status_label)
        
        # Flotten-Modus
        self._fleet_mode_combo = QComboBox()
        self._fleet_mode_combo.addItems([mode.value for mode in FleetMode])
        self._fleet_mode_combo.currentTextChanged.connect(self._on_fleet_mode_changed)
        fleet_layout.addRow("Flotten-Modus:", self._fleet_mode_combo)
        
        # Flotten-Button
        self._fleet_button = QPushButton("Flotte initialisieren")
        self._fleet_button.clicked.connect(self._on_fleet_clicked)
        fleet_layout.addRow(self._fleet_button)
        
        self._fleet_group.setLayout(fleet_layout)
        layout.addWidget(self._fleet_group)
        
        # UAV-Tabelle
        self._uav_table = QTableWidget()
        self._uav_table.setColumnCount(8)
        self._uav_table.setHorizontalHeaderLabels([
            "UAV-ID",
            "UAV-Name",
            "UAV-Status",
            "UAV-Modus",
            "Position",
            "Geschwindigkeit",
            "Attitude",
            "Ressourcen"
        ])
        layout.addWidget(self._uav_table)
        
        # UAV-Button
        self._uav_button = QPushButton("UAV hinzufügen")
        self._uav_button.clicked.connect(self._on_uav_clicked)
        layout.addWidget(self._uav_button)
        
        # Ressourcen-Gruppe
        self._resources_group = QGroupBox("Ressourcen")
        resources_layout = QFormLayout()
        
        # Energie
        self._energy_label = QLabel()
        resources_layout.addRow("Energie:", self._energy_label)
        
        # Bandbreite
        self._bandwidth_label = QLabel()
        resources_layout.addRow("Bandbreite:", self._bandwidth_label)
        
        # Last
        self._load_label = QLabel()
        resources_layout.addRow("Last:", self._load_label)
        
        # Ressourcen-Button
        self._resources_button = QPushButton("Ressourcen verwalten")
        self._resources_button.clicked.connect(self._on_resources_clicked)
        resources_layout.addRow(self._resources_button)
        
        self._resources_group.setLayout(resources_layout)
        layout.addWidget(self._resources_group)
        
        # Kommunikations-Gruppe
        self._communication_group = QGroupBox("Kommunikation")
        communication_layout = QFormLayout()
        
        # Netzwerk-Topologie
        self._network_topology_combo = QComboBox()
        self._network_topology_combo.addItems([topology.value for topology in NetworkTopology])
        self._network_topology_combo.currentTextChanged.connect(self._on_network_topology_changed)
        communication_layout.addRow("Netzwerk-Topologie:", self._network_topology_combo)
        
        # Verschlüsselungs-Status
        self._encryption_status_label = QLabel()
        communication_layout.addRow("Verschlüsselungs-Status:", self._encryption_status_label)
        
        # Kommunikations-Button
        self._communication_button = QPushButton("Kommunikation verwalten")
        self._communication_button.clicked.connect(self._on_communication_clicked)
        communication_layout.addRow(self._communication_button)
        
        self._communication_group.setLayout(communication_layout)
        layout.addWidget(self._communication_group)
        
        # Koordinations-Button
        self._coordination_button = QPushButton("Flotte koordinieren")
        self._coordination_button.clicked.connect(self._on_coordination_clicked)
        layout.addWidget(self._coordination_button)
        
        # Kollisionsvermeidungs-Button
        self._collision_button = QPushButton("Kollisionen vermeiden")
        self._collision_button.clicked.connect(self._on_collision_clicked)
        layout.addWidget(self._collision_button)
    
    def _update_ui(self):
        """UI aktualisieren."""
        if not self._viewmodel:
            return
        
        # Flotten-Daten
        self._fleet_id_label.setText(self._viewmodel.fleet_id)
        self._fleet_name_label.setText(self._viewmodel.fleet_name)
        self._fleet_status_label.setText(self._viewmodel.fleet_status)
        self._fleet_mode_combo.setCurrentText(self._viewmodel.fleet_mode)
        
        # UAV-Tabelle
        self._uav_table.setRowCount(len(self._viewmodel.uavs))
        for i, uav in enumerate(self._viewmodel.uavs):
            self._uav_table.setItem(i, 0, QTableWidgetItem(uav["uav_id"]))
            self._uav_table.setItem(i, 1, QTableWidgetItem(uav["uav_name"]))
            self._uav_table.setItem(i, 2, QTableWidgetItem(uav["uav_status"]))
            self._uav_table.setItem(i, 3, QTableWidgetItem(uav["uav_mode"]))
            self._uav_table.setItem(i, 4, QTableWidgetItem(
                f"Lat: {uav['position']['latitude']:.6f}, "
                f"Lon: {uav['position']['longitude']:.6f}, "
                f"Alt: {uav['position']['altitude']:.2f}"
            ))
            self._uav_table.setItem(i, 5, QTableWidgetItem(
                f"vx: {uav['velocity']['vx']:.2f}, "
                f"vy: {uav['velocity']['vy']:.2f}, "
                f"vz: {uav['velocity']['vz']:.2f}"
            ))
            self._uav_table.setItem(i, 6, QTableWidgetItem(
                f"Roll: {uav['attitude']['roll']:.2f}, "
                f"Pitch: {uav['attitude']['pitch']:.2f}, "
                f"Yaw: {uav['attitude']['yaw']:.2f}"
            ))
            self._uav_table.setItem(i, 7, QTableWidgetItem(
                f"E: {uav['resources']['energy']:.2f}, "
                f"B: {uav['resources']['bandwidth']:.2f}, "
                f"L: {uav['resources']['load']:.2f}"
            ))
        
        # Ressourcen
        self._energy_label.setText(f"{self._viewmodel.resources['energy']:.2f}")
        self._bandwidth_label.setText(f"{self._viewmodel.resources['bandwidth']:.2f}")
        self._load_label.setText(f"{self._viewmodel.resources['load']:.2f}")
        
        # Kommunikation
        self._network_topology_combo.setCurrentText(self._viewmodel.communication["network_topology"])
        self._encryption_status_label.setText(self._viewmodel.communication["encryption_status"])
    
    def _update_uav(self, uav_id: str):
        """UAV-Daten aktualisieren.
        
        Args:
            uav_id: UAV-ID
        """
        self._update_ui()
    
    def _on_fleet_mode_changed(self, mode: str):
        """Flotten-Modus geändert.
        
        Args:
            mode: Neuer Flotten-Modus
        """
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.initialize_fleet({
                "fleet_id": self._viewmodel.fleet_id,
                "fleet_name": self._viewmodel.fleet_name,
                "fleet_mode": mode
            })
        except FleetError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_fleet_clicked(self):
        """Flotten-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.initialize_fleet({
                "fleet_id": "fleet_1",
                "fleet_name": "Test Fleet",
                "fleet_mode": FleetMode.COORDINATED.value
            })
        except FleetError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_uav_clicked(self):
        """UAV-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.add_uav({
                "uav_id": f"uav_{len(self._viewmodel.uavs) + 1}",
                "uav_name": f"Test UAV {len(self._viewmodel.uavs) + 1}",
                "uav_mode": UAVMode.AUTONOMOUS.value
            })
        except FleetError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_resources_clicked(self):
        """Ressourcen-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.manage_resources()
        except FleetError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_network_topology_changed(self, topology: str):
        """Netzwerk-Topologie geändert.
        
        Args:
            topology: Neue Netzwerk-Topologie
        """
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.initialize_fleet({
                "fleet_id": self._viewmodel.fleet_id,
                "fleet_name": self._viewmodel.fleet_name,
                "fleet_mode": self._viewmodel.fleet_mode
            })
        except FleetError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_communication_clicked(self):
        """Kommunikations-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.initialize_fleet({
                "fleet_id": self._viewmodel.fleet_id,
                "fleet_name": self._viewmodel.fleet_name,
                "fleet_mode": self._viewmodel.fleet_mode
            })
        except FleetError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_coordination_clicked(self):
        """Koordinations-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.coordinate_fleet()
        except FleetError as e:
            QMessageBox.critical(self, "Fehler", str(e))
    
    def _on_collision_clicked(self):
        """Kollisionsvermeidungs-Button geklickt."""
        if not self._viewmodel:
            return
        
        try:
            self._viewmodel.avoid_collisions()
        except FleetError as e:
            QMessageBox.critical(self, "Fehler", str(e)) 