"""Datenmodelle für Flugsteuerung.

Dieses Modul enthält die Datenmodelle für die Flugsteuerung.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any

class FlightMode(Enum):
    """Flugmodus.
    
    Attributes:
        MANUAL: Manueller Modus
        ASSISTED: Unterstützter Modus
        AUTONOMOUS: Autonomer Modus
        EMERGENCY: Notfallmodus
    """
    MANUAL = "MANUAL"
    ASSISTED = "ASSISTED"
    AUTONOMOUS = "AUTONOMOUS"
    EMERGENCY = "EMERGENCY"

class ControlMode(Enum):
    """Steuerungsmodus.
    
    Attributes:
        POSITION: Positionssteuerung
        VELOCITY: Geschwindigkeitssteuerung
        ATTITUDE: Attitudensteuerung
        RATE: Ratensteuerung
    """
    POSITION = "POSITION"
    VELOCITY = "VELOCITY"
    ATTITUDE = "ATTITUDE"
    RATE = "RATE"

class ControlAxis(Enum):
    """Steuerungsachse.
    
    Attributes:
        ROLL: Rollachse
        PITCH: Nickachse
        YAW: Gierachse
        THRUST: Schubachse
    """
    ROLL = "ROLL"
    PITCH = "PITCH"
    YAW = "YAW"
    THRUST = "THRUST"

class ControlCommand(Enum):
    """Steuerungsbefehl.
    
    Attributes:
        HOLD: Halten
        MOVE: Bewegen
        ROTATE: Rotieren
        THRUST: Schub
    """
    HOLD = "HOLD"
    MOVE = "MOVE"
    ROTATE = "ROTATE"
    THRUST = "THRUST"

class ControlStatus(Enum):
    """Steuerungsstatus.
    
    Attributes:
        IDLE: Inaktiv
        ACTIVE: Aktiv
        COMPLETED: Abgeschlossen
        ERROR: Fehler
    """
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

@dataclass
class ControlInput:
    """Steuerungseingabe.
    
    Attributes:
        axis: Steuerungsachse
        command: Steuerungsbefehl
        value: Wert
        timestamp: Zeitstempel
    """
    axis: ControlAxis
    command: ControlCommand
    value: float
    timestamp: datetime

@dataclass
class ControlOutput:
    """Steuerungsausgabe.
    
    Attributes:
        axis: Steuerungsachse
        value: Wert
        timestamp: Zeitstempel
    """
    axis: ControlAxis
    value: float
    timestamp: datetime

@dataclass
class ControlState:
    """Steuerungszustand.
    
    Attributes:
        mode: Flugmodus
        control_mode: Steuerungsmodus
        status: Steuerungsstatus
        inputs: Steuerungseingaben
        outputs: Steuerungsausgaben
        timestamp: Zeitstempel
    """
    mode: FlightMode
    control_mode: ControlMode
    status: ControlStatus
    inputs: List[ControlInput]
    outputs: List[ControlOutput]
    timestamp: datetime

@dataclass
class ControlEvent:
    """Steuerungsereignis.
    
    Attributes:
        event_type: Ereignistyp
        description: Beschreibung
        timestamp: Zeitstempel
    """
    event_type: str
    description: str
    timestamp: datetime

@dataclass
class ControlLog:
    """Steuerungslog.
    
    Attributes:
        events: Ereignisse
    """
    events: List[ControlEvent]

    def add_event(self, event: ControlEvent):
        """Fügt ein Ereignis hinzu.
        
        Args:
            event: Das hinzuzufügende Ereignis
        """
        self.events.append(event)

    @property
    def last_event(self) -> Optional[ControlEvent]:
        """Gibt das letzte Ereignis zurück.
        
        Returns:
            Das letzte Ereignis oder None
        """
        return self.events[-1] if self.events else None

class FlightControlError(Exception):
    """Basis-Fehlerklasse für Flugsteuerung."""
    pass

class FlightControlValidationError(FlightControlError):
    """Fehler bei der Validierung."""
    pass

class FlightControlCommandError(FlightControlError):
    """Fehler bei der Ausführung eines Befehls."""
    pass

class FlightControlStateError(FlightControlError):
    """Fehler bei der Zustandsverwaltung."""
    pass

class FlightStatus(Enum):
    """Flugstatus."""
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    ARMED = "ARMED"
    DISARMED = "DISARMED"
    TAKEOFF = "TAKEOFF"
    LANDING = "LANDING"
    ERROR = "ERROR"

@dataclass
class FlightState:
    """Flugzustand."""
    is_active: bool = False
    is_error: bool = False
    error_message: Optional[str] = None
    mode: FlightMode = FlightMode.MANUAL
    status: FlightStatus = FlightStatus.INACTIVE
    is_armed: bool = False
    is_flying: bool = False
    is_landing: bool = False
    is_taking_off: bool = False
    last_update: Optional[datetime] = None
    
    def update(self, **kwargs):
        """Zustand aktualisieren."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_update = datetime.now()
    
    def validate(self):
        """Zustand validieren."""
        if self.is_error and not self.error_message:
            raise ValueError("Error message required when in error state")
        if self.is_flying and not self.is_armed:
            raise ValueError("Cannot be flying when not armed")
        if self.is_landing and not self.is_flying:
            raise ValueError("Cannot be landing when not flying")
        if self.is_taking_off and not self.is_armed:
            raise ValueError("Cannot be taking off when not armed")

@dataclass
class FlightStatistics:
    """Flugstatistiken."""
    total_flights: int = 0
    total_flight_time: float = 0.0
    total_distance: float = 0.0
    max_altitude: float = 0.0
    max_speed: float = 0.0
    total_landings: int = 0
    total_takeoffs: int = 0
    total_errors: int = 0
    mode_changes: int = 0
    last_flight_time: float = 0.0
    last_flight_distance: float = 0.0
    last_flight_max_altitude: float = 0.0
    last_flight_max_speed: float = 0.0
    
    def update(self, **kwargs):
        """Statistiken aktualisieren."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate(self):
        """Statistiken berechnen."""
        if self.total_flights > 0:
            self.last_flight_time = self.total_flight_time / self.total_flights
            self.last_flight_distance = self.total_distance / self.total_flights
            self.last_flight_max_altitude = self.max_altitude
            self.last_flight_max_speed = self.max_speed

@dataclass
class FlightEvent:
    """Flugereignis."""
    event_type: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Nach der Initialisierung."""
        if not self.event_type:
            raise ValueError("Event type is required")
        if not self.description:
            raise ValueError("Description is required")

@dataclass
class FlightLog:
    """Fluglog."""
    events: List[FlightEvent] = field(default_factory=list)
    last_event: Optional[FlightEvent] = None
    
    def add_event(self, event: FlightEvent):
        """Event hinzufügen."""
        self.events.append(event)
        self.last_event = event
    
    def clear(self):
        """Log leeren."""
        self.events.clear()
        self.last_event = None

class FlightError(Exception):
    """Basisklasse für Flugfehler."""
    pass

class FlightValidationError(FlightError):
    """Validierungsfehler."""
    pass

class FlightCommandError(FlightError):
    """Befehlsfehler."""
    pass

class FlightModeError(FlightError):
    """Modusfehler."""
    pass 