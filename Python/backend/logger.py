import logging
from PySide6.QtCore import QObject, Signal, Slot, Property
from datetime import datetime
import re

class Logger(QObject):
    logAdded = Signal(str)
    logsChanged = Signal()
    systemInfoLogsChanged = Signal()
    # New signal for forwarding to MessageManager
    messageForwarded = Signal(str, int)  # message, type

    def __init__(self):
        super().__init__()
        self._logs = []
        self._system_info_logs = []
        self._max_logs = 1000  # Maximum number of logs to keep
        self._message_callback = None  # Callback for forwarding to MessageManager
        
        # Patterns für wichtige Systeminformationen
        self._system_info_patterns = [
            # Original-Patterns
            r"Frame:", 
            r"RCOut:", 
            r"MicoAir", 
            r"ChibiOS:", 
            r"ArduCopter", 
            r"PreArm:",
            # MAVSDK-Server-bezogene Nachrichten
            r"\[SYSTEM INFO\]",
            r"MAVSDK-Server",
            r"serial://",
            r"Verbindungsversuch",
            r"Baudrate",
            r"connected",
            r"Connected"
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

    def set_message_callback(self, callback):
        """Setzt eine Callback-Funktion für die Weiterleitung an MessageManager"""
        self._message_callback = callback
        print("[DEBUG] Logger: Message callback gesetzt")

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
        
        # Sicheres Ausgeben auf die Konsole
        try:
            print(log_entry)  # Print to console
        except UnicodeEncodeError:
            # Fallback für Windows-Konsole, die Unicode nicht vollständig unterstützt
            safe_entry = log_entry.encode('ascii', 'replace').decode('ascii')
            print(safe_entry)
        
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
        
        # Forward to MessageManager if callback is set
        if self._message_callback:
            try:
                # Determine message type based on content
                message_type = self._determine_message_type(message)
                self._message_callback(message, message_type)
            except Exception as e:
                print(f"[ERROR] Logger: Fehler beim Weiterleiten an MessageManager: {e}")

    def _determine_message_type(self, message):
        """Bestimmt den Message-Typ basierend auf dem Inhalt"""
        message_lower = message.lower()
        
        # Error messages
        if any(keyword in message_lower for keyword in ['error', 'failed', 'fehlgeschlagen', 'ungültig']):
            return 3  # Error
        
        # Warning messages
        if any(keyword in message_lower for keyword in ['warn', 'warning', 'warnung']):
            return 2  # Warning
        
        # Success messages
        if any(keyword in message_lower for keyword in ['ok', 'success', 'erfolgreich', 'connected', 'verbunden']):
            return 4  # Success
        
        # Debug messages
        if message.startswith('[DEBUG]') or message.startswith('[FIRMWARE]'):
            return 1  # Info
        
        # Default to info
        return 1  # Info

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
        
        # Forward to MessageManager if callback is set
        if self._message_callback:
            try:
                self._message_callback(f"[SYSTEM INFO] {message}", 1)  # Info type
            except Exception as e:
                print(f"[ERROR] Logger: Fehler beim Weiterleiten an MessageManager: {e}")
        
        return True
