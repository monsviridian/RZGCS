#!/usr/bin/env python3
"""
DroneSignalHub - Eine zentrale Signal-Hub-Klasse für Drohnensignale
"""

from PySide6.QtCore import QObject, Signal


class DroneSignalHub(QObject):
    """
    Eine zentrale Signal-Hub-Klasse, die alle Signale für die Drohnenkommunikation bereitstellt.
    Diese Klasse vermeidet Metaklassen-Konflikte zwischen QObject und Protocol.
    """
    
    # Verbindungssignale
    connection_established = Signal()
    connection_lost = Signal()
    error_occurred = Signal(str)
    
    # Telemetrie-Signale
    telemetry_updated = Signal(str, dict)  # telemetry_type, data
    statustext_received = Signal(str)
    
    # Spezifische Telemetrie-Signale
    armed_changed = Signal(bool)
    flight_mode_changed = Signal(str)
    gps_info_changed = Signal(dict)
    battery_changed = Signal(dict)
    attitude_changed = Signal(dict)
    heading_changed = Signal(float)
    position_changed = Signal(dict)
    parameters_updated = Signal(list)  # Parameter-Liste
    home_position_changed = Signal(dict)
    
    def __init__(self, parent=None):
        """Initialisiert den DroneSignalHub"""
        super().__init__(parent)
        
        # Verbinde spezifische Signale mit dem allgemeinen Signal
        self.armed_changed.connect(lambda value: self.telemetry_updated.emit('armed', {'armed': value}))
        self.flight_mode_changed.connect(lambda mode: self.telemetry_updated.emit('flight_mode', {'mode': mode}))
        self.gps_info_changed.connect(lambda info: self.telemetry_updated.emit('gps_info', info))
        self.battery_changed.connect(lambda info: self.telemetry_updated.emit('battery', info))
        self.attitude_changed.connect(lambda info: self.telemetry_updated.emit('attitude', info))
        self.heading_changed.connect(lambda value: self.telemetry_updated.emit('heading', {'heading': value}))
        self.position_changed.connect(lambda info: self.telemetry_updated.emit('position', info))
        self.home_position_changed.connect(lambda info: self.telemetry_updated.emit('home_position', info))
        self.parameters_updated.connect(lambda params: self.telemetry_updated.emit('parameters', {'parameters': params}))
