"""Frontend-ViewModel.

Dieses ViewModel stellt die Verbindung zwischen dem Frontend-Service und der Frontend-View her.
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
from flight_control.services.frontend_service import FrontendService

class FrontendViewModel(QObject):
    """Frontend-ViewModel.
    
    Dieses ViewModel stellt die Verbindung zwischen dem Frontend-Service und der Frontend-View her.
    
    Attributes:
        _service: Frontend-Service
        _fleet_data: Aktuelle Flottendaten
        
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
        self._service = None
        self._fleet_data = {}
    
    def set_service(self, service: FrontendService):
        """Service setzen.
        
        Args:
            service: Frontend-Service
        """
        self._service = service
        
        # Service-Signale verbinden
        self._service.fleet_changed.connect(self._update_fleet)
        self._service.uav_changed.connect(self._update_uav)
        self._service.frontend_connected.connect(self._on_frontend_connected)
        self._service.frontend_disconnected.connect(self._on_frontend_disconnected)
    
    @Property(bool, notify=frontend_connected)
    def frontend_connected(self) -> bool:
        """Frontend verbunden."""
        return self._service.frontend_connected if self._service else False
    
    @Property(str, notify=fleet_changed)
    def fleet_id(self) -> str:
        """Flotten-ID."""
        return self._fleet_data.get("fleet_id", "")
    
    @Property(str, notify=fleet_changed)
    def fleet_name(self) -> str:
        """Flotten-Name."""
        return self._fleet_data.get("fleet_name", "")
    
    @Property(str, notify=fleet_changed)
    def fleet_status(self) -> str:
        """Flotten-Status."""
        return self._fleet_data.get("fleet_status", FleetStatus.INACTIVE.value)
    
    @Property(str, notify=fleet_changed)
    def fleet_mode(self) -> str:
        """Flotten-Modus."""
        return self._fleet_data.get("fleet_mode", FleetMode.MANUAL.value)
    
    @Property(list, notify=fleet_changed)
    def uavs(self) -> List[Dict[str, Any]]:
        """UAVs."""
        return self._fleet_data.get("uavs", [])
    
    @Property(dict, notify=fleet_changed)
    def resources(self) -> Dict[str, Any]:
        """Ressourcen."""
        return self._fleet_data.get("resources", {})
    
    @Property(dict, notify=fleet_changed)
    def communication(self) -> Dict[str, Any]:
        """Kommunikation."""
        return self._fleet_data.get("communication", {})
    
    def update_fleet_data(self, fleet_data: Dict[str, Any]):
        """Flottendaten aktualisieren.
        
        Args:
            fleet_data: Flottendaten
        """
        self._fleet_data = fleet_data
        self.fleet_changed.emit()
    
    def update_uav_data(self, uav_id: str, uav_data: Dict[str, Any]):
        """UAV-Daten aktualisieren.
        
        Args:
            uav_id: UAV-ID
            uav_data: UAV-Daten
        """
        # UAV finden
        uavs = self._fleet_data.get("uavs", [])
        uav = next((u for u in uavs if u["uav_id"] == uav_id), None)
        if not uav:
            return
        
        # UAV-Daten aktualisieren
        uav.update(uav_data)
        
        # Signal auslösen
        self.uav_changed.emit(uav_id)
    
    def _update_fleet(self):
        """Flottendaten aktualisieren."""
        if not self._service:
            return
        
        self._fleet_data = self._service.get_fleet_data()
        self.fleet_changed.emit()
    
    def _update_uav(self, uav_id: str):
        """UAV-Daten aktualisieren.
        
        Args:
            uav_id: UAV-ID
        """
        if not self._service:
            return
        
        uav_data = self._service.get_uav_data(uav_id)
        self.update_uav_data(uav_id, uav_data)
    
    def _on_frontend_connected(self):
        """Frontend verbunden."""
        self.frontend_connected.emit()
    
    def _on_frontend_disconnected(self):
        """Frontend getrennt."""
        self.frontend_disconnected.emit() 