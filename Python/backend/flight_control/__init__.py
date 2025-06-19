"""
Flight Control Package.
"""

from .services import (
    ControlService,
    SafetyService,
    MissionService,
    TelemetryService
)

from .enums import (
    FlightMode,
    ControlMode,
    EmergencyProcedure
)

from .connection.connection_manager import ConnectionManager, ConnectionType, ConnectionStatus

__all__ = [
    'ControlService',
    'SafetyService',
    'MissionService',
    'TelemetryService',
    'FlightMode',
    'ControlMode',
    'EmergencyProcedure',
    'ConnectionManager',
    'ConnectionType',
    'ConnectionStatus'
]

"""
Flugsteuerungsmodul.
Implementiert die Flugsteuerung basierend auf der MVVM-Architektur.
"""

from .models.flight_data import (
    Position,
    Waypoint,
    Mission,
    FlightState,
    ControlCommand,
    MissionPlan
)

from .enums import (
    FlightStatus,
    FlightMode,
    ConnectionStatus,
    ConnectionType,
    WaypointType,
    MissionStatus
)

from .config import (
    Config,
    ConnectionConfig,
    FlightConfig,
    MissionConfig,
    TelemetryConfig
)

from .services.flight_service import FlightService
from .services.mission_service import MissionService
from .services.telemetry_service import TelemetryService
from .services.connection_service import ConnectionService

from .viewmodels.flight_viewmodel import FlightViewModel
from .viewmodels.mission_viewmodel import MissionViewModel
from .viewmodels.telemetry_viewmodel import TelemetryViewModel
from .viewmodels.connection_viewmodel import ConnectionViewModel
from .viewmodels.main_viewmodel import MainViewModel

from .views.main_view import MainView

# FlightControlMain wird direkt in main definiert
from .main import FlightControlMain

__version__ = "0.1.0"
__author__ = "RZGCS Team"
__license__ = "MIT"

__all__ = ["FlightControlMain"]

"""Flottensteuerung.

Dieses Paket implementiert die Flottensteuerung für die Multi-UAV Funktionalität.
"""

# Dokumentation
"""Flotten-Dokumentation.

Diese Module implementieren die Dokumentation für die Flottensteuerung.
""" 