# Architektur-Dokumentation

## MVVM-Architektur

Die Anwendung folgt dem MVVM (Model-View-ViewModel) Muster, das eine klare Trennung zwischen Daten, Logik und Benutzeroberfläche ermöglicht.

### Komponenten

#### Model
- **Datenmodelle**: Reine Datenstrukturen ohne Logik
- **Services**: Implementieren die Geschäftslogik
- **Repositories**: Verwalten den Datenzugriff

#### ViewModel
- **Präsentationslogik**: Bereitet Daten für die View auf
- **Datenbindung**: Verbindet Model und View
- **Kommandos**: Verarbeitet Benutzerinteraktionen

#### View
- **Benutzeroberfläche**: Zeigt Daten an und sammelt Benutzereingaben
- **Bindungen**: Verbindet UI-Elemente mit ViewModel-Eigenschaften
- **Templates**: Definiert das Layout und Design

## Frontend-Integration

### QML/Qt Quick Integration

Die Anwendung verwendet Qt/QML für die Benutzeroberfläche. Die Integration erfolgt über:

1. **QML-Bindings**:
```qml
// Beispiel für Flugsteuerung
import RZGCS.FlightControl 1.0

FlightControl {
    id: flightControl
    
    // Properties
    property bool isConnected: connectionViewModel.status === ConnectionStatus.CONNECTED
    property bool isArmed: flightViewModel.state.armed
    
    // Bindings
    Connections {
        target: flightViewModel
        function onStateChanged(state) {
            // Update UI
        }
    }
    
    // UI Elements
    Button {
        text: isConnected ? "Disconnect" : "Connect"
        onClicked: {
            if (isConnected) {
                connectionViewModel.disconnect()
            } else {
                connectionViewModel.connect()
            }
        }
    }
}
```

2. **C++/Python Bridge**:
```python
# Python-Backend
class FlightControlBridge(QObject):
    @Slot()
    def connect(self):
        self._viewmodel.connection_viewmodel.connect()
        
    @Signal
    def connectionStatusChanged(self, status):
        pass
```

### REST API Integration

Alternativ kann die Anwendung über eine REST API integriert werden:

1. **API-Endpunkte**:
```python
# FastAPI Implementation
from fastapi import FastAPI
from .viewmodels.main_viewmodel import MainViewModel

app = FastAPI()
viewmodel = MainViewModel()

@app.get("/api/status")
async def get_status():
    return {
        "connection": viewmodel.connection_viewmodel.status,
        "flight": viewmodel.flight_viewmodel.state,
        "mission": viewmodel.mission_viewmodel.current_mission
    }

@app.post("/api/connect")
async def connect():
    return viewmodel.connection_viewmodel.connect()
```

2. **Frontend-Integration**:
```javascript
// JavaScript/TypeScript Frontend
class FlightControlAPI {
    async getStatus() {
        const response = await fetch('/api/status');
        return response.json();
    }
    
    async connect() {
        const response = await fetch('/api/connect', {
            method: 'POST'
        });
        return response.json();
    }
}
```

### WebSocket Integration

Für Echtzeit-Updates:

1. **WebSocket Server**:
```python
# Python-Backend
from fastapi import FastAPI, WebSocket
from .viewmodels.main_viewmodel import MainViewModel

app = FastAPI()
viewmodel = MainViewModel()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Subscribe to ViewModel signals
    viewmodel.flight_viewmodel.state_updated.connect(
        lambda state: websocket.send_json({"type": "state", "data": state})
    )
```

2. **Frontend-Integration**:
```javascript
// JavaScript/TypeScript Frontend
class FlightControlWebSocket {
    constructor() {
        this.ws = new WebSocket('ws://localhost:8000/ws');
        this.ws.onmessage = this.handleMessage.bind(this);
    }
    
    handleMessage(event) {
        const data = JSON.parse(event.data);
        switch(data.type) {
            case 'state':
                this.updateState(data.data);
                break;
        }
    }
}
```

## Komponenten-Integration

### 1. Connection Module

```python
# Backend
class ConnectionViewModel(QObject):
    statusChanged = Signal(ConnectionStatus)
    
    def connect(self):
        # Implementation
        pass

# Frontend
ConnectionControl {
    id: connectionControl
    
    // Bind to ViewModel
    property var viewModel: connectionViewModel
    
    // UI Elements
    Button {
        text: viewModel.status === ConnectionStatus.CONNECTED ? "Disconnect" : "Connect"
        onClicked: viewModel.connect()
    }
}
```

### 2. Flight Control Module

```python
# Backend
class FlightViewModel(QObject):
    stateChanged = Signal(FlightState)
    
    def arm(self):
        # Implementation
        pass

# Frontend
FlightControl {
    id: flightControl
    
    // Bind to ViewModel
    property var viewModel: flightViewModel
    
    // UI Elements
    Button {
        text: viewModel.state.armed ? "Disarm" : "Arm"
        onClicked: viewModel.arm()
    }
}
```

### 3. Mission Control Module

```python
# Backend
class MissionViewModel(QObject):
    missionChanged = Signal(Mission)
    
    def startMission(self):
        # Implementation
        pass

# Frontend
MissionControl {
    id: missionControl
    
    // Bind to ViewModel
    property var viewModel: missionViewModel
    
    // UI Elements
    Button {
        text: "Start Mission"
        onClicked: viewModel.startMission()
    }
}
```

## Best Practices

1. **Datenbindung**:
   - Verwende QML-Bindings für direkte UI-Updates
   - Implementiere Signal/Slot-Mechanismen für asynchrone Updates
   - Nutze Properties für reaktive UI-Elemente

2. **Fehlerbehandlung**:
   - Implementiere Error-Handler in ViewModels
   - Zeige Fehlermeldungen in der UI an
   - Protokolliere Fehler für Debugging

3. **Performance**:
   - Nutze Lazy Loading für große Datenmengen
   - Implementiere Caching für häufig verwendete Daten
   - Optimiere UI-Updates

4. **Sicherheit**:
   - Validiere alle Benutzereingaben
   - Implementiere Authentifizierung und Autorisierung
   - Schütze sensible Daten

## Beispiel-Implementation

### Backend (Python)

```python
# main.py
from fastapi import FastAPI
from .viewmodels.main_viewmodel import MainViewModel

app = FastAPI()
viewmodel = MainViewModel()

@app.get("/api/status")
async def get_status():
    return {
        "connection": viewmodel.connection_viewmodel.status,
        "flight": viewmodel.flight_viewmodel.state,
        "mission": viewmodel.mission_viewmodel.current_mission
    }
```

### Frontend (QML)

```qml
// Main.qml
import QtQuick 2.15
import RZGCS.FlightControl 1.0

ApplicationWindow {
    id: window
    
    // ViewModels
    property var connectionViewModel: ConnectionViewModel {}
    property var flightViewModel: FlightViewModel {}
    property var missionViewModel: MissionViewModel {}
    
    // UI
    Column {
        ConnectionControl {
            viewModel: connectionViewModel
        }
        
        FlightControl {
            viewModel: flightViewModel
        }
        
        MissionControl {
            viewModel: missionViewModel
        }
    }
}
```

### Frontend (JavaScript/TypeScript)

```typescript
// flight-control.ts
class FlightControl {
    private api: FlightControlAPI;
    private ws: FlightControlWebSocket;
    
    constructor() {
        this.api = new FlightControlAPI();
        this.ws = new FlightControlWebSocket();
    }
    
    async connect() {
        const result = await this.api.connect();
        if (result.success) {
            this.ws.connect();
        }
    }
}
``` 