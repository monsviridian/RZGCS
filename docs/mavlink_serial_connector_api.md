# SerialConnector API Dokumentation für MAVLink

**Version**: 3.0.0  
**Letztes Update**: 08.06.2025  
**Status**: Aktiv  

## Übersicht

Diese Dokumentation beschreibt die API des SerialConnector-Moduls, das die bidirektionale MAVLink-Kommunikation zwischen der RZGCS (Bodenstation) und den Drohnen oder Flugsteuerungen ermöglicht. Der SerialConnector ist Teil der MVVM-Architektur und agiert als Model/Service-Komponente für die direkte MAVLink-Kommunikation ohne MAVSDK-Zwischenschicht.

## Wichtige API-Änderungen

> **WICHTIG**: Die `connect()`-Methode akzeptiert **keine Parameter**. Die korrekte Verwendung besteht darin, zuerst `setPort(port)` und `setBaudRate(rate)` aufzurufen und anschließend `connect()`.

## Initialisierung

```python
from backend.serial_connector import SerialConnector
from backend.message_handler import MessageHandler
from backend.sensor_manager import SensorManager

# Korrekte Initialisierung
serial_connector = SerialConnector(
    sensor_model=sensor_manager,  # Für Sensor-Updates
    logger=logger,                # Logging-Instanz
    parameter_model=parameter_model  # Parameter-Modell für MAVLink-Parameter
)

# Message Handler einrichten
message_handler = MessageHandler(logger=logger)
```

## Verbindungsherstellung

### Verbindungsaufbau und -verwaltung

| Methode | Signatur | Beschreibung |
|---------|----------|-------------|
| `setPort` | `setPort(port: str) -> None` | Setzt den zu verwendenden Port (COM, UDP, TCP) |
| `setBaudRate` | `setBaudRate(rate: int) -> None` | Setzt die Baudrate für die Verbindung |
| `connect` | `connect() -> bool` | **Stellt eine Verbindung mit vorher konfigurierten Parametern her** |
| `disconnect` | `disconnect() -> bool` | Trennt eine bestehende Verbindung |
| `refresh_ports` | `refresh_ports() -> None` | Aktualisiert die Liste der verfügbaren Ports |

### MAVLink-Kommunikation

| Methode | Signatur | Beschreibung |
|---------|----------|-------------|
| `send_command` | `send_command(command_id, param1=0, ..., param7=0) -> bool` | Sendet ein MAVLink-Kommando direkt an die Flugsteuerung |
| `send_mavlink_message` | `send_mavlink_message(message) -> bool` | Sendet eine direkte MAVLink-Nachricht |
| `send_heartbeat` | `send_heartbeat() -> None` | Sendet einen Heartbeat zur Verbindungsaufrechterhaltung |
| `request_data_stream` | `request_data_stream(stream_id, rate, start_stop) -> bool` | Konfiguriert MAVLink-Datenströme |
| `request_parameters` | `request_parameters() -> None` | Fordert alle Parameter der Flugsteuerung an |
| `set_parameter` | `set_parameter(name, value, param_type) -> bool` | Setzt einen Parameter auf der Flugsteuerung |

## Eigenschaften (Properties)

| Property | Typ | Beschreibung |
|----------|-----|-------------|
| `connected` | `bool` | Liefert `True` wenn eine aktive Verbindung besteht, sonst `False` |
| `connectionState` | `Enum` | Detaillierter Verbindungsstatus (CONNECTED, DISCONNECTED, ERROR, CONNECTING) |
| `port` | `str` | Aktuell ausgewählter Port |
| `baudRate` | `int` | Aktuell eingestellte Baudrate |
| `availablePorts` | `List[str]` | Liste der verfügbaren Ports |
| `availableBaudRates` | `List[int]` | Liste der unterstützten Baudraten |
| `system_id` | `int` | MAVLink-System-ID der verbundenen Flugsteuerung |
| `component_id` | `int` | MAVLink-Komponenten-ID der verbundenen Flugsteuerung |
| `autopilot_type` | `int` | MAVLink-Autopilot-Typ der verbundenen Flugsteuerung |

## Signale

| Signal | Parameter | Beschreibung |
|--------|-----------|-------------|
| `connectedChanged` | `bool` | Wird ausgelöst, wenn sich der Verbindungsstatus ändert |
| `portChanged` | `str` | Wird ausgelöst, wenn sich der Port ändert |
| `baudRateChanged` | `int` | Wird ausgelöst, wenn sich die Baudrate ändert |
| `errorOccurred` | `str` | Wird ausgelöst bei Verbindungsfehlern |
| `connection_successful` | - | Wird ausgelöst bei erfolgreicher Verbindung |
| `availablePortsChanged` | `list` | Wird ausgelöst, wenn sich die Liste verfügbarer Ports ändert |
| `message_received` | `msg` | Wird ausgelöst, wenn eine MAVLink-Nachricht empfangen wurde |
| `heartbeat_received` | `msg` | Wird ausgelöst, wenn ein Heartbeat empfangen wurde |
| `system_status_changed` | `status` | Wird ausgelöst, wenn sich der System-Status ändert |
| `parameter_received` | `name, value` | Wird ausgelöst, wenn ein Parameter empfangen wurde |

## Integration mit MessageHandler

Der SerialConnector arbeitet eng mit dem MessageHandler zusammen, um MAVLink-Nachrichten zu verarbeiten:

```python
# Verbindung einrichten
serial_connector = SerialConnector(sensor_model, logger, parameter_model)
message_handler = MessageHandler(logger)

# Nach erfolgreicher Verbindung
if serial_connector.connect():
    # MAVLink-Connection an Message Handler übergeben
    mavlink_connection = serial_connector.get_mavlink_connection()
    message_handler.set_connection(mavlink_connection)
    
    # Nachrichtenverarbeitung starten
    message_handler.start_message_processing()
```

## Korrekte Verwendung - Code-Beispiele

### Beispiel 1: Grundlegende Verbindungsherstellung

```python
# Korrekte Verwendung der SerialConnector-API
def establish_connection(port_name, baud_rate=115200):
    # 1. Port setzen
    serial_connector.setPort(port_name)
    
    # 2. Baudrate setzen
    serial_connector.setBaudRate(baud_rate)
    
    # 3. Verbindung herstellen (ohne Parameter)
    serial_connector.connect()
    
    # 4. Verbindungsstatus prüfen
    if serial_connector.connected:
        print(f"✅ Verbindung zu {port_name} erfolgreich hergestellt")
        return True
    else:
        print(f"❌ Verbindung zu {port_name} konnte nicht hergestellt werden")
        return False
```

### Beispiel 2: MAVLink-Kommandos senden

```python
def set_flight_mode(mode):
    """
    Setzt den Flugmodus über MAVLink.
    
    Args:
        mode (int): MAVLink-Flugmodus-ID
    """
    # MAV_CMD_DO_SET_MODE - ID 176
    # param1: Mode (vgl. MAV_MODE)
    # param2: Custom Mode (Flugmodus)
    # param3: Custom Sub-Mode
    return serial_connector.send_command(
        command_id=176,
        param1=1,  # MODE_FLAG_CUSTOM_MODE_ENABLED
        param2=mode,
        param3=0
    )
```

### Beispiel 3: ConnectionAdapter Integration (MVVM)

```python
class ConnectionAdapter(QObject):
    """ViewModel für die Verbindungssteuerung."""
    
    # [...] Signaldefinitionen usw.
    
    def connect(self):
        """Stellt eine Verbindung her."""
        try:
            # Status aktualisieren
            self._state.status = ConnectionStatus.CONNECTING
            self._state.is_connecting = True
            self.status_changed.emit(self._state.status)
            
            # Parameter aus dem State holen
            port = self._state.parameters.port or "COM1"
            baudrate = self._state.parameters.baudrate or 115200
            
            # Setze Port und Baudrate
            self._serial_connector.setPort(port)
            self._serial_connector.setBaudRate(int(baudrate))
            
            # Verbindung herstellen (ohne Parameter)
            self._serial_connector.connect()
            success = self._serial_connector.connected
            
            # Status aktualisieren
            self._state.is_connecting = False
            self._state.is_connected = success
            self._state.status = ConnectionStatus.CONNECTED if success else ConnectionStatus.ERROR
            
            return success
        except Exception as e:
            # Fehlerbehandlung
            self._state.is_error = True
            self._state.error_message = str(e)
            return False
```

## Unterstützung verschiedener Verbindungsformate

Der SerialConnector unterstützt verschiedene Verbindungsformate:

| Format | Beispiel | Beschreibung |
|--------|----------|-------------|
| COM-Ports | `COM3` | Standard serielle Verbindung |
| COM-Ports mit Baudrate | `COM3:115200` | Serielle Verbindung mit spezifischer Baudrate |
| UDP | `udp:localhost:14550` | UDP-Verbindung für SITL oder Netzwerk |
| TCP | `tcp:192.168.1.10:5760` | TCP-Verbindung für entfernte Geräte |

## MAVLink-spezifische Konfiguration

Der SerialConnector kann für verschiedene MAVLink-Dialekte und -Versionen konfiguriert werden:

```python
# Beispiel für spezifische MAVLink-Konfiguration
serial_connector.set_mavlink_dialect("ardupilotmega")  # Oder "common", "px4", usw.
serial_connector.set_source_system(255)  # GCS System ID
serial_connector.set_source_component(0)  # GCS Component ID
```

## MAVLink-Nachrichtenfilterung

Die in `message_handler.py` implementierte MAVLink-Nachrichtenfilterung sorgt für effiziente Verarbeitung:

1. Caching der letzten Werte jedes Nachrichtentyps
2. Filtern basierend auf konfigurierbaren Schwellenwerten
3. Einhaltung von Mindestzeiträumen zwischen gleichen Nachrichtentypen
4. Priorisierung kritischer Nachrichten (z.B. STATUS_TEXT)

```python
# Beispiel für Nachrichtenfilter-Konfiguration
message_handler.configure_filter(
    message_type="ATTITUDE",
    threshold=0.05,  # 5% Änderung für neue Nachricht
    min_interval=500  # Mindestens 500ms zwischen Nachrichten
)
```

## Typische Fehler und deren Vermeidung

| Fehler | Vermeidung |
|--------|------------|
| `SerialConnector.connect() takes 1 positional argument but X were given` | Niemals Parameter an `connect()` übergeben. Stattdessen vorher `setPort()` und `setBaudRate()` verwenden |
| `Port already in use` | Vor erneutem Verbindungsaufbau `disconnect()` aufrufen |
| `No port selected` | Vor `connect()` immer `setPort()` aufrufen |
| `Invalid baud rate` | Baudrate mit `setBaudRate()` auf einen gültigen Wert setzen |
| `MAVLink parsing error` | Sicherstellen, dass die Baudrate korrekt ist und der richtige MAVLink-Dialekt verwendet wird |

## Thread-Sicherheit

Der SerialConnector ist nicht inhärent thread-sicher. Bei Verwendung in Threads:

```python
# Thread-sichere Verwendung
from PySide6.QtCore import QMutex

# Mutex in der umschließenden Klasse definieren
self._connection_mutex = QMutex()

# Vor Zugriff sperren
self._connection_mutex.lock()
try:
    self._serial_connector.setPort(port)
    self._serial_connector.connect()
    # Weitere Operationen
finally:
    self._connection_mutex.unlock()
```

## Best Practices

1. **Konsistente Fehlerbehandlung**: Fange Exceptions bei Verbindungsoperationen ab
2. **Signal-Slot-Verbindungen**: Verwende die Signale für UI-Updates
3. **Effizienter MAVLink-Nachrichtenfluss**: Nutze die Filterung, um die Anwendung nicht zu überlasten
4. **Parameterbehandlung**: Lade Parameter nur bei Bedarf oder bei Verbindungsaufbau
5. **Zyklische Prüfung vermeiden**: Vermeide aktives Polling, nutze stattdessen Signale
