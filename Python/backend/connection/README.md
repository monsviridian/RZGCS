# RZGCS Connection Management

## Übersicht
Das Connection-Management-Modul ist ein zentraler Bestandteil des RZGCS-Systems und implementiert die Kommunikation mit MAVLink-kompatiblen Fahrzeugen. Die Implementierung orientiert sich an bewährten Praktiken von QGroundControl und MissionPlanner.

## Modulstruktur
```
connection/
├── __init__.py              # Modul-Initialisierung und Exports
├── connection_manager.py    # Hauptklasse für das Verbindungsmanagement
├── connection_types.py      # Implementierung der Verbindungstypen
├── connection_logger.py     # Logging-System
├── connection_security.py   # Sicherheitsfunktionen
├── bandwidth_manager.py     # Bandbreitenmanagement
└── enums.py                # Enumerationen
```

## Klassen-Dokumentation

### ConnectionManager (connection_manager.py)
Die Hauptklasse für das Verbindungsmanagement, die alle Komponenten koordiniert.

#### Eigenschaften
- `status`: Aktueller Verbindungsstatus (Property)
- `error_message`: Letzte Fehlermeldung (Property)
- `bandwidth_usage`: Aktuelle Bandbreitennutzung in Prozent (Property)

#### Signale
- `statusChanged`: Wird ausgelöst bei Statusänderungen
- `errorOccurred`: Wird bei Fehlern ausgelöst
- `connectionEstablished`: Wird bei erfolgreicher Verbindung ausgelöst
- `connectionLost`: Wird bei Verbindungsverlust ausgelöst
- `bandwidthUsageChanged`: Wird bei Änderung der Bandbreitennutzung ausgelöst

#### Methoden
```python
def connect(self, settings: Dict) -> None:
    """
    Stellt eine Verbindung her.
    
    Args:
        settings: Dictionary mit Verbindungseinstellungen
            - type: Verbindungstyp (SERIAL, UDP, TCP, SIMULATOR)
            - port: Serieller Port (für SERIAL)
            - baudrate: Baudrate (für SERIAL)
            - host: Host-IP (für UDP/TCP)
            - port: Port (für UDP/TCP)
    """

def disconnect(self) -> None:
    """Trennt die aktuelle Verbindung."""

def send_message(self, message: bytes) -> None:
    """
    Sendet eine Nachricht über die aktuelle Verbindung.
    
    Args:
        message: Zu sendende Nachricht als Bytes
    """

def receive_message(self) -> bytes:
    """
    Empfängt eine Nachricht von der aktuellen Verbindung.
    
    Returns:
        Empfangene Nachricht als Bytes
    """
```

### BaseConnection (connection_types.py)
Basisklasse für alle Verbindungstypen.

#### Methoden
```python
def connect(self) -> None:
    """Verbindung herstellen (muss von Unterklassen implementiert werden)"""

def disconnect(self) -> None:
    """Verbindung trennen (muss von Unterklassen implementiert werden)"""

def is_alive(self) -> bool:
    """Prüft ob die Verbindung aktiv ist"""

def send_message(self, message: bytes) -> None:
    """Nachricht senden (muss von Unterklassen implementiert werden)"""

def receive_message(self) -> bytes:
    """Nachricht empfangen (muss von Unterklassen implementiert werden)"""
```

### SerialConnection (connection_types.py)
Implementiert serielle Verbindungen.

#### Eigenschaften
- `supported_baudrates`: Liste unterstützter Baudraten
  ```python
  [9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
  ```

#### Methoden
```python
def connect(self, port: str, baudrate: int) -> None:
    """
    Stellt eine serielle Verbindung her.
    
    Args:
        port: Serieller Port (z.B. 'COM1' oder '/dev/ttyUSB0')
        baudrate: Baudrate für die Verbindung
        
    Raises:
        ValueError: Wenn die Baudrate nicht unterstützt wird
        ConnectionError: Wenn die Verbindung fehlschlägt
    """
```

### UDPConnection (connection_types.py)
Implementiert UDP-Verbindungen.

#### Eigenschaften
- `default_ports`: Standard-Ports für MAVLink
  ```python
  {
      'local': 14550,  # Standard MAVLink UDP Port
      'remote': 14540  # Standard GCS UDP Port
  }
  ```

#### Methoden
```python
def connect(self, host: str, port: Optional[int] = None) -> None:
    """
    Stellt eine UDP-Verbindung her.
    
    Args:
        host: Host-IP oder Hostname
        port: Port für die Verbindung (optional)
        
    Raises:
        ConnectionError: Wenn die Verbindung fehlschlägt
    """
```

### TCPConnection (connection_types.py)
Implementiert TCP-Verbindungen.

#### Eigenschaften
- `default_port`: Standard-Port für MAVLink TCP (5760)

#### Methoden
```python
def connect(self, host: str, port: Optional[int] = None) -> None:
    """
    Stellt eine TCP-Verbindung her.
    
    Args:
        host: Host-IP oder Hostname
        port: Port für die Verbindung (optional)
        
    Raises:
        ConnectionError: Wenn die Verbindung fehlschlägt
    """
```

### ConnectionLogger (connection_logger.py)
Verwaltet das Logging von Verbindungsereignissen.

#### Methoden
```python
def start_logging(self, connection_id: str) -> None:
    """
    Startet das Logging für eine Verbindung.
    
    Args:
        connection_id: Eindeutige ID für die Verbindung
    """

def log_connection_event(self, event_type: str, details: str) -> None:
    """
    Protokolliert ein Verbindungsereignis.
    
    Args:
        event_type: Typ des Ereignisses
        details: Details zum Ereignis
    """

def stop_logging(self) -> None:
    """Beendet das Logging."""
```

### ConnectionSecurity (connection_security.py)
Implementiert Sicherheitsfunktionen für die Verbindung.

#### Methoden
```python
def enable_encryption(self, key: bytes) -> None:
    """
    Aktiviert die Verschlüsselung.
    
    Args:
        key: Verschlüsselungsschlüssel
    """

def encrypt_message(self, message: bytes) -> bytes:
    """
    Verschlüsselt eine Nachricht.
    
    Args:
        message: Zu verschlüsselnde Nachricht
        
    Returns:
        Verschlüsselte Nachricht
    """

def decrypt_message(self, encrypted_message: bytes) -> bytes:
    """
    Entschlüsselt eine Nachricht.
    
    Args:
        encrypted_message: Verschlüsselte Nachricht
        
    Returns:
        Entschlüsselte Nachricht
    """

def generate_key(self) -> bytes:
    """
    Generiert einen neuen Verschlüsselungsschlüssel.
    
    Returns:
        Generierter Schlüssel
    """

def verify_message(self, message: bytes, signature: bytes) -> bool:
    """
    Überprüft die Signatur einer Nachricht.
    
    Args:
        message: Nachricht
        signature: Signatur
        
    Returns:
        True wenn die Signatur gültig ist, sonst False
    """
```

### BandwidthManager (bandwidth_manager.py)
Verwaltet die Bandbreitennutzung der Verbindung.

#### Eigenschaften
- `max_bandwidth`: Maximale Bandbreite in Bits pro Sekunde (default: 1 Mbps)
- `message_priorities`: Prioritäten für verschiedene Nachrichtentypen
  ```python
  {
      'HEARTBEAT': 1,
      'COMMAND': 2,
      'TELEMETRY': 3,
      'LOG': 4
  }
  ```

#### Methoden
```python
def can_send_message(self, message_type: str, message_size: int) -> bool:
    """
    Prüft ob eine Nachricht gesendet werden kann.
    
    Args:
        message_type: Typ der Nachricht
        message_size: Größe der Nachricht in Bytes
        
    Returns:
        True wenn die Nachricht gesendet werden kann, sonst False
    """

def reset_usage(self) -> None:
    """Setzt die Bandbreitennutzung zurück."""

def get_bandwidth_usage(self) -> float:
    """
    Gibt die aktuelle Bandbreitennutzung zurück.
    
    Returns:
        Bandbreitennutzung in Prozent
    """
```

## Verwendung

### Beispiel: Serielle Verbindung
```python
from backend.connection import ConnectionManager, ConnectionType

# ConnectionManager erstellen
connection_manager = ConnectionManager()

# Serielle Verbindung herstellen
settings = {
    'type': ConnectionType.SERIAL.value,
    'port': 'COM1',
    'baudrate': 115200
}
connection_manager.connect(settings)

# Nachricht senden
message = b'Hello, MAVLink!'
connection_manager.send_message(message)

# Nachricht empfangen
response = connection_manager.receive_message()

# Verbindung trennen
connection_manager.disconnect()
```

### Beispiel: UDP-Verbindung
```python
from backend.connection import ConnectionManager, ConnectionType

# ConnectionManager erstellen
connection_manager = ConnectionManager()

# UDP-Verbindung herstellen
settings = {
    'type': ConnectionType.UDP.value,
    'host': '127.0.0.1',
    'port': 14550
}
connection_manager.connect(settings)

# Verschlüsselung aktivieren
connection_manager.enable_encryption()

# Nachricht senden
message = b'Hello, MAVLink!'
connection_manager.send_message(message)

# Verbindung trennen
connection_manager.disconnect()
```

## Best Practices

1. **Verbindungsaufbau**
   - Immer Timeout für Verbindungsversuche setzen
   - Automatische Wiederverbindung implementieren
   - Verbindungsstatus regelmäßig überprüfen

2. **Fehlerbehandlung**
   - Alle Verbindungsfehler protokollieren
   - Benutzerfreundliche Fehlermeldungen anzeigen
   - Automatische Fehlerbehebung wo möglich

3. **Sicherheit**
   - Verschlüsselung für sensible Daten
   - Authentifizierung implementieren
   - Regelmäßige Sicherheitsüberprüfungen

4. **Performance**
   - Bandbreite effizient nutzen
   - Nachrichten priorisieren
   - Verbindungsqualität überwachen

## Abhängigkeiten

- PySide6: Für QML-Integration
- pyserial: Für serielle Verbindungen
- cryptography: Für Verschlüsselung
- logging: Für Protokollierung

# Connection-Modul

## Architektur

Das Connection-Modul implementiert die Verbindungsverwaltung für das RZGCS nach dem MVVM-Pattern (Model-View-ViewModel). Es ist für die Verwaltung aller Verbindungen zum UAV zuständig, einschließlich der Kommunikation über verschiedene Protokolle (MAVLink, Serial, UDP, TCP).

### Komponenten

#### 1. Model Layer
- **ConnectionState**: Repräsentiert den aktuellen Verbindungsstatus
- **ConnectionParameters**: Enthält die Verbindungsparameter
- **ConnectionStatistics**: Speichert Verbindungsstatistiken
- **ConnectionType**: Enum für die verschiedenen Verbindungstypen
- **ConnectionStatus**: Enum für die verschiedenen Verbindungsstatus

#### 2. Service Layer
- **ConnectionService**: Implementiert die Geschäftslogik für die Verbindungsverwaltung
  - Verbindungsaufbau/-abbau
  - Parameter-Management
  - Status-Updates
  - Fehlerbehandlung
  - Statistiken

#### 3. ViewModel Layer
- **ConnectionViewModel**: Bindet die Services an die View
  - Properties für Status und Parameter
  - Slots für Benutzerinteraktionen
  - Signale für Statusänderungen
  - Fehlerbehandlung

#### 4. View Layer
- **ConnectionView**: QML-UI für die Verbindungsverwaltung
  - Status-Anzeige
  - Parameter-Konfiguration
  - Statistiken
  - Aktions-Buttons

### Datenfluss

1. **Benutzerinteraktion** → View
2. **View** → ViewModel (Slots)
3. **ViewModel** → Service (Methodenaufrufe)
4. **Service** → Model (Datenaktualisierung)
5. **Model** → Service (Statusänderungen)
6. **Service** → ViewModel (Signale)
7. **ViewModel** → View (Properties)

## Frontend-Integration

### 1. QML-Integration

```qml
import RZGCS.Connection 1.0

Item {
    // ViewModel-Instanz
    property var viewModel: ConnectionViewModel {}
    
    // Status-Bindings
    Label {
        text: "Status: " + viewModel.status
    }
    
    // Parameter-Bindings
    TextField {
        text: viewModel.parameters.port
        onTextChanged: {
            var params = viewModel.parameters
            params.port = text
            viewModel.set_parameters(params)
        }
    }
    
    // Aktionen
    Button {
        text: viewModel.state.is_connected ? "Trennen" : "Verbinden"
        onClicked: {
            if (viewModel.state.is_connected) {
                viewModel.disconnect()
            } else {
                viewModel.connect()
            }
        }
    }
}
```

### 2. Python-Integration

```python
from rzgcs.connection import ConnectionViewModel, ConnectionService

# Service-Instanz erstellen
connection_service = ConnectionService()

# ViewModel-Instanz erstellen
view_model = ConnectionViewModel()
view_model.set_connection_service(connection_service)

# Status-Überwachung
@view_model.status_changed.connect
def on_status_changed(status):
    print(f"Neuer Status: {status}")

# Parameter setzen
params = view_model.parameters
params.port = "COM1"
params.baudrate = 57600
view_model.set_parameters(params)

# Verbindung aufbauen
view_model.connect()
```

### 3. Signal-Handling

```python
# Status-Änderungen
view_model.status_changed.connect(lambda status: print(f"Status: {status}"))
view_model.type_changed.connect(lambda type: print(f"Typ: {type}"))
view_model.parameters_changed.connect(lambda params: print(f"Parameter: {params}"))

# Fehlerbehandlung
view_model.error_occurred.connect(lambda message: print(f"Fehler: {message}"))
```

### 4. Best Practices

1. **ViewModel-Instanziierung**:
   - Erstellen Sie eine ViewModel-Instanz pro View
   - Setzen Sie den Service vor der Verwendung

2. **Parameter-Management**:
   - Ändern Sie Parameter immer über das ViewModel
   - Nutzen Sie die Parameter-Properties für Bindings

3. **Fehlerbehandlung**:
   - Implementieren Sie Error-Handler für alle Views
   - Zeigen Sie Fehlermeldungen dem Benutzer an

4. **Status-Updates**:
   - Reagieren Sie auf Status-Änderungen
   - Aktualisieren Sie die UI entsprechend

5. **Ressourcen-Management**:
   - Trennen Sie die Verbindung beim Beenden
   - Löschen Sie ViewModel-Instanzen ordnungsgemäß

## Beispiel-Implementierung

### 1. Einfache Verbindungsverwaltung

```python
from rzgcs.connection import ConnectionViewModel, ConnectionService

class ConnectionManager:
    def __init__(self):
        self.service = ConnectionService()
        self.view_model = ConnectionViewModel()
        self.view_model.set_connection_service(self.service)
        
        # Signal-Handler
        self.view_model.status_changed.connect(self._on_status_changed)
        self.view_model.error_occurred.connect(self._on_error)
    
    def connect(self, params):
        self.view_model.set_parameters(params)
        return self.view_model.connect()
    
    def disconnect(self):
        return self.view_model.disconnect()
    
    def _on_status_changed(self, status):
        print(f"Verbindungsstatus: {status}")
    
    def _on_error(self, message):
        print(f"Verbindungsfehler: {message}")
```

### 2. Erweiterte Verbindungsverwaltung

```python
from rzgcs.connection import (
    ConnectionViewModel,
    ConnectionService,
    ConnectionType,
    ConnectionStatus
)

class AdvancedConnectionManager:
    def __init__(self):
        self.service = ConnectionService()
        self.view_model = ConnectionViewModel()
        self.view_model.set_connection_service(self.service)
        
        # Signal-Handler
        self.view_model.status_changed.connect(self._on_status_changed)
        self.view_model.type_changed.connect(self._on_type_changed)
        self.view_model.parameters_changed.connect(self._on_parameters_changed)
        self.view_model.error_occurred.connect(self._on_error)
    
    def connect_serial(self, port, baudrate):
        params = self.view_model.parameters
        params.type = ConnectionType.SERIAL
        params.port = port
        params.baudrate = baudrate
        return self.view_model.connect()
    
    def connect_udp(self, host, port):
        params = self.view_model.parameters
        params.type = ConnectionType.UDP
        params.host = host
        params.port_number = port
        return self.view_model.connect()
    
    def connect_tcp(self, host, port):
        params = self.view_model.parameters
        params.type = ConnectionType.TCP
        params.host = host
        params.port_number = port
        return self.view_model.connect()
    
    def _on_status_changed(self, status):
        if status == ConnectionStatus.CONNECTED:
            print("Verbunden")
        elif status == ConnectionStatus.DISCONNECTED:
            print("Getrennt")
        elif status == ConnectionStatus.ERROR:
            print("Fehler")
    
    def _on_type_changed(self, type):
        print(f"Verbindungstyp: {type}")
    
    def _on_parameters_changed(self, params):
        print(f"Parameter: {params}")
    
    def _on_error(self, message):
        print(f"Fehler: {message}")
```

## Fehlerbehandlung

### 1. Verbindungsfehler

```python
def handle_connection_error(error):
    if error == ConnectionError.TIMEOUT:
        print("Verbindungszeitüberschreitung")
    elif error == ConnectionError.REFUSED:
        print("Verbindung abgelehnt")
    elif error == ConnectionError.INVALID_PARAMETERS:
        print("Ungültige Parameter")
    else:
        print(f"Unbekannter Fehler: {error}")
```

### 2. Parameter-Validierung

```python
def validate_parameters(params):
    if params.type == ConnectionType.SERIAL:
        if not params.port:
            raise ValueError("Port muss angegeben werden")
        if not params.baudrate:
            raise ValueError("Baudrate muss angegeben werden")
    elif params.type in [ConnectionType.UDP, ConnectionType.TCP]:
        if not params.host:
            raise ValueError("Host muss angegeben werden")
        if not params.port_number:
            raise ValueError("Port-Nummer muss angegeben werden")
```

## Sicherheitsaspekte

1. **Parameter-Validierung**:
   - Validieren Sie alle Parameter vor der Verwendung
   - Prüfen Sie die Parameter-Grenzen

2. **Fehlerbehandlung**:
   - Implementieren Sie umfassende Fehlerbehandlung
   - Protokollieren Sie alle Fehler

3. **Ressourcen-Management**:
   - Schließen Sie Verbindungen ordnungsgemäß
   - Räumen Sie Ressourcen auf

4. **Sicherheitsmaßnahmen**:
   - Implementieren Sie Timeouts
   - Nutzen Sie Verschlüsselung
   - Validieren Sie alle Eingaben 