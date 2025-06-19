"""
Drone Connection Interface
Definiert das Interface für die Kommunikation mit Drohnen, unabhängig vom verwendeten Backend
"""

from typing import Protocol, Callable, Dict, Any, List, Optional, runtime_checkable

@runtime_checkable
class DroneConnectionInterface(Protocol):
    """Interface für die Kommunikation mit Drohnen
    
    Dieses Protocol definiert die Schnittstelle, die jeder Drohnen-Connector
    implementieren muss. Im Gegensatz zu ABC vermeidet Protocol Metaklassen-Konflikte
    mit QObject und anderen Klassen.
    """

    # Callback-Registrierungsmethoden
    def register_connection_callback(self, callback: Callable[[], None]) -> None:
        """Registriert einen Callback für Verbindungs-Status-Änderungen"""
        ...
        
    def register_disconnection_callback(self, callback: Callable[[], None]) -> None:
        """Registriert einen Callback für Verbindungs-Verlust"""
        ...
        
    def register_telemetry_callback(self, telemetry_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Registriert einen Callback für einen bestimmten Telemetrie-Typ
        
        Args:
            telemetry_type: Typ der Telemetrie (z.B. 'position', 'attitude', 'battery')
            callback: Funktion, die aufgerufen wird, wenn neue Daten verfügbar sind
        """
        ...
        
    def register_statustext_callback(self, callback: Callable[[str], None]) -> None:
        """Registriert einen Callback für Status-Texte"""
        ...
    
    # Verbindungsmethoden
    def connect(self, connection_string: str) -> bool:
        """Stellt eine Verbindung zur Drohne her
        
        Args:
            connection_string: Verbindungsstring (z.B. 'udp://:14540')
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich hergestellt wurde
        """
        ...
    
    def connect_serial(self, port: str, baudrate: int) -> bool:
        """Stellt eine Verbindung zur Drohne über einen seriellen Port her
        
        Args:
            port: COM-Port oder Device (z.B. COM3, /dev/ttyACM0)
            baudrate: Baudrate (z.B. 57600, 115200)
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich hergestellt wurde
        """
        ...
    
    def disconnect(self) -> bool:
        """Trennt die Verbindung zur Drohne
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich getrennt wurde
        """
        ...
    
    # Drohnen-Steuerungsmethoden
    def arm(self) -> bool:
        """Armiert die Drohne
        
        Returns:
            bool: True, wenn das Armieren erfolgreich war
        """
        ...
    
    def disarm(self) -> bool:
        """Disarmiert die Drohne
        
        Returns:
            bool: True, wenn das Disarmieren erfolgreich war
        """
        ...
    
    def takeoff(self) -> bool:
        """Lässt die Drohne starten
        
        Returns:
            bool: True, wenn der Start erfolgreich initiiert wurde
        """
        ...
    
    def land(self) -> bool:
        """Lässt die Drohne landen
        
        Returns:
            bool: True, wenn die Landung erfolgreich initiiert wurde
        """
        ...
    
    # Die is_connected-Methode ist bereits oben definiert und
    # es sollte keine doppelte Definition geben
