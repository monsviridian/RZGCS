"""
Bandbreitenmanagement
"""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MessageStats:
    """Statistiken für eine Nachricht"""
    size: int
    timestamp: datetime
    priority: int

class BandwidthManager:
    """Bandbreitenmanagement"""
    
    def __init__(self, max_bandwidth: int = 1000000):  # 1 Mbps default
        """
        Initialisiert den BandwidthManager
        
        Args:
            max_bandwidth: Maximale Bandbreite in Bits pro Sekunde
        """
        self.max_bandwidth = max_bandwidth
        self.current_usage = 0
        self.message_history: Dict[str, MessageStats] = {}
        self.message_priorities = {
            'HEARTBEAT': 1,
            'COMMAND': 2,
            'TELEMETRY': 3,
            'LOG': 4
        }
    
    def can_send_message(self, message_type: str, message_size: int) -> bool:
        """
        Prüft ob eine Nachricht gesendet werden kann
        
        Args:
            message_type: Typ der Nachricht
            message_size: Größe der Nachricht in Bytes
            
        Returns:
            True wenn die Nachricht gesendet werden kann, sonst False
        """
        # Alte Nachrichten aus der Historie entfernen
        self._cleanup_old_messages()
        
        # Bandbreitenverbrauch berechnen
        if self.current_usage + message_size > self.max_bandwidth:
            return False
        
        # Nachricht zur Historie hinzufügen
        self.message_history[message_type] = MessageStats(
            size=message_size,
            timestamp=datetime.now(),
            priority=self.message_priorities.get(message_type, 5)
        )
        
        self.current_usage += message_size
        return True
    
    def _cleanup_old_messages(self) -> None:
        """Entfernt alte Nachrichten aus der Historie"""
        current_time = datetime.now()
        old_messages = [
            msg_type for msg_type, stats in self.message_history.items()
            if current_time - stats.timestamp > timedelta(seconds=1)
        ]
        
        for msg_type in old_messages:
            self.current_usage -= self.message_history[msg_type].size
            del self.message_history[msg_type]
    
    def reset_usage(self) -> None:
        """Setzt die Bandbreitennutzung zurück"""
        self.current_usage = 0
        self.message_history.clear()
    
    def get_bandwidth_usage(self) -> float:
        """
        Gibt die aktuelle Bandbreitennutzung zurück
        
        Returns:
            Bandbreitennutzung in Prozent
        """
        return (self.current_usage / self.max_bandwidth) * 100
    
    def get_message_priority(self, message_type: str) -> int:
        """
        Gibt die Priorität einer Nachricht zurück
        
        Args:
            message_type: Typ der Nachricht
            
        Returns:
            Priorität der Nachricht
        """
        return self.message_priorities.get(message_type, 5) 