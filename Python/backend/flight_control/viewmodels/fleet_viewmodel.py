"""Flotten-ViewModel.

Dieses ViewModel stellt die Verbindung zwischen dem Flotten-Service und der View her.
Es verwaltet den UI-Zustand und leitet Benutzerinteraktionen an den Service weiter.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, Property

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
from ..services.fleet_service import FleetService

class FleetViewModel(QObject):
    """Flotten-ViewModel.
    
    Dieses ViewModel stellt die Verbindung zwischen dem Flotten-Service und der View her.
    
    Attributes:
        _service: Flotten-Service
        _fleet_data: Aktuelle Flottendaten
        
    Signals:
        fleet_changed: Wird ausgelöst, wenn sich die Flottendaten ändern
        uav_changed: Wird ausgelöst, wenn sich die UAV-Daten ändern
    """
    
    # Signale
    fleet_changed = Signal()
    uav_changed = Signal(str)  # UAV-ID
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._service = None
        self._fleet_data = None
    
    def set_service(self, service: FleetService):
        """Service setzen.
        
        Args:
            service: Flotten-Service
        """
        self._service = service
        
        # Service-Signale verbinden
        self._service.fleet_changed.connect(self._update_fleet)
        self._service.uav_changed.connect(self._update_uav)
    
    @Property(str, notify=fleet_changed)
    def fleet_id(self) -> str:
        """Flotten-ID."""
        return self._fleet_data.fleet_id if self._fleet_data else ""
    
    @Property(str, notify=fleet_changed)
    def fleet_name(self) -> str:
        """Flotten-Name."""
        return self._fleet_data.fleet_name if self._fleet_data else ""
    
    @Property(str, notify=fleet_changed)
    def fleet_status(self) -> str:
        """Flotten-Status."""
        return self._fleet_data.fleet_status.value if self._fleet_data else FleetStatus.INACTIVE.value
    
    @Property(str, notify=fleet_changed)
    def fleet_mode(self) -> str:
        """Flotten-Modus."""
        return self._fleet_data.fleet_mode.value if self._fleet_data else FleetMode.MANUAL.value
    
    @Property(list, notify=fleet_changed)
    def uavs(self) -> List[Dict[str, Any]]:
        """UAVs."""
        if not self._fleet_data:
            return []
        
        return [{
            "uav_id": uav.uav_id,
            "uav_name": uav.uav_name,
            "uav_status": uav.uav_status.value,
            "uav_mode": uav.uav_mode.value,
            "position": {
                "latitude": uav.position.latitude,
                "longitude": uav.position.longitude,
                "altitude": uav.position.altitude
            },
            "velocity": {
                "vx": uav.velocity.vx,
                "vy": uav.velocity.vy,
                "vz": uav.velocity.vz
            },
            "attitude": {
                "roll": uav.attitude.roll,
                "pitch": uav.attitude.pitch,
                "yaw": uav.attitude.yaw
            },
            "resources": {
                "energy": uav.resources.energy,
                "bandwidth": uav.resources.bandwidth,
                "load": uav.resources.load
            }
        } for uav in self._fleet_data.uavs]
    
    @Property(dict, notify=fleet_changed)
    def resources(self) -> Dict[str, Any]:
        """Ressourcen."""
        if not self._fleet_data:
            return {}
        
        return {
            "energy": self._fleet_data.resources.energy,
            "bandwidth": self._fleet_data.resources.bandwidth,
            "load": self._fleet_data.resources.load
        }
    
    @Property(dict, notify=fleet_changed)
    def communication(self) -> Dict[str, Any]:
        """Kommunikation."""
        if not self._fleet_data:
            return {}
        
        return {
            "network_topology": self._fleet_data.communication.network_topology.value,
            "encryption_status": self._fleet_data.communication.encryption_status.value
        }
    
    def initialize_fleet(self, fleet_config: Dict[str, Any]):
        """Flotte initialisieren.
        
        Args:
            fleet_config: Flotten-Konfiguration
        """
        if not self._service:
            raise FleetCommandError("No service set")
        
        try:
            self._service.initialize_fleet(fleet_config)
        except FleetError as e:
            self._handle_error(str(e))
    
    def add_uav(self, uav_config: Dict[str, Any]):
        """UAV zur Flotte hinzufügen.
        
        Args:
            uav_config: UAV-Konfiguration
        """
        if not self._service:
            raise FleetCommandError("No service set")
        
        try:
            self._service.add_uav(uav_config)
        except FleetError as e:
            self._handle_error(str(e))
    
    def remove_uav(self, uav_id: str):
        """UAV aus Flotte entfernen.
        
        Args:
            uav_id: UAV-ID
        """
        if not self._service:
            raise FleetCommandError("No service set")
        
        try:
            self._service.remove_uav(uav_id)
        except FleetError as e:
            self._handle_error(str(e))
    
    def coordinate_fleet(self):
        """Flotte koordinieren."""
        if not self._service:
            raise FleetCommandError("No service set")
        
        try:
            self._service.coordinate_fleet()
        except FleetError as e:
            self._handle_error(str(e))
    
    def manage_resources(self):
        """Ressourcen verwalten."""
        if not self._service:
            raise FleetCommandError("No service set")
        
        try:
            self._service.manage_resources()
        except FleetError as e:
            self._handle_error(str(e))
    
    def avoid_collisions(self):
        """Kollisionen vermeiden."""
        if not self._service:
            raise FleetCommandError("No service set")
        
        try:
            self._service.avoid_collisions()
        except FleetError as e:
            self._handle_error(str(e))
    
    def _update_fleet(self):
        """Flottendaten aktualisieren."""
        self._fleet_data = self._service.fleet_data
        self.fleet_changed.emit()
    
    def _update_uav(self, uav_id: str):
        """UAV-Daten aktualisieren.
        
        Args:
            uav_id: UAV-ID
        """
        self._fleet_data = self._service.fleet_data
        self.uav_changed.emit(uav_id)
    
    def _handle_error(self, error_message: str):
        """Fehler behandeln.
        
        Args:
            error_message: Fehlermeldung
        """
        if self._fleet_data:
            self._fleet_data.fleet_status = FleetStatus.ERROR
            self.fleet_changed.emit() 