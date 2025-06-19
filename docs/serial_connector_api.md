# SerialConnector API Dokumentation

**Version**: 2.1.0  
**Letztes Update**: 08.06.2025  
**Status**: Aktiv  

## Übersicht

Diese Dokumentation beschreibt die API des SerialConnector-Moduls, das für die Kommunikation zwischen der RZGCS (Bodenstation) und den Drohnen oder Flugsteuerungen zuständig ist. Der SerialConnector ist Teil der MVVM-Architektur und agiert als Model/Service-Komponente.

## Wichtige API-Änderungen

> **WICHTIG**: Die `connect()`-Methode akzeptiert **keine Parameter**. Die korrekte Verwendung besteht darin, zuerst `setPort(port)` und `setBaudRate(rate)` aufzurufen und anschließend `connect()`.

## Initialisierung

```python
from backend.connection.models.serial_connector import SerialConnector

# Korrekte Initialisierung
serial_connector = SerialConnector(
    sensor_model=sensor_view_model,  # Referenz zum SensorViewModel
    logger=logger,                   # Logging-Instanz
    parameter_model=parameter_model  # Parameter-Modell für MAVLink-Parameter
)
```

## Hauptmethoden

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
| `send_command` | `send_command(command_id, param1=0, param2=0, ..., param7=0)` | Sendet ein MAVLink-Kommando |
| `send_heartbeat` | `send_heartbeat() -> None` | Sendet einen Heartbeat zur Verbindungsaufrechterhaltung |
| `send_request_data_stream` | `send_request_data_stream(...) -> None` | Konfiguriert Telemetrie-Datenströme |

### Simulationsfunktionen

| Methode | Signatur | Beschreibung |
|---------|----------|-------------|
| `start_simulator` | `start_simulator(simulator_type="compatible") -> bool` | Startet einen Simulator |
| `stop_simulator` | `stop_simulator() -> bool` | Stoppt den laufenden Simulator |

## Eigenschaften (Properties)

| Property | Typ | Beschreibung |
|----------|-----|-------------|
| `connected` | `bool` | Liefert `True` wenn eine aktive Verbindung besteht, sonst `False` |
| `connectionState` | `Enum` | Detaillierter Verbindungsstatus (CONNECTED, DISCONNECTED, ERROR, CONNECTING) |
| `port` | `str` | Aktuell ausgewählter Port |
| `baudRate` | `int` | Aktuell eingestellte Baudrate |
| `availablePorts` | `List[str]` | Liste der verfügbaren Ports |
| `availableBaudRates` | `List[int]` | Liste der unterstützten Baudraten |

## Signale

| Signal | Parameter | Beschreibung |
|--------|-----------|-------------|
| `connectedChanged` | `bool` | Wird ausgelöst, wenn sich der Verbindungsstatus ändert |
| `portChanged` | `str` | Wird ausgelöst, wenn sich der Port ändert |
| `baudRateChanged` | `int` | Wird ausgelöst, wenn sich die Baudrate ändert |
| `errorOccurred` | `str` | Wird ausgelöst bei Verbindungsfehlern |
| `connection_successful` | - | Wird ausgelöst bei erfolgreicher Verbindung |
| `availablePortsChanged` | `list` | Wird ausgelöst, wenn sich die Liste verfügbarer Ports ändert |

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

### Beispiel 2: Verbindungsabbruch und Wiederverbindung

```python
# Korrekte Behandlung von Verbindungsabbrüchen
def handle_connection_loss_and_reconnect(port):
    print(f"Verbindung verloren. Versuche Wiederverbindung mit {port}...")
    
    # Immer zuerst die bestehende Verbindung trennen
    serial_connector.disconnect()
    
    # Port konfigurieren
    serial_connector.setPort(port)
    
    # Verbindung wiederherstellen (ohne Parameter)
    serial_connector.connect()
    
    # Status überprüfen
    return serial_connector.connected
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

## Typische Fehler und deren Vermeidung

| Fehler | Vermeidung |
|--------|------------|
| `SerialConnector.connect() takes 1 positional argument but X were given` | Niemals Parameter an `connect()` übergeben. Stattdessen vorher `setPort()` und `setBaudRate()` verwenden |
| `Port already in use` | Vor erneutem Verbindungsaufbau `disconnect()` aufrufen |
| `No port selected` | Vor `connect()` immer `setPort()` aufrufen |
| `Invalid baud rate` | Baudrate mit `setBaudRate()` auf einen gültigen Wert setzen |

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

1. **Immer die Properties nutzen**: Vermeide direkten Zugriff auf interne Variablen
2. **Fehlerbehandlung**: Fange Exceptions bei Verbindungsoperationen ab
3. **Signal-Slot-Verbindungen**: Verwende die Signale für UI-Updates
4. **Polling vermeiden**: Vermeide aktives Polling des Verbindungsstatus, nutze stattdessen Signale
5. **Logging**: Aktiviere detailliertes Logging bei Verbindungsproblemen

## Beispiel für Signal-Verbindungen

```python
# QML-Integration
def register_qml_types():
    qmlRegisterType(SerialConnector, "RZGCS", 1, 0, "SerialConnector")

# Python-Integration
serial_connector.connectedChanged.connect(on_connection_state_changed)
serial_connector.errorOccurred.connect(on_connection_error)
```

## Migration von älteren Versionen

Wenn du von einer älteren Version migrierst, die `connect(port, baudrate)` unterstützt hat:

```python
# Alt (nicht mehr unterstützt):
serial_connector.connect("COM3", 115200)

# Neu (korrekte Verwendung):
serial_connector.setPort("COM3")
serial_connector.setBaudRate(115200)
serial_connector.connect()
```
