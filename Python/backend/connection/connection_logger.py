"""
Verbindungsprotokollierung
"""

import logging
from datetime import datetime
from typing import Optional

class ConnectionLogger:
    """Verbindungsprotokollierung"""
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Initialisiert den ConnectionLogger
        
        Args:
            log_level: Logging-Level (default: logging.INFO)
        """
        self.log_file: Optional[file] = None
        self.log_level = log_level
        logging.basicConfig(level=self.log_level)
    
    def start_logging(self, connection_id: str) -> None:
        """
        Startet das Logging für eine Verbindung
        
        Args:
            connection_id: Eindeutige ID für die Verbindung
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"connection_{connection_id}_{timestamp}.log"
        self.log_file = open(filename, 'w')
    
    def log_connection_event(self, event_type: str, details: str) -> None:
        """
        Protokolliert ein Verbindungsereignis
        
        Args:
            event_type: Typ des Ereignisses
            details: Details zum Ereignis
        """
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} - {event_type}: {details}\n"
        
        if self.log_file:
            self.log_file.write(log_entry)
            self.log_file.flush()
        
        logging.info(log_entry.strip())
    
    def stop_logging(self) -> None:
        """Beendet das Logging"""
        if self.log_file:
            self.log_file.close()
            self.log_file = None 