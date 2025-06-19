"""Backend-KeyVerifier.

Dieser KeyVerifier implementiert die Verbindung zwischen Backend-KeyValidator und Backend-KeySigner.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, Property

from flight_control.models.fleet_data import (
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
from flight_control.keysigner.backend_keysigner import BackendKeySigner

class BackendKeyVerifier(QObject):
    """Backend-KeyVerifier.
    
    Dieser KeyVerifier implementiert die Verbindung zwischen Backend-KeyValidator und Backend-KeySigner.
    
    Attributes:
        _backend_keysigner: Backend-KeySigner
        _frontend_connected: Frontend verbunden
        
    Signals:
        fleet_changed: Wird ausgelöst, wenn sich die Flottendaten ändern
        uav_changed: Wird ausgelöst, wenn sich die UAV-Daten ändern
        frontend_connected: Wird ausgelöst, wenn sich das Frontend verbindet
        frontend_disconnected: Wird ausgelöst, wenn sich das Frontend trennt
    """
    
    # Signale
    fleet_changed = Signal()
    uav_changed = Signal(str)  # UAV-ID
    frontend_connected = Signal()
    frontend_disconnected = Signal()
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._backend_keysigner = BackendKeySigner()
        self._frontend_connected = False
        
        # Backend-KeySigner-Signale verbinden
        self._backend_keysigner.fleet_changed.connect(self._on_fleet_changed)
        self._backend_keysigner.uav_changed.connect(self._on_uav_changed)
        self._backend_keysigner.frontend_connected.connect(self._on_frontend_connected)
        self._backend_keysigner.frontend_disconnected.connect(self._on_frontend_disconnected)
    
    @Property(bool, notify=frontend_connected)
    def frontend_connected(self) -> bool:
        """Frontend verbunden."""
        return self._frontend_connected
    
    def connect_frontend(self):
        """Frontend verbinden."""
        self._backend_keysigner.connect_frontend()
    
    def disconnect_frontend(self):
        """Frontend trennen."""
        self._backend_keysigner.disconnect_frontend()
    
    def get_fleet_data(self) -> Dict[str, Any]:
        """Flottendaten abrufen.
        
        Returns:
            Flottendaten
        """
        return self._backend_keysigner.get_fleet_data()
    
    def get_uav_data(self, uav_id: str) -> Dict[str, Any]:
        """UAV-Daten abrufen.
        
        Args:
            uav_id: UAV-ID
            
        Returns:
            UAV-Daten
        """
        return self._backend_keysigner.get_uav_data(uav_id)
    
    def update_fleet_data(self, fleet_data: Dict[str, Any]):
        """Flottendaten aktualisieren.
        
        Args:
            fleet_data: Flottendaten
        """
        self._backend_keysigner.update_fleet_data(fleet_data)
    
    def update_uav_data(self, uav_id: str, uav_data: Dict[str, Any]):
        """UAV-Daten aktualisieren.
        
        Args:
            uav_id: UAV-ID
            uav_data: UAV-Daten
        """
        self._backend_keysigner.update_uav_data(uav_id, uav_data)
    
    def _on_fleet_changed(self):
        """Flottendaten geändert."""
        self.fleet_changed.emit()
    
    def _on_uav_changed(self, uav_id: str):
        """UAV-Daten geändert.
        
        Args:
            uav_id: UAV-ID
        """
        self.uav_changed.emit(uav_id)
    
    def _on_frontend_connected(self):
        """Frontend verbunden."""
        self._frontend_connected = True
        self.frontend_connected.emit()
    
    def _on_frontend_disconnected(self):
        """Frontend getrennt."""
        self._frontend_connected = False
        self.frontend_disconnected.emit() 