from PySide6.QtCore import QObject, Signal, Slot, Property, QStringListModel, QTimer
from datetime import datetime
import logging
import json
from typing import Optional, List, Dict
import os

class Logger(QObject):
    """
    Erweiterter Logger mit Qt-Integration und Datei-Logging.
    
    Signals:
        logAdded: Signal wird bei neuem Log-Eintrag emittiert
        errorOccurred: Signal wird bei Fehlern emittiert
        logsChanged: Signal wird bei Änderung der Logs emittiert
    """
    
    logAdded = Signal(str)
    errorOccurred = Signal(str)
    logsChanged = Signal()  # Neues Signal für QML-Binding
    
    def __init__(self, parent: Optional[QObject] = None, 
                 log_file: Optional[str] = None,
                 max_entries: int = 1000,
                 log_level: int = logging.INFO) -> None:
        """
        Initializes the logger.
        
        Args:
            parent: Qt parent object
            log_file: Path to log file
            max_entries: Maximum number of log entries in memory
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        super().__init__(parent)
        self._logs = []  # Simple list instead of QStringListModel
        self._max_entries = max_entries
        self._stats: Dict[str, int] = {
            "info": 0,
            "warning": 0,
            "error": 0,
            "debug": 0
        }
        
        # Setup Python logger
        self._logger = logging.getLogger("DroneLogger")
        self._logger.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self._logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            self._setup_file_handler(log_file)
            
        # Initial log
        self.info("Logger initialized")
    
    def _setup_file_handler(self, log_file: str) -> None:
        """Richtet das Logging in eine Datei ein."""
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            self._logger.addHandler(file_handler)
        except Exception as e:
            self.error(f"Fehler beim Einrichten des File-Handlers: {str(e)}")
    
    def _should_throttle(self, level: str, message: str) -> bool:
        """Check if a log message should be throttled."""
        key = f"{level}:{message}"
        current_time = datetime.now().timestamp()
        
        if key in self._last_log_time:
            time_diff = current_time - self._last_log_time[key]
            if time_diff < self._log_throttle_interval:
                return True
                
        self._last_log_time[key] = current_time
        return False
    
    def _add_to_model(self, level: str, message: str) -> None:
        """Adds a log entry to the model."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # Update statistics
        self._stats[level.lower()] += 1
        
        # Add new log at the end
        self._logs.append(log_message)
        
        # Emit signals
        self.logAdded.emit(log_message)
        self.logsChanged.emit()  # Important for QML binding
        
        # Debug-Ausgabe
        print(f"Log added: {log_message}")
        print(f"Current log count: {len(self._logs)}")
    
    @Slot(str)
    def debug(self, message: str) -> None:
        """Loggt eine Debug-Nachricht."""
        self._logger.debug(message)
        self._add_to_model("DEBUG", message)
    
    @Slot(str)
    def info(self, message: str) -> None:
        """Loggt eine Info-Nachricht."""
        self._logger.info(message)
        self._add_to_model("INFO", message)
    
    @Slot(str)
    def warning(self, message: str) -> None:
        """Loggt eine Warnung."""
        self._logger.warning(message)
        self._add_to_model("WARNING", message)
    
    @Slot(str)
    def error(self, message: str) -> None:
        """Loggt einen Fehler."""
        self._logger.error(message)
        self._add_to_model("ERROR", message)
        self.errorOccurred.emit(message)
    
    @Property('QVariantList', notify=logsChanged)
    def logs(self) -> List[str]:
        """Gibt alle Log-Einträge zurück."""
        return self._logs
    
    @Property(dict)
    def statistics(self) -> Dict[str, int]:
        """Gibt Logging-Statistiken zurück."""
        return self._stats
    
    def export_logs(self, filepath: str) -> None:
        """Exportiert alle Logs in eine JSON-Datei."""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'logs': self.logs,
                    'statistics': self.statistics,
                    'exported_at': datetime.now().isoformat()
                }, f, indent=4)
        except Exception as e:
            self.error(f"Fehler beim Exportieren der Logs: {str(e)}")
    
    @Slot()
    def clear(self) -> None:
        """Löscht alle Log-Einträge."""
        self._logs = []
        for key in self._stats:
            self._stats[key] = 0
        self.logsChanged.emit()
        self.info("Logs cleared")
