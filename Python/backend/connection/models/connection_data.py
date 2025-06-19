"""
Datenmodelle für die Verbindungsverwaltung.
Implementiert die Model-Schicht der MVVM-Architektur.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ConnectionType(Enum):
    """Verbindungstypen."""
    SERIAL = "serial"
    UDP = "udp"
    TCP = "tcp"
    MAVLINK = "mavlink"

class ConnectionStatus(Enum):
    """Verbindungsstatus."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class ConnectionParameters:
    """Verbindungsparameter."""
    type: ConnectionType
    port: Optional[str] = None
    baudrate: Optional[int] = None
    host: Optional[str] = None
    port_number: Optional[int] = None
    timeout: float = 5.0
    retry_count: int = 3
    auto_reconnect: bool = True

@dataclass
class ConnectionState:
    """Verbindungszustand."""
    status: ConnectionStatus
    type: ConnectionType
    parameters: ConnectionParameters
    last_heartbeat: Optional[datetime] = None
    error_message: Optional[str] = None
    is_connected: bool = False
    is_connecting: bool = False
    is_error: bool = False

@dataclass
class ConnectionStatistics:
    """Verbindungsstatistiken."""
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    errors: int = 0
    connection_time: float = 0.0
    last_error_time: Optional[datetime] = None
    last_error_message: Optional[str] = None

@dataclass
class ConnectionInfo:
    """Verbindungsinformationen."""
    state: ConnectionState
    statistics: ConnectionStatistics
    parameters: ConnectionParameters
    start_time: datetime
    last_update: datetime
    is_active: bool = False
    is_healthy: bool = False
    latency: float = 0.0
    signal_strength: float = 0.0 