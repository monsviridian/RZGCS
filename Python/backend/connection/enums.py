"""
Enums für das Verbindungsmanagement
"""

from enum import Enum

class ConnectionType(Enum):
    """Verfügbare Verbindungstypen"""
    SERIAL = "Serial"
    UDP = "UDP"
    TCP = "TCP"
    SIMULATOR = "Simulator"

class ConnectionStatus(Enum):
    """Verbindungsstatus"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error" 