import logging
from PySide6.QtCore import QObject, Signal, Slot, Property
from datetime import datetime
import re

class Logger(QObject):
    logAdded = Signal(str)
    logsChanged = Signal()
    systemInfoLogsChanged = Signal()

    def __init__(self):
        super().__init__()
        self._logs = []
        self._system_info_logs = []
        self._max_logs = 1000  # Maximum number of logs to keep
        
        # Patterns für wichtige Systeminformationen
        self._system_info_patterns = [
            r"Frame:", 
            r"RCOut:", 
            r"MicoAir", 
            r"ChibiOS:", 
            r"ArduCopter", 
            r"PreArm:"
        ]
        
        # Debug-Log für Systeminfo-Anzeige
        self._system_info_logs.append("[SYSTEMINFO] Waiting for FC system information...")
        print("Logger initialized with system info filter")

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        self.addLog("Logger initialized")

    @Property('QVariantList', notify=logsChanged)
    def logs(self):
        return self._logs
        
    @Property('QVariantList', notify=systemInfoLogsChanged)
    def system_info_logs(self):
        return self._system_info_logs

    @Slot(str)
    def addLog(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)  # Print to console
        
        # Add to logs list
        self._logs.append(log_entry)
        
        # Check if this is a system info log we're interested in
        is_system_info = False
        for pattern in self._system_info_patterns:
            if re.search(pattern, message):
                is_system_info = True
                print(f"SYSTEMINFO LOG MATCHED: {pattern} in {message}")
                break
                
        if is_system_info:
            self._system_info_logs.append(log_entry)
            print(f"Added system info log, count: {len(self._system_info_logs)}")
            self.systemInfoLogsChanged.emit()
        
        # Keep only the last max_logs entries
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]
            
        if len(self._system_info_logs) > self._max_logs:
            self._system_info_logs = self._system_info_logs[-self._max_logs:]
        
        # Emit signals
        self.logAdded.emit(log_entry)
        self.logsChanged.emit()

    @Slot(result=str)
    def getLogs(self):
        return "\n".join(self._logs)

    @Slot()
    def clear(self):
        self._logs = []
        self._system_info_logs = []
        self.logsChanged.emit()
        self.systemInfoLogsChanged.emit()
        self.addLog("Logs cleared")
        
    @Slot(result='QVariantList')
    def getSystemInfoLogs(self):
        """Gibt nur die Logs zurück, die Systeminformationen enthalten"""
        # Wenn keine Systeminformationen vorhanden sind, geben wir einen Hinweis zurück
        if not self._system_info_logs:
            return ["Waiting for FC system information..."]
        return self._system_info_logs
        
    @Slot(str)
    def addSystemInfoLog(self, message):
        """Fügt manuell ein System-Info Log hinzu (für Tests)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [SYSTEM INFO] {message}"
        self._system_info_logs.append(log_entry)
        print(f"Manually added system info log: {log_entry}")
        self.systemInfoLogsChanged.emit()
        return True
