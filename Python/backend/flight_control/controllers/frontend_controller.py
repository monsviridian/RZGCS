"""Frontend-Controller.

Dieser Controller implementiert die Verbindung zwischen Frontend-Service und Frontend-View.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

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
from flight_control.viewmodels.frontend_viewmodel import FrontendViewModel
from flight_control.views.frontend_view import FrontendView

class FrontendController(QObject):
    """Frontend-Controller.
    
    Dieser Controller implementiert die Verbindung zwischen Frontend-Service und Frontend-View.
    
    Attributes:
        _service: Frontend-Service
        _viewmodel: Frontend-ViewModel
        _view: Frontend-View
        _update_timer: Timer für regelmäßige Updates
    """
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        
        # Service
        self._service = FrontendService()
        
        # ViewModel
        self._viewmodel = FrontendViewModel()
        self._viewmodel.set_service(self._service)
        
        # View
        self._view = FrontendView()
        self._view.set_viewmodel(self._viewmodel)
        
        # Update-Timer
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update)
        self._update_timer.start(100)  # 100ms
    
    def show(self):
        """View anzeigen."""
        self._view.show()
    
    def _update(self):
        """Regelmäßiges Update."""
        try:
            # Frontend verbunden
            if not self._service.frontend_connected:
                return
            
            # Flottendaten aktualisieren
            fleet_data = self._service.get_fleet_data()
            self._viewmodel.update_fleet_data(fleet_data)
            
            # UAV-Daten aktualisieren
            for uav in fleet_data["uavs"]:
                self._viewmodel.update_uav_data(uav["uav_id"], uav)
        except FleetError as e:
            print(f"Fehler beim Update: {e}")
    
    def connect_frontend(self):
        """Frontend verbinden."""
        self._service.connect_frontend()
    
    def disconnect_frontend(self):
        """Frontend trennen."""
        self._service.disconnect_frontend()
    
    def update_fleet_data(self, fleet_data: FleetData):
        """Flottendaten aktualisieren.
        
        Args:
            fleet_data: Flottendaten
        """
        self._service.update_fleet_data(fleet_data)
    
    def update_uav_data(self, uav_id: str, uav_data: UAVData):
        """UAV-Daten aktualisieren.
        
        Args:
            uav_id: UAV-ID
            uav_data: UAV-Daten
        """
        self._service.update_uav_data(uav_id, uav_data) 