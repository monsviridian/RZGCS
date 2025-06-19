"""
ConnectionAdapter - Adapter zwischen SerialConnector und ConnectionViewModel
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from enum import Enum, auto

# Einfache Enum-Definitionen für Kompatibilität mit der ConnectionView
class ConnectionStatus(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()

class ConnectionType(Enum):
    SERIAL = auto()
    UDP = auto()
    TCP = auto()
    MAVLINK = auto()

# Einfache Datenklassen für Kompatibilität mit der ConnectionView
class ConnectionParameters:
    def __init__(self, type=ConnectionType.MAVLINK, port="", baudrate=115200, 
                 host="", port_number=0, timeout=5, retry_count=3, auto_reconnect=True):
        self.type = type
        self.port = port
        self.baudrate = baudrate
        self.host = host
        self.port_number = port_number
        self.timeout = timeout
        self.retry_count = retry_count
        self.auto_reconnect = auto_reconnect

class ConnectionState:
    def __init__(self, status=ConnectionStatus.DISCONNECTED, type=ConnectionType.MAVLINK,
                 is_connected=False, is_connecting=False, is_error=False,
                 error_message="", parameters=None):
        self.status = status
        self.type = type
        self.is_connected = is_connected
        self.is_connecting = is_connecting
        self.is_error = is_error
        self.error_message = error_message
        self.parameters = parameters or ConnectionParameters()

class ConnectionStatistics:
    def __init__(self, bytes_sent=0, bytes_received=0, packets_sent=0, 
                 packets_received=0, errors=0, connection_time=0.0, 
                 last_error_message=""):
        self.bytes_sent = bytes_sent
        self.bytes_received = bytes_received
        self.packets_sent = packets_sent
        self.packets_received = packets_received
        self.errors = errors
        self.connection_time = connection_time
        self.last_error_message = last_error_message

class ConnectionAdapter(QObject):
    """
    Adapter zwischen SerialConnector und dem ConnectionViewModel
    """
    # Signale für Änderungen des Verbindungszustands
    # Definiere eine explizite Signal-Signatur für status_changed
    # Verwende int anstelle von object für ConnectionStatus,
    # da die Enum-Werte als Ganzzahlen übertragen werden können
    # Wichtig: Verwende nur ein einheitliches Signal-Format ohne Mischung der Klassen
    status_changed = Signal(int)  # ConnectionStatus als int
    connected_changed = Signal(bool)  # Einfaches Boolean-Signal für Verbindungsstatus
    type_changed = Signal(object)    # ConnectionType
    parameters_changed = Signal(object)  # ConnectionParameters
    state_updated = Signal(object)   # ConnectionState
    statistics_updated = Signal(object)  # ConnectionStatistics
    error_occurred = Signal(str)
    
    # Signal-Definitionen werden als Klassenvariablen vor der Instanziierung gespeichert
    # Um Probleme mit Signal-Verbindungen zu beheben, sicherstellen, dass Initialisierungsreihenfolge korrekt ist
    
    def __init__(self, serial_connector):
        """Initialisiert den Connection-Adapter."""
        super().__init__()
        
        self._serial_connector = serial_connector
        
        # Initialisiere Verbindungszustand
        self._state = ConnectionState(
            status=ConnectionStatus.DISCONNECTED,
            type=ConnectionType.MAVLINK,
            parameters=ConnectionParameters(
                type=ConnectionType.MAVLINK,
                port=serial_connector.port or "",
                baudrate=serial_connector.baud_rate
            )
        )
        
        # Initialisiere Statistiken
        self._statistics = ConnectionStatistics()
        
        # Letzter bekannter Verbindungsstatus
        self._last_connected_state = False
        
        # Initialisiere Timer für Status-Updates
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_state)
        self._update_timer.timeout.connect(self._check_connection_status)
        self._update_timer.start(1000)  # Update alle 1 Sekunde
    
    def _check_connection_status(self):
        """Überprüft regelmäßig den Verbindungsstatus des SerialConnector und aktualisiert den Zustand bei Änderungen."""
        try:
            # Aktuellen Verbindungsstatus vom SerialConnector abfragen
            current_connected = self._serial_connector.connected
            
            # Wenn sich der Status geändert hat, aktualisieren und Signal senden
            if current_connected != self._last_connected_state:
                self._last_connected_state = current_connected
                self._state.is_connected = current_connected
                self._state.status = ConnectionStatus.CONNECTED if current_connected else ConnectionStatus.DISCONNECTED
                # Emittiere den Status als int und das connected_changed Signal
                self.status_changed.emit(self._state.status.value)
                self.connected_changed.emit(current_connected)
                self.state_updated.emit(self._state)
        except Exception as e:
            # Fehlerbehandlung
            self._state.is_error = True
            self._state.error_message = f"Fehler bei der Überprüfung des Verbindungsstatus: {str(e)}"
            self._statistics.errors += 1
            self._statistics.last_error_message = str(e)
            
            self.error_occurred.emit(str(e))
            self.state_updated.emit(self._state)
    
    def _update_state(self):
        """Aktualisiert den Verbindungszustand und Statistiken."""
        try:
            # Verbindungsstatus abrufen
            is_connected = self._serial_connector.connected
        
            # Aktualisiere State, wenn sich der Status geändert hat
            if is_connected != self._state.is_connected:
                self._state.is_connected = is_connected
                self._state.status = ConnectionStatus.CONNECTED if is_connected else ConnectionStatus.DISCONNECTED
                # Emittiere den Status als int und das connected_changed Signal
                self.status_changed.emit(self._state.status.value)
                self.connected_changed.emit(is_connected)
                self.state_updated.emit(self._state)
            self.state_updated.emit(self._state)
        
            # Aktualisiere Parameter, wenn sich der Port oder die Baudrate geändert haben
            current_port = self._serial_connector.port
            current_baudrate = self._serial_connector.baud_rate
            if current_port != self._state.parameters.port or current_baudrate != self._state.parameters.baudrate:
                self._state.parameters.port = current_port
                self._state.parameters.baudrate = current_baudrate
                self.parameters_changed.emit(self._state.parameters)
        except Exception as e:
            # Fehlerbehandlung
            self._state.is_error = True
            self._state.error_message = f"Fehler bei der Aktualisierung des Zustands: {str(e)}"
            self._statistics.errors += 1
            self._statistics.last_error_message = str(e)
            
            self.error_occurred.emit(str(e))
        
        # Aktualisiere Statistiken
        # Diese sind Platzhalter, da der SerialConnector möglicherweise keine detaillierten Statistiken bietet
        if is_connected:
            self._statistics.connection_time += 1.0
            self.statistics_updated.emit(self._statistics)
    
    # Properties
    @Property(object, notify=status_changed)
    def status(self):
        """Gibt den aktuellen Verbindungsstatus zurück."""
        return self._state.status
        
    @Property(object, notify=type_changed)
    def type(self):
        """Gibt den aktuellen Verbindungstyp zurück."""
        return self._state.type
        
    @Property(object, notify=parameters_changed)
    def parameters(self):
        """Gibt die aktuellen Verbindungsparameter zurück."""
        return self._state.parameters
        
    @Property(object, notify=state_updated)
    def state(self):
        """Gibt den aktuellen Verbindungszustand zurück."""
        return self._state
        
    @Property(object, notify=statistics_updated)
    def statistics(self):
        """Gibt die aktuellen Verbindungsstatistiken zurück."""
        return self._statistics
        
    # Slots
    @Slot(str)
    @Slot()
    def connect(self, conn_string=None, port=None, baudrate=None, host=None):
        """Stellt eine Verbindung her.
        
        Args:
            conn_string: Optionaler Verbindungsstring im Format 'PORT:BAUDRATE'
            port: Optionaler Port-Name
            baudrate: Optionale Baudrate
            host: Optionaler Host-Name bei UDP/TCP-Verbindungen
        """
        try:
            # Verbindung mit dem SerialConnector herstellen
            self._state.status = ConnectionStatus.CONNECTING
            self._state.is_connecting = True
            # Emittiere den Status als int
            self.status_changed.emit(self._state.status.value)
            self.state_updated.emit(self._state)
            
            # Parameter verarbeiten, falls vorhanden
            if conn_string:
                # Format: 'PORT:BAUDRATE' oder nur 'PORT'
                parts = conn_string.split(':')
                if len(parts) > 0 and parts[0]:
                    self._state.parameters.port = parts[0]
                if len(parts) > 1 and parts[1]:
                    self._state.parameters.baudrate = int(parts[1])
            
            # Einzelne Parameter überschreiben, falls angegeben
            if port:
                self._state.parameters.port = port
            if baudrate:
                self._state.parameters.baudrate = baudrate
            
            # Endgültige Parameter festlegen
            port = self._state.parameters.port or "COM1"
            baudrate = self._state.parameters.baudrate or 115200
            
            # Setze Port und Baudrate
            self._serial_connector.setPort(port)
            self._serial_connector.setBaudRate(int(baudrate))
            
            # Verbindung herstellen
            self._serial_connector.connect()
            success = self._serial_connector.connected
            
            # Status aktualisieren
            self._state.is_connecting = False
            self._state.is_connected = success
            self._state.status = ConnectionStatus.CONNECTED if success else ConnectionStatus.ERROR
            self._state.is_error = not success
            # Emittiere den Status als int und das connected_changed Signal
            self.status_changed.emit(self._state.status.value)
            self.connected_changed.emit(success)
            self.state_updated.emit(self._state)
            
            return success
        except Exception as e:
            self._state.is_connecting = False
            self._state.is_error = True
            self._state.error_message = str(e)
            self._state.status = ConnectionStatus.ERROR
            self._statistics.errors += 1
            self._statistics.last_error_message = str(e)
            
            self.error_occurred.emit(str(e))
            self.status_changed.emit(self._state.status)
            self.state_updated.emit(self._state)
            self.statistics_updated.emit(self._statistics)
            
            return False
        
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung."""
        try:
            self._serial_connector.disconnect()
            success = not self._serial_connector.connected
            
            self._state.is_connected = False
            self._state.status = ConnectionStatus.DISCONNECTED
            self.status_changed.emit(self._state.status)
            self.state_updated.emit(self._state)
            
            return success
        except Exception as e:
            self._state.is_error = True
            self._state.error_message = str(e)
            self._state.status = ConnectionStatus.ERROR
            self._statistics.errors += 1
            self._statistics.last_error_message = str(e)
            
            self.error_occurred.emit(str(e))
            self.status_changed.emit(self._state.status)
            self.state_updated.emit(self._state)
            self.statistics_updated.emit(self._statistics)
            
            return False
        
    @Slot(object)
    def set_parameters(self, parameters):
        """Setzt die Verbindungsparameter."""
        try:
            # Parameter aktualisieren
            self._state.parameters = parameters
            
            # Port und Baudrate im SerialConnector setzen (nur wenn nicht verbunden)
            if not self._state.is_connected:
                self._serial_connector.setPort(parameters.port)
                self._serial_connector.setBaudRate(int(parameters.baudrate))
            
            self.parameters_changed.emit(self._state.parameters)
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
        
    @Slot(str)
    def export_connection_data(self, file_path):
        """Exportiert die Verbindungsdaten in eine JSON-Datei (Platzhalterfunktion)."""
        # Diese Funktion ist ein Platzhalter, da der SerialConnector diese Funktion möglicherweise nicht bietet
        self.error_occurred.emit("Export-Funktion nicht implementiert")
        return False
        
    @Slot(str)
    def import_connection_data(self, file_path):
        """Importiert die Verbindungsdaten aus einer JSON-Datei (Platzhalterfunktion)."""
        # Diese Funktion ist ein Platzhalter, da der SerialConnector diese Funktion möglicherweise nicht bietet
        self.error_occurred.emit("Import-Funktion nicht implementiert")
        return False
