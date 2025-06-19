#!/usr/bin/env python3
"""
DroneSignalHub - Zentraler Signal-Hub für Drohnen-Kommunikation

Diese Klasse dient als zentraler Signal-Hub für alle Drohnen-Kommunikation
und vereinheitlicht die Signalstruktur zwischen verschiedenen Komponenten.
"""

from PySide6.QtCore import QObject, Signal

class DroneSignalHub(QObject):
    """Signal-Hub für die Drohnen-Kommunikation"""
    
    # Verbindungssignale
    connection_established = Signal()
    connection_lost = Signal()
    error_occurred = Signal(str)
    
    # Telemetrie-Signale
    armed_changed = Signal(bool)
    flight_mode_changed = Signal(str)
    gps_info_changed = Signal(dict)
    battery_changed = Signal(dict)
    attitude_changed = Signal(dict)
    heading_changed = Signal(float)
    position_changed = Signal(dict)
    home_position_changed = Signal(dict)
    
    # Status-Signale
    statustext_received = Signal(str)
    telemetry_updated = Signal(dict)
    
    def __init__(self, parent=None):
        """Initialisierung des Signal-Hubs"""
        super().__init__(parent)
