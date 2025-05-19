import logging
from PySide6.QtCore import QObject, Signal, Slot, Property
from datetime import datetime

class Logger(QObject):
    logAdded = Signal(str)
    logsChanged = Signal()

    def __init__(self):
        super().__init__()
        self._logs = []
        self._max_logs = 1000  # Maximum number of logs to keep

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

    @Slot(str)
    def addLog(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)  # Print to console
        
        # Add to logs list
        self._logs.append(log_entry)
        
        # Keep only the last max_logs entries
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]
        
        # Emit signals
        self.logAdded.emit(log_entry)
        self.logsChanged.emit()
        print(f"Current log count: {len(self._logs)}")

    @Slot(result=str)
    def getLogs(self):
        return "\n".join(self._logs)

    @Slot()
    def clear(self):
        self._logs = []
        self.logsChanged.emit()
        self.addLog("Logs cleared")
