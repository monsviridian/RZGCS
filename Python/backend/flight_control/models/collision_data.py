"""
Datenmodelle für die Kollisionsvermeidung.

Dieses Modul definiert die Datenmodelle für die Kollisionsvermeidung,
einschließlich Objekterkennung, Abstandsberechnung und Ausweichmanöver.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import math

class ObjectType(Enum):
    """Typen von erkannten Objekten."""
    STATIC = "static"  # Statische Objekte (Bäume, Gebäude, etc.)
    DYNAMIC = "dynamic"  # Dynamische Objekte (andere UAVs, Vögel, etc.)
    UNKNOWN = "unknown"  # Unbekannte Objekte

class DetectionMethod(Enum):
    """Methoden zur Objekterkennung."""
    LIDAR = "lidar"  # Lidar-basierte Erkennung
    RADAR = "radar"  # Radar-basierte Erkennung
    CAMERA = "camera"  # Kamera-basierte Erkennung
    FUSION = "fusion"  # Sensorfusion

class AvoidanceStrategy(Enum):
    """Strategien zur Kollisionsvermeidung."""
    STOP = "stop"  # Anhalten
    HOVER = "hover"  # Schweben
    ALTITUDE = "altitude"  # Höhenänderung
    LATERAL = "lateral"  # Seitliche Ausweichbewegung
    COMBINED = "combined"  # Kombinierte Strategie

@dataclass
class DetectedObject:
    """Repräsentiert ein erkanntes Objekt."""
    id: str
    type: ObjectType
    position: Dict[str, float]  # lat, lon, alt
    velocity: Dict[str, float]  # vx, vy, vz
    size: Dict[str, float]  # length, width, height
    confidence: float
    detection_method: DetectionMethod
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CollisionState:
    """Repräsentiert den aktuellen Zustand der Kollisionsvermeidung."""
    is_active: bool = False
    is_error: bool = False
    error_message: Optional[str] = None
    detected_objects: List[DetectedObject] = field(default_factory=list)
    current_strategy: Optional[AvoidanceStrategy] = None
    avoidance_in_progress: bool = False
    last_update: datetime = field(default_factory=datetime.now)

@dataclass
class CollisionStatistics:
    """Statistiken zur Kollisionsvermeidung."""
    total_detections: int = 0
    static_detections: int = 0
    dynamic_detections: int = 0
    unknown_detections: int = 0
    avoidance_maneuvers: int = 0
    successful_avoidance: int = 0
    failed_avoidance: int = 0
    average_response_time: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)

@dataclass
class CollisionEvent:
    """Repräsentiert ein Ereignis in der Kollisionsvermeidung."""
    type: str
    description: str
    severity: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollisionLog:
    """Log für die Kollisionsvermeidung."""
    events: List[CollisionEvent] = field(default_factory=list)
    max_events: int = 1000

    def add_event(self, event: CollisionEvent) -> None:
        """Füge ein Ereignis zum Log hinzu."""
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)

class CollisionError(Exception):
    """Basisklasse für Kollisionsvermeidungsfehler."""
    pass

class DetectionError(CollisionError):
    """Fehler bei der Objekterkennung."""
    pass

class AvoidanceError(CollisionError):
    """Fehler bei der Kollisionsvermeidung."""
    pass

class StrategyError(CollisionError):
    """Fehler bei der Strategieauswahl."""
    pass 