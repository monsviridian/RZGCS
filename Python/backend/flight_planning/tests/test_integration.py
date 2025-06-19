"""Integrationstests für Flugplanung."""

import unittest
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

class TestFlightPlanningIntegration(unittest.TestCase):
    """Integrationstests für Flugplanung."""

    def setUp(self):
        """Test-Setup."""
        self.service = FlightPlanningService()
        self.viewmodel = FlightPlanningViewModel()
        self.viewmodel.set_service(self.service)

    def test_mission_creation_flow(self):
        """Test Missions-Erstellungs-Flow."""
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
        position1 = {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0}
        position2 = {'latitude': 48.137155, 'longitude': 11.576125, 'altitude': 101.0}
        waypoint1 = self.viewmodel.add_waypoint(
            route.id,
            "WAYPOINT",
            position1,
            "NONE"
        )
        waypoint2 = self.viewmodel.add_waypoint(
            route.id,
            "WAYPOINT",
            position2,
            "NONE"
        )
        self.assertIsNotNone(waypoint1)
        self.assertIsNotNone(waypoint2)
        self.assertEqual(len(route.waypoints), 2)

        # Mission starten
        self.viewmodel.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Zum nächsten Wegpunkt gehen
        self.viewmodel.next_waypoint()
        self.assertEqual(self.service.current_waypoint, waypoint2)

        # Mission abschließen
        self.viewmodel.complete_mission()
        self.assertEqual(mission.status, MissionStatus.COMPLETED)

    def test_mission_pause_flow(self):
        """Test Missions-Pause-Flow."""
        # Mission erstellen und starten
        mission = self.viewmodel.create_mission("Test Mission")
        self.viewmodel.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Mission pausieren
        self.viewmodel.pause_mission()
        self.assertEqual(mission.status, MissionStatus.PAUSED)

        # Mission fortsetzen
        self.viewmodel.resume_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

    def test_mission_error_flow(self):
        """Test Missions-Fehler-Flow."""
        # Mission erstellen und starten
        mission = self.viewmodel.create_mission("Test Mission")
        self.viewmodel.start_mission()
        self.assertEqual(mission.status, MissionStatus.ACTIVE)

        # Mission abbrechen
        self.viewmodel.abort_mission()
        self.assertEqual(mission.status, MissionStatus.ERROR)

    def test_waypoint_management_flow(self):
        """Test Wegpunkt-Verwaltungs-Flow."""
        # Mission und Route erstellen
        mission = self.viewmodel.create_mission("Test Mission")
        route = self.viewmodel.add_route("Test Route")

        # Wegpunkt hinzufügen
        position = {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0}
        waypoint = self.viewmodel.add_waypoint(
            route.id,
            "WAYPOINT",
            position,
            "NONE"
        )
        self.assertIsNotNone(waypoint)
        self.assertEqual(len(route.waypoints), 1)

        # Wegpunkt aktualisieren
        new_position = {'latitude': 48.137155, 'longitude': 11.576125, 'altitude': 101.0}
        self.viewmodel.update_waypoint(
            waypoint.id,
            new_position,
            "PHOTO"
        )
        self.assertEqual(waypoint.position, new_position)
        self.assertEqual(waypoint.action.value, "PHOTO")

        # Wegpunkt löschen
        self.viewmodel.delete_waypoint(waypoint.id)
        self.assertEqual(len(route.waypoints), 0)

    def test_log_flow(self):
        """Test Log-Flow."""
        # Mission erstellen
        mission = self.viewmodel.create_mission("Test Mission")
        self.assertEqual(len(self.service.log.events), 1)
        self.assertEqual(self.service.log.last_event.description, "Mission created")

        # Mission starten
        self.viewmodel.start_mission()
        self.assertEqual(len(self.service.log.events), 2)
        self.assertEqual(self.service.log.last_event.description, "Mission started")

        # Mission abschließen
        self.viewmodel.complete_mission()
        self.assertEqual(len(self.service.log.events), 3)
        self.assertEqual(self.service.log.last_event.description, "Mission completed")

    def test_error_handling_flow(self):
        """Test Fehlerbehandlungs-Flow."""
        # Keine aktive Mission
        with self.assertRaises(FlightPlanningCommandError):
            self.viewmodel.start_mission()

        # Ungültige Route
        with self.assertRaises(FlightPlanningValidationError):
            self.viewmodel.add_waypoint(
                "invalid_route",
                "WAYPOINT",
                {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
                "NONE"
            )

        # Ungültiger Wegpunkt
        with self.assertRaises(FlightPlanningValidationError):
            self.viewmodel.update_waypoint(
                "invalid_waypoint",
                {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
                "NONE"
            )

if __name__ == '__main__':
    unittest.main() 