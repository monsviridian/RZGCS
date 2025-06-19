"""Systemtests für Flugplanung."""

import unittest
import time
from datetime import datetime
from flight_planning.services.flight_planning_service import FlightPlanningService
from flight_planning.viewmodels.flight_planning_viewmodel import FlightPlanningViewModel
from flight_planning.models.flight_planning_data import (
    Waypoint,
    Route,
    Mission,
    MissionStatus,
    MissionEvent,
    MissionLog,
    FlightPlanningError,
    FlightPlanningValidationError,
    FlightPlanningCommandError,
    FlightPlanningMissionError
)

class TestFlightPlanningSystem(unittest.TestCase):
    """Systemtests für Flugplanung."""

    def setUp(self):
        """Test-Setup."""
        self.service = FlightPlanningService()
        self.viewmodel = FlightPlanningViewModel()
        self.viewmodel.set_service(self.service)

    def test_complete_mission_flow(self):
        """Test vollständiger Missions-Flow."""
        # Mission erstellen
        mission = self.viewmodel.create_mission("Test Mission")
        self.assertIsNotNone(mission)
        self.assertEqual(mission.name, "Test Mission")
        self.assertEqual(mission.status, MissionStatus.INACTIVE)

        # Route hinzufügen
        route = self.viewmodel.add_route("Test Route")
        self.assertIsNotNone(route)
        self.assertEqual(route.name, "Test Route")
        self.assertEqual(len(mission.routes), 1)

        # Wegpunkte hinzufügen
        positions = [
            {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
            {'latitude': 48.137155, 'longitude': 11.576125, 'altitude': 101.0},
            {'latitude': 48.137156, 'longitude': 11.576126, 'altitude': 102.0}
        ]
        waypoints = []
        for i, pos in enumerate(positions):
            waypoint = self.viewmodel.add_waypoint(
                route.id,
                "WAYPOINT",
                pos,
                "NONE"
            )
            waypoints.append(waypoint)
            self.assertIsNotNone(waypoint)
            self.assertEqual(len(route.waypoints), i + 1)

        # Mission starten
        self.viewmodel.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Durch alle Wegpunkte gehen
        for i in range(len(waypoints) - 1):
            self.viewmodel.next_waypoint()
            self.assertEqual(self.service.current_waypoint, waypoints[i + 1])
            time.sleep(0.1)  # Simuliere Flugzeit

        # Mission abschließen
        self.viewmodel.complete_mission()
        self.assertEqual(mission.status, MissionStatus.COMPLETED)

        # Log überprüfen
        self.assertGreater(len(self.service.log.events), 0)
        self.assertEqual(self.service.log.last_event.description, "Mission completed")

    def test_pause_resume_flow(self):
        """Test Pause-Fortsetzen-Flow."""
        # Mission erstellen
        mission = self.viewmodel.create_mission("Test Mission")
        route = self.viewmodel.add_route("Test Route")

        # Wegpunkte hinzufügen
        positions = [
            {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
            {'latitude': 48.137155, 'longitude': 11.576125, 'altitude': 101.0}
        ]
        for pos in positions:
            self.viewmodel.add_waypoint(
                route.id,
                "WAYPOINT",
                pos,
                "NONE"
            )

        # Mission starten
        self.viewmodel.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Zum ersten Wegpunkt gehen
        self.viewmodel.next_waypoint()
        time.sleep(0.1)  # Simuliere Flugzeit

        # Mission pausieren
        self.viewmodel.pause_mission()
        self.assertEqual(mission.status, MissionStatus.PAUSED)

        # Kurz warten
        time.sleep(0.1)

        # Mission fortsetzen
        self.viewmodel.resume_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Zum nächsten Wegpunkt gehen
        self.viewmodel.next_waypoint()
        time.sleep(0.1)  # Simuliere Flugzeit

        # Mission abschließen
        self.viewmodel.complete_mission()
        self.assertEqual(mission.status, MissionStatus.COMPLETED)

    def test_error_recovery_flow(self):
        """Test Fehler-Wiederherstellungs-Flow."""
        # Mission erstellen
        mission = self.viewmodel.create_mission("Test Mission")
        route = self.viewmodel.add_route("Test Route")

        # Wegpunkte hinzufügen
        positions = [
            {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
            {'latitude': 48.137155, 'longitude': 11.576125, 'altitude': 101.0}
        ]
        for pos in positions:
            self.viewmodel.add_waypoint(
                route.id,
                "WAYPOINT",
                pos,
                "NONE"
            )

        # Mission starten
        self.viewmodel.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Zum ersten Wegpunkt gehen
        self.viewmodel.next_waypoint()
        time.sleep(0.1)  # Simuliere Flugzeit

        # Mission abbrechen (simuliere Fehler)
        self.viewmodel.abort_mission()
        self.assertEqual(mission.status, MissionStatus.ERROR)

        # Neue Mission erstellen
        new_mission = self.viewmodel.create_mission("Recovery Mission")
        self.assertIsNotNone(new_mission)
        self.assertEqual(new_mission.status, MissionStatus.INACTIVE)

        # Neue Route hinzufügen
        new_route = self.viewmodel.add_route("Recovery Route")
        self.assertIsNotNone(new_route)

        # Neue Wegpunkte hinzufügen
        for pos in positions:
            self.viewmodel.add_waypoint(
                new_route.id,
                "WAYPOINT",
                pos,
                "NONE"
            )

        # Neue Mission starten
        self.viewmodel.start_mission()
        self.assertEqual(new_mission.status, MissionStatus.ACTIVE)

        # Durch alle Wegpunkte gehen
        for _ in range(len(positions) - 1):
            self.viewmodel.next_waypoint()
            time.sleep(0.1)  # Simuliere Flugzeit

        # Neue Mission abschließen
        self.viewmodel.complete_mission()
        self.assertEqual(new_mission.status, MissionStatus.COMPLETED)

    def test_concurrent_operations(self):
        """Test gleichzeitige Operationen."""
        # Mission erstellen
        mission = self.viewmodel.create_mission("Test Mission")
        route = self.viewmodel.add_route("Test Route")

        # Wegpunkte hinzufügen
        positions = [
            {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
            {'latitude': 48.137155, 'longitude': 11.576125, 'altitude': 101.0}
        ]
        for pos in positions:
            self.viewmodel.add_waypoint(
                route.id,
                "WAYPOINT",
                pos,
                "NONE"
            )

        # Mission starten
        self.viewmodel.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Gleichzeitige Operationen
        for _ in range(10):
            # Zum nächsten Wegpunkt gehen
            self.viewmodel.next_waypoint()
            time.sleep(0.01)  # Simuliere Flugzeit

            # Mission pausieren
            self.viewmodel.pause_mission()
            time.sleep(0.01)

            # Mission fortsetzen
            self.viewmodel.resume_mission()
            time.sleep(0.01)

        # Mission abschließen
        self.viewmodel.complete_mission()
        self.assertEqual(mission.status, MissionStatus.COMPLETED)

    def test_long_running_mission(self):
        """Test länger laufende Mission."""
        # Mission erstellen
        mission = self.viewmodel.create_mission("Long Mission")
        route = self.viewmodel.add_route("Long Route")

        # Viele Wegpunkte hinzufügen
        for i in range(100):
            position = {
                'latitude': 48.137154 + i * 0.000001,
                'longitude': 11.576124 + i * 0.000001,
                'altitude': 100.0 + i
            }
            self.viewmodel.add_waypoint(
                route.id,
                "WAYPOINT",
                position,
                "NONE"
            )

        # Mission starten
        self.viewmodel.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Durch alle Wegpunkte gehen
        for _ in range(99):
            self.viewmodel.next_waypoint()
            time.sleep(0.01)  # Simuliere Flugzeit

        # Mission abschließen
        self.viewmodel.complete_mission()
        self.assertEqual(mission.status, MissionStatus.COMPLETED)

        # Log überprüfen
        self.assertGreater(len(self.service.log.events), 0)
        self.assertEqual(self.service.log.last_event.description, "Mission completed")

if __name__ == '__main__':
    unittest.main() 