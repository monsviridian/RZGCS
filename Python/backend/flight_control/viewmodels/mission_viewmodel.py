"""
ViewModel für die Missionsverwaltung.
Implementiert die Präsentationslogik für die Missionsverwaltung.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot, Property

from ..models.flight_data import Waypoint, Mission, MissionPlan
from ..enums import MissionStatus, WaypointType
from ..services.mission_service import MissionService

class MissionViewModel(QObject):
    """Implementiert die Präsentationslogik für die Missionsverwaltung"""
    
    # Signale
    mission_created = Signal(Mission)
    mission_updated = Signal(Mission)
    mission_deleted = Signal(str)  # Mission ID
    mission_plan_created = Signal(MissionPlan)
    mission_plan_updated = Signal(MissionPlan)
    mission_plan_deleted = Signal(str)  # Plan ID
    error_occurred = Signal(str)
    
    def __init__(self):
        """Initialisiert das ViewModel"""
        super().__init__()
        
        # Service
        self._mission_service: Optional[MissionService] = None
        
        # Missionen und Pläne
        self._missions: Dict[str, Mission] = {}
        self._mission_plans: Dict[str, MissionPlan] = {}
        
    def set_mission_service(self, service: MissionService) -> None:
        """
        Setzt den Mission-Service.
        
        Args:
            service: Mission-Service
        """
        self._mission_service = service
        
        # Signale verbinden
        self._mission_service.mission_created.connect(self._on_mission_created)
        self._mission_service.mission_updated.connect(self._on_mission_updated)
        self._mission_service.mission_deleted.connect(self._on_mission_deleted)
        self._mission_service.mission_plan_created.connect(self._on_mission_plan_created)
        self._mission_service.mission_plan_updated.connect(self._on_mission_plan_updated)
        self._mission_service.mission_plan_deleted.connect(self._on_mission_plan_deleted)
        self._mission_service.error_occurred.connect(self._on_error)
        
    # Properties
    @Property(list, notify=mission_created)
    def missions(self) -> List[Mission]:
        """Gibt alle Missionen zurück"""
        return list(self._missions.values())
        
    @Property(list, notify=mission_plan_created)
    def mission_plans(self) -> List[MissionPlan]:
        """Gibt alle Missionspläne zurück"""
        return list(self._mission_plans.values())
        
    # Slots
    @Slot(str, list)
    def create_mission(self, name: str, waypoints: List[Waypoint]) -> Optional[Mission]:
        """
        Erstellt eine neue Mission.
        
        Args:
            name: Missionsname
            waypoints: Liste der Wegpunkte
            
        Returns:
            Erstellte Mission oder None bei Fehler
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return None
            
        return self._mission_service.create_mission(name, waypoints)
        
    @Slot(Mission)
    def update_mission(self, mission: Mission) -> bool:
        """
        Aktualisiert eine Mission.
        
        Args:
            mission: Zu aktualisierende Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return False
            
        return self._mission_service.update_mission(mission)
        
    @Slot(str)
    def delete_mission(self, mission_id: str) -> bool:
        """
        Löscht eine Mission.
        
        Args:
            mission_id: ID der zu löschenden Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return False
            
        return self._mission_service.delete_mission(mission_id)
        
    @Slot(str)
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """
        Gibt eine Mission zurück.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            Mission oder None wenn nicht gefunden
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return None
            
        return self._mission_service.get_mission(mission_id)
        
    @Slot(Mission)
    def create_mission_plan(self, mission: Mission) -> Optional[MissionPlan]:
        """
        Erstellt einen neuen Missionsplan.
        
        Args:
            mission: Mission
            
        Returns:
            Erstellter Plan oder None bei Fehler
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return None
            
        return self._mission_service.create_mission_plan(mission)
        
    @Slot(MissionPlan)
    def update_mission_plan(self, plan: MissionPlan) -> bool:
        """
        Aktualisiert einen Missionsplan.
        
        Args:
            plan: Zu aktualisierender Plan
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return False
            
        return self._mission_service.update_mission_plan(plan)
        
    @Slot(str)
    def delete_mission_plan(self, mission_id: str) -> bool:
        """
        Löscht einen Missionsplan.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return False
            
        return self._mission_service.delete_mission_plan(mission_id)
        
    @Slot(str)
    def get_mission_plan(self, mission_id: str) -> Optional[MissionPlan]:
        """
        Gibt einen Missionsplan zurück.
        
        Args:
            mission_id: ID der Mission
            
        Returns:
            Plan oder None wenn nicht gefunden
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return None
            
        return self._mission_service.get_mission_plan(mission_id)
        
    @Slot(Mission, str)
    def export_mission(self, mission: Mission, file_path: str) -> bool:
        """
        Exportiert eine Mission.
        
        Args:
            mission: Zu exportierende Mission
            file_path: Dateipfad
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return False
            
        return self._mission_service.export_mission(mission, file_path)
        
    @Slot(str)
    def import_mission(self, file_path: str) -> Optional[Mission]:
        """
        Importiert eine Mission.
        
        Args:
            file_path: Dateipfad
            
        Returns:
            Importierte Mission oder None bei Fehler
        """
        if not self._mission_service:
            self._on_error("Kein Mission-Service verfügbar")
            return None
            
        return self._mission_service.import_mission(file_path)
        
    # Signal-Handler
    def _on_mission_created(self, mission: Mission) -> None:
        """
        Handler für erstellte Missionen.
        
        Args:
            mission: Erstellte Mission
        """
        self._missions[mission.id] = mission
        self.mission_created.emit(mission)
        
    def _on_mission_updated(self, mission: Mission) -> None:
        """
        Handler für aktualisierte Missionen.
        
        Args:
            mission: Aktualisierte Mission
        """
        self._missions[mission.id] = mission
        self.mission_updated.emit(mission)
        
    def _on_mission_deleted(self, mission_id: str) -> None:
        """
        Handler für gelöschte Missionen.
        
        Args:
            mission_id: ID der gelöschten Mission
        """
        if mission_id in self._missions:
            del self._missions[mission_id]
            self.mission_deleted.emit(mission_id)
            
    def _on_mission_plan_created(self, plan: MissionPlan) -> None:
        """
        Handler für erstellte Missionspläne.
        
        Args:
            plan: Erstellter Plan
        """
        self._mission_plans[plan.mission.id] = plan
        self.mission_plan_created.emit(plan)
        
    def _on_mission_plan_updated(self, plan: MissionPlan) -> None:
        """
        Handler für aktualisierte Missionspläne.
        
        Args:
            plan: Aktualisierter Plan
        """
        self._mission_plans[plan.mission.id] = plan
        self.mission_plan_updated.emit(plan)
        
    def _on_mission_plan_deleted(self, mission_id: str) -> None:
        """
        Handler für gelöschte Missionspläne.
        
        Args:
            mission_id: ID der Mission
        """
        if mission_id in self._mission_plans:
            del self._mission_plans[mission_id]
            self.mission_plan_deleted.emit(mission_id)
            
    def _on_error(self, message: str) -> None:
        """
        Handler für Fehlermeldungen.
        
        Args:
            message: Fehlermeldung
        """
        self.error_occurred.emit(message) 