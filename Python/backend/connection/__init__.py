"""
Connection-Modul für das RZGCS.

Dieses Modul implementiert die Verbindungsverwaltung für das RZGCS.
Es folgt der MVVM-Architektur und bietet eine klare Trennung zwischen
Datenmodellen, Geschäftslogik und Präsentation.
"""

from .models.connection_data import (
    ConnectionState,
    ConnectionParameters,
    ConnectionStatistics
)
from .enums import ConnectionType, ConnectionStatus
from .services.connection_service import ConnectionService
from .viewmodels.connection_viewmodel import ConnectionViewModel

__version__ = "1.0.0"
__author__ = "RZGCS Team"
__license__ = "MIT"

from .connection_manager import ConnectionManager
from .connection_types import (
    BaseConnection,
    SerialConnection,
    UDPConnection,
    TCPConnection,
    SimulatorConnection
)
from .connection_logger import ConnectionLogger
from .connection_security import ConnectionSecurity
from .bandwidth_manager import BandwidthManager

__all__ = [
    'ConnectionManager',
    'BaseConnection',
    'SerialConnection',
    'UDPConnection',
    'TCPConnection',
    'SimulatorConnection',
    'ConnectionLogger',
    'ConnectionSecurity',
    'BandwidthManager',
    'ConnectionType',
    'ConnectionStatus'
] 