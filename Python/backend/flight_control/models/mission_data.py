"""
Mission-Daten-Struktur.
Implementiert die Datenmodelle für Missionen.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import math

@dataclass
class Position:
    """Position im 3D-Raum"""
    x: float = 0.0  # X-Koordinate in m
    y: float = 0.0  # Y-Koordinate in m
    z: float = 0.0  # Z-Koordinate in m
    
    def distance_to(self, other: 'Position') -> float:
        """
        Berechnet die Distanz zu einer anderen Position.
        
        Args:
            other: Andere Position
            
        Returns:
            Distanz in m
        """
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
        
    def to_dict(self) -> Dict[str, float]:
        """
        Konvertiert die Position in ein Dictionary.
        
        Returns:
            Position als Dictionary
        """
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Position':
        """
        Erstellt eine Position aus einem Dictionary.
        
        Args:
            data: Position als Dictionary
            
        Returns:
            Position
        """
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0)
        )

@dataclass
class Waypoint:
    """Wegpunkt einer Mission"""
    id: str  # Eindeutige ID
    position: Position  # Position
    type: str = "NORMAL"  # Wegpunkt-Typ
    parameters: Dict[str, Any] = field(default_factory=dict)  # Zusätzliche Parameter
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert den Wegpunkt in ein Dictionary.
        
        Returns:
            Wegpunkt als Dictionary
        """
        return {
            "id": self.id,
            "position": self.position.to_dict(),
            "type": self.type,
            "parameters": self.parameters
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Waypoint':
        """
        Erstellt einen Wegpunkt aus einem Dictionary.
        
        Args:
            data: Wegpunkt als Dictionary
            
        Returns:
            Wegpunkt
        """
        return cls(
            id=data["id"],
            position=Position.from_dict(data["position"]),
            type=data.get("type", "NORMAL"),
            parameters=data.get("parameters", {})
        )

@dataclass
class Mission:
    """Mission mit Wegpunkten"""
    id: str  # Eindeutige ID
    name: str  # Name der Mission
    waypoints: List[Waypoint] = field(default_factory=list)  # Liste der Wegpunkte
    created_at: datetime = field(default_factory=datetime.now)  # Erstellungszeitpunkt
    updated_at: datetime = field(default_factory=datetime.now)  # Letztes Update
    
    def add_waypoint(self, waypoint: Waypoint) -> None:
        """
        Fügt einen Wegpunkt hinzu.
        
        Args:
            waypoint: Wegpunkt
        """
        self.waypoints.append(waypoint)
        self.updated_at = datetime.now()
        
    def remove_waypoint(self, waypoint_id: str) -> bool:
        """
        Entfernt einen Wegpunkt.
        
        Args:
            waypoint_id: ID des Wegpunkts
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        for i, waypoint in enumerate(self.waypoints):
            if waypoint.id == waypoint_id:
                self.waypoints.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
        
    def get_waypoint(self, waypoint_id: str) -> Optional[Waypoint]:
        """
        Gibt einen Wegpunkt zurück.
        
        Args:
            waypoint_id: ID des Wegpunkts
            
        Returns:
            Wegpunkt oder None
        """
        for waypoint in self.waypoints:
            if waypoint.id == waypoint_id:
                return waypoint
        return None
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Mission in ein Dictionary.
        
        Returns:
            Mission als Dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "waypoints": [wp.to_dict() for wp in self.waypoints],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mission':
        """
        Erstellt eine Mission aus einem Dictionary.
        
        Args:
            data: Mission als Dictionary
            
        Returns:
            Mission
        """
        return cls(
            id=data["id"],
            name=data["name"],
            waypoints=[Waypoint.from_dict(wp) for wp in data.get("waypoints", [])],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        
    def to_json(self) -> str:
        """
        Konvertiert die Mission in JSON.
        
        Returns:
            Mission als JSON-String
        """
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_json(cls, json_str: str) -> 'Mission':
        """
        Erstellt eine Mission aus JSON.
        
        Args:
            json_str: Mission als JSON-String
            
        Returns:
            Mission
        """
        return cls.from_dict(json.loads(json_str))

@dataclass
class MissionPlan:
    """Missions-Plan mit mehreren Missionen"""
    missions: List[Mission] = field(default_factory=list)  # Liste der Missionen
    created_at: datetime = field(default_factory=datetime.now)  # Erstellungszeitpunkt
    updated_at: datetime = field(default_factory=datetime.now)  # Letztes Update
    
    def add_mission(self, mission: Mission) -> None:
        """
        Fügt eine Mission hinzu.
        
        Args:
            mission: Mission
        """
        self.missions.append(mission)
        self.updated_at = datetime.now()
        
    def remove_mission(self, mission_id: str) -> bool:
        """
        Entfernt eine Mission.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        for i, mission in enumerate(self.missions):
            if mission.id == mission_id:
                self.missions.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
        
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """
        Gibt eine Mission zurück.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            Mission oder None
        """
        for mission in self.missions:
            if mission.id == mission_id:
                return mission
        return None
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert den Missions-Plan in ein Dictionary.
        
        Returns:
            Missions-Plan als Dictionary
        """
        return {
            "missions": [m.to_dict() for m in self.missions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MissionPlan':
        """
        Erstellt einen Missions-Plan aus einem Dictionary.
        
        Args:
            data: Missions-Plan als Dictionary
            
        Returns:
            Missions-Plan
        """
        return cls(
            missions=[Mission.from_dict(m) for m in data.get("missions", [])],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        
    def to_json(self) -> str:
        """
        Konvertiert den Missions-Plan in JSON.
        
        Returns:
            Missions-Plan als JSON-String
        """
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_json(cls, json_str: str) -> 'MissionPlan':
        """
        Erstellt einen Missions-Plan aus JSON.
        
        Args:
            json_str: Missions-Plan als JSON-String
            
        Returns:
            Missions-Plan
        """
        return cls.from_dict(json.loads(json_str)) 