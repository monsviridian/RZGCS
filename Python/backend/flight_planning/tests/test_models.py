"""Unit-Tests für Flugplanungs-Datenmodelle."""

import unittest
from datetime import datetime
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

class TestWaypoint(unittest.TestCase):
    """Tests für Waypoint-Klasse."""

    def setUp(self):
        """Test-Setup."""
        self.position = {
            'latitude': 48.137154,
            'longitude': 11.576124,
            'altitude': 100.0
        }
        self.waypoint = Waypoint(
            id="WP1",
            type="WAYPOINT",
            position=self.position,
            action="NONE"
        )

    def test_waypoint_creation(self):
        """Test Waypoint-Erstellung."""
        self.assertEqual(self.waypoint.id, "WP1")
        self.assertEqual(self.waypoint.type.value, "WAYPOINT")
        self.assertEqual(self.waypoint.position, self.position)
        self.assertEqual(self.waypoint.action.value, "NONE")

    def test_waypoint_validation(self):
        """Test Waypoint-Validierung."""
        # Ungültige Position
        with self.assertRaises(FlightPlanningValidationError):
            Waypoint(
                id="WP1",
                type="WAYPOINT",
                position={'latitude': 91.0, 'longitude': 0.0, 'altitude': 0.0},
                action="NONE"
            )

        # Ungültiger Typ
        with self.assertRaises(FlightPlanningValidationError):
            Waypoint(
                id="WP1",
                type="INVALID",
                position=self.position,
                action="NONE"
            )

        # Ungültige Aktion
        with self.assertRaises(FlightPlanningValidationError):
            Waypoint(
                id="WP1",
                type="WAYPOINT",
                position=self.position,
                action="INVALID"
            )

class TestRoute(unittest.TestCase):
    """Tests für Route-Klasse."""

    def setUp(self):
        """Test-Setup."""
        self.route = Route(
            id="R1",
            name="Test Route",
            waypoints=[]
        )

    def test_route_creation(self):
        """Test Route-Erstellung."""
        self.assertEqual(self.route.id, "R1")
        self.assertEqual(self.route.name, "Test Route")
        self.assertEqual(len(self.route.waypoints), 0)

    def test_add_waypoint(self):
        """Test Wegpunkt-Hinzufügen."""
        waypoint = Waypoint(
            id="WP1",
            type="WAYPOINT",
            position={'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
            action="NONE"
        )
        self.route.add_waypoint(waypoint)
        self.assertEqual(len(self.route.waypoints), 1)
        self.assertEqual(self.route.waypoints[0], waypoint)

    def test_remove_waypoint(self):
        """Test Wegpunkt-Entfernen."""
        waypoint = Waypoint(
            id="WP1",
            type="WAYPOINT",
            position={'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
            action="NONE"
        )
        self.route.add_waypoint(waypoint)
        self.route.remove_waypoint("WP1")
        self.assertEqual(len(self.route.waypoints), 0)

class TestMission(unittest.TestCase):
    """Tests für Mission-Klasse."""

    def setUp(self):
        """Test-Setup."""
        self.mission = Mission(
            id="M1",
            name="Test Mission",
            status=MissionStatus.INACTIVE,
            routes=[]
        )

    def test_mission_creation(self):
        """Test Mission-Erstellung."""
        self.assertEqual(self.mission.id, "M1")
        self.assertEqual(self.mission.name, "Test Mission")
        self.assertEqual(self.mission.status, MissionStatus.INACTIVE)
        self.assertEqual(len(self.mission.routes), 0)

    def test_add_route(self):
        """Test Route-Hinzufügen."""
        route = Route(id="R1", name="Test Route", waypoints=[])
        self.mission.add_route(route)
        self.assertEqual(len(self.mission.routes), 1)
        self.assertEqual(self.mission.routes[0], route)

    def test_remove_route(self):
        """Test Route-Entfernen."""
        route = Route(id="R1", name="Test Route", waypoints=[])
        self.mission.add_route(route)
        self.mission.remove_route("R1")
        self.assertEqual(len(self.mission.routes), 0)

    def test_mission_status_transitions(self):
        """Test Missions-Status-Übergänge."""
        # INACTIVE -> ACTIVE
        self.mission.start()
        self.assertEqual(self.mission.status, MissionStatus.ACTIVE)

        # ACTIVE -> PAUSED
        self.mission.pause()
        self.assertEqual(self.mission.status, MissionStatus.PAUSED)

        # PAUSED -> ACTIVE
        self.mission.resume()
        self.assertEqual(self.mission.status, MissionStatus.ACTIVE)

        # ACTIVE -> COMPLETED
        self.mission.complete()
        self.assertEqual(self.mission.status, MissionStatus.COMPLETED)

        # COMPLETED -> ERROR
        self.mission.set_error("Test error")
        self.assertEqual(self.mission.status, MissionStatus.ERROR)

class TestMissionEvent(unittest.TestCase):
    """Tests für MissionEvent-Klasse."""

    def test_event_creation(self):
        """Test Event-Erstellung."""
        event = MissionEvent(
            timestamp=datetime.now(),
            event_type="STATUS_CHANGE",
            description="Mission started"
        )
        self.assertEqual(event.event_type, "STATUS_CHANGE")
        self.assertEqual(event.description, "Mission started")

class TestMissionLog(unittest.TestCase):
    """Tests für MissionLog-Klasse."""

    def setUp(self):
        """Test-Setup."""
        self.log = MissionLog()

    def test_add_event(self):
        """Test Event-Hinzufügen."""
        event = MissionEvent(
            timestamp=datetime.now(),
            event_type="STATUS_CHANGE",
            description="Mission started"
        )
        self.log.add_event(event)
        self.assertEqual(len(self.log.events), 1)
        self.assertEqual(self.log.events[0], event)

    def test_last_event(self):
        """Test Letztes-Event-Abfrage."""
        event1 = MissionEvent(
            timestamp=datetime.now(),
            event_type="STATUS_CHANGE",
            description="Mission started"
        )
        event2 = MissionEvent(
            timestamp=datetime.now(),
            event_type="STATUS_CHANGE",
            description="Mission completed"
        )
        self.log.add_event(event1)
        self.log.add_event(event2)
        self.assertEqual(self.log.last_event, event2)

class TestFlightPlanningErrors(unittest.TestCase):
    """Tests für Flugplanungs-Fehlerklassen."""

    def test_base_error(self):
        """Test Basis-Fehlerklasse."""
        error = FlightPlanningError("Test error")
        self.assertEqual(str(error), "Test error")

    def test_validation_error(self):
        """Test Validierungs-Fehlerklasse."""
        error = FlightPlanningValidationError("Invalid waypoint")
        self.assertEqual(str(error), "Invalid waypoint")

    def test_command_error(self):
        """Test Kommando-Fehlerklasse."""
        error = FlightPlanningCommandError("Invalid command")
        self.assertEqual(str(error), "Invalid command")

    def test_mission_error(self):
        """Test Missions-Fehlerklasse."""
        error = FlightPlanningMissionError("Mission failed")
        self.assertEqual(str(error), "Mission failed")

if __name__ == '__main__':
    unittest.main() 