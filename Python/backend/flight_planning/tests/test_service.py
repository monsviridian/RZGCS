"""Unit-Tests für Flugplanungs-Service."""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from flight_planning.services.flight_planning_service import FlightPlanningService
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

class TestFlightPlanningService(unittest.TestCase):
    """Tests für FlightPlanningService-Klasse."""

    def setUp(self):
        """Test-Setup."""
        self.service = FlightPlanningService()
        self.mock_mission = Mock(spec=Mission)
        self.mock_route = Mock(spec=Route)
        self.mock_waypoint = Mock(spec=Waypoint)

    def test_create_mission(self):
        """Test Mission-Erstellung."""
        # Mission erstellen
        mission = self.service.create_mission("Test Mission")
        self.assertIsNotNone(mission)
        self.assertEqual(mission.name, "Test Mission")
        self.assertEqual(mission.status, MissionStatus.INACTIVE)

        # Mission mit Parametern erstellen
        mission = self.service.create_mission("Test Mission", {"param": "value"})
        self.assertIsNotNone(mission)
        self.assertEqual(mission.name, "Test Mission")

    def test_add_route(self):
        """Test Route-Hinzufügen."""
        # Mission erstellen
        mission = self.service.create_mission("Test Mission")

        # Route hinzufügen
        route = self.service.add_route("Test Route")
        self.assertIsNotNone(route)
        self.assertEqual(route.name, "Test Route")
        self.assertEqual(len(mission.routes), 1)

        # Route mit Parametern hinzufügen
        route = self.service.add_route("Test Route", {"param": "value"})
        self.assertIsNotNone(route)
        self.assertEqual(route.name, "Test Route")

    def test_add_waypoint(self):
        """Test Wegpunkt-Hinzufügen."""
        # Mission und Route erstellen
        mission = self.service.create_mission("Test Mission")
        route = self.service.add_route("Test Route")

        # Wegpunkt hinzufügen
        position = {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0}
        waypoint = self.service.add_waypoint(
            route.id,
            "WAYPOINT",
            position,
            "NONE"
        )
        self.assertIsNotNone(waypoint)
        self.assertEqual(waypoint.type.value, "WAYPOINT")
        self.assertEqual(waypoint.position, position)
        self.assertEqual(waypoint.action.value, "NONE")
        self.assertEqual(len(route.waypoints), 1)

        # Wegpunkt mit Parametern hinzufügen
        waypoint = self.service.add_waypoint(
            route.id,
            "WAYPOINT",
            position,
            "NONE",
            {"param": "value"}
        )
        self.assertIsNotNone(waypoint)
        self.assertEqual(waypoint.type.value, "WAYPOINT")

    def test_update_waypoint(self):
        """Test Wegpunkt-Aktualisierung."""
        # Mission, Route und Wegpunkt erstellen
        mission = self.service.create_mission("Test Mission")
        route = self.service.add_route("Test Route")
        position = {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0}
        waypoint = self.service.add_waypoint(
            route.id,
            "WAYPOINT",
            position,
            "NONE"
        )

        # Wegpunkt aktualisieren
        new_position = {'latitude': 48.137155, 'longitude': 11.576125, 'altitude': 101.0}
        self.service.update_waypoint(
            waypoint.id,
            new_position,
            "PHOTO"
        )
        self.assertEqual(waypoint.position, new_position)
        self.assertEqual(waypoint.action.value, "PHOTO")

    def test_delete_waypoint(self):
        """Test Wegpunkt-Löschung."""
        # Mission, Route und Wegpunkt erstellen
        mission = self.service.create_mission("Test Mission")
        route = self.service.add_route("Test Route")
        position = {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0}
        waypoint = self.service.add_waypoint(
            route.id,
            "WAYPOINT",
            position,
            "NONE"
        )

        # Wegpunkt löschen
        self.service.delete_waypoint(waypoint.id)
        self.assertEqual(len(route.waypoints), 0)

    def test_start_mission(self):
        """Test Missions-Start."""
        # Mission erstellen
        mission = self.service.create_mission("Test Mission")

        # Mission starten
        self.service.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

    def test_pause_mission(self):
        """Test Missions-Pause."""
        # Mission erstellen und starten
        mission = self.service.create_mission("Test Mission")
        self.service.start_mission()

        # Mission pausieren
        self.service.pause_mission()
        self.assertEqual(mission.status, MissionStatus.PAUSED)

    def test_resume_mission(self):
        """Test Missions-Fortsetzung."""
        # Mission erstellen, starten und pausieren
        mission = self.service.create_mission("Test Mission")
        self.service.start_mission()
        self.service.pause_mission()

        # Mission fortsetzen
        self.service.resume_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

    def test_complete_mission(self):
        """Test Missions-Abschluss."""
        # Mission erstellen und starten
        mission = self.service.create_mission("Test Mission")
        self.service.start_mission()

        # Mission abschließen
        self.service.complete_mission()
        self.assertEqual(mission.status, MissionStatus.COMPLETED)

    def test_abort_mission(self):
        """Test Missions-Abbruch."""
        # Mission erstellen und starten
        mission = self.service.create_mission("Test Mission")
        self.service.start_mission()

        # Mission abbrechen
        self.service.abort_mission()
        self.assertEqual(mission.status, MissionStatus.ERROR)

    def test_next_waypoint(self):
        """Test Nächster-Wegpunkt."""
        # Mission, Route und Wegpunkte erstellen
        mission = self.service.create_mission("Test Mission")
        route = self.service.add_route("Test Route")
        position1 = {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0}
        position2 = {'latitude': 48.137155, 'longitude': 11.576125, 'altitude': 101.0}
        waypoint1 = self.service.add_waypoint(
            route.id,
            "WAYPOINT",
            position1,
            "NONE"
        )
        waypoint2 = self.service.add_waypoint(
            route.id,
            "WAYPOINT",
            position2,
            "NONE"
        )

        # Mission starten
        self.service.start_mission()

        # Zum nächsten Wegpunkt gehen
        self.service.next_waypoint()
        self.assertEqual(self.service.current_waypoint, waypoint2)

    def test_error_handling(self):
        """Test Fehlerbehandlung."""
        # Keine aktive Mission
        with self.assertRaises(FlightPlanningCommandError):
            self.service.start_mission()

        # Ungültige Route
        with self.assertRaises(FlightPlanningValidationError):
            self.service.add_waypoint(
                "invalid_route",
                "WAYPOINT",
                {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
                "NONE"
            )

        # Ungültiger Wegpunkt
        with self.assertRaises(FlightPlanningValidationError):
            self.service.update_waypoint(
                "invalid_waypoint",
                {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
                "NONE"
            )

if __name__ == '__main__':
    unittest.main() 