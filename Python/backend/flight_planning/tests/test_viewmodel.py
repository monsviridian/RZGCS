"""Unit-Tests für Flugplanungs-ViewModel."""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
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

class TestFlightPlanningViewModel(unittest.TestCase):
    """Tests für FlightPlanningViewModel-Klasse."""

    def setUp(self):
        """Test-Setup."""
        self.viewmodel = FlightPlanningViewModel()
        self.mock_service = Mock()
        self.viewmodel.set_service(self.mock_service)

    def test_set_service(self):
        """Test Service-Setzung."""
        self.assertEqual(self.viewmodel._service, self.mock_service)

    def test_mission_properties(self):
        """Test Missions-Properties."""
        # Mock-Mission erstellen
        mock_mission = Mock(spec=Mission)
        mock_mission.id = "M1"
        mock_mission.name = "Test Mission"
        mock_mission.status = MissionStatus.ACTIVE
        self.mock_service.mission = mock_mission

        # Properties testen
        self.assertTrue(self.viewmodel.has_mission)
        self.assertEqual(self.viewmodel.mission_id, "M1")
        self.assertEqual(self.viewmodel.mission_name, "Test Mission")
        self.assertEqual(self.viewmodel.mission_status, "ACTIVE")
        self.assertTrue(self.viewmodel.is_mission_active)
        self.assertFalse(self.viewmodel.is_mission_paused)
        self.assertFalse(self.viewmodel.is_mission_completed)
        self.assertFalse(self.viewmodel.is_mission_error)

    def test_route_properties(self):
        """Test Routen-Properties."""
        # Mock-Route erstellen
        mock_route = Mock(spec=Route)
        mock_route.id = "R1"
        mock_route.name = "Test Route"
        self.mock_service.current_route = mock_route

        # Properties testen
        self.assertTrue(self.viewmodel.has_route)
        self.assertEqual(self.viewmodel.route_id, "R1")
        self.assertEqual(self.viewmodel.route_name, "Test Route")

    def test_waypoint_properties(self):
        """Test Wegpunkt-Properties."""
        # Mock-Wegpunkt erstellen
        mock_waypoint = Mock(spec=Waypoint)
        mock_waypoint.id = "WP1"
        mock_waypoint.type.value = "WAYPOINT"
        mock_waypoint.action.value = "NONE"
        mock_waypoint.position = {
            'latitude': 48.137154,
            'longitude': 11.576124,
            'altitude': 100.0
        }
        self.mock_service.current_waypoint = mock_waypoint

        # Properties testen
        self.assertTrue(self.viewmodel.has_waypoint)
        self.assertEqual(self.viewmodel.waypoint_id, "WP1")
        self.assertEqual(self.viewmodel.waypoint_type, "WAYPOINT")
        self.assertEqual(self.viewmodel.waypoint_action, "NONE")
        self.assertEqual(
            self.viewmodel.waypoint_position,
            [48.137154, 11.576124, 100.0]
        )

    def test_log_properties(self):
        """Test Log-Properties."""
        # Mock-Log erstellen
        mock_log = Mock(spec=MissionLog)
        mock_event = Mock(spec=MissionEvent)
        mock_event.description = "Test event"
        mock_log.events = [mock_event]
        mock_log.last_event = mock_event
        self.mock_service.log = mock_log

        # Properties testen
        self.assertEqual(self.viewmodel.log_events, ["Test event"])
        self.assertEqual(self.viewmodel.last_event, "Test event")

    def test_create_mission(self):
        """Test Mission-Erstellung."""
        # Mission erstellen
        self.viewmodel.create_mission("Test Mission")
        self.mock_service.create_mission.assert_called_once_with(
            "Test Mission",
            None
        )

        # Mission mit Parametern erstellen
        self.viewmodel.create_mission("Test Mission", {"param": "value"})
        self.mock_service.create_mission.assert_called_with(
            "Test Mission",
            {"param": "value"}
        )

    def test_add_route(self):
        """Test Route-Hinzufügen."""
        # Route hinzufügen
        self.viewmodel.add_route("Test Route")
        self.mock_service.add_route.assert_called_once_with(
            "Test Route",
            None
        )

        # Route mit Parametern hinzufügen
        self.viewmodel.add_route("Test Route", {"param": "value"})
        self.mock_service.add_route.assert_called_with(
            "Test Route",
            {"param": "value"}
        )

    def test_add_waypoint(self):
        """Test Wegpunkt-Hinzufügen."""
        # Wegpunkt hinzufügen
        position = {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0}
        self.viewmodel.add_waypoint(
            "R1",
            "WAYPOINT",
            position,
            "NONE"
        )
        self.mock_service.add_waypoint.assert_called_once_with(
            "R1",
            "WAYPOINT",
            position,
            "NONE",
            None
        )

        # Wegpunkt mit Parametern hinzufügen
        self.viewmodel.add_waypoint(
            "R1",
            "WAYPOINT",
            position,
            "NONE",
            {"param": "value"}
        )
        self.mock_service.add_waypoint.assert_called_with(
            "R1",
            "WAYPOINT",
            position,
            "NONE",
            {"param": "value"}
        )

    def test_update_waypoint(self):
        """Test Wegpunkt-Aktualisierung."""
        # Wegpunkt aktualisieren
        position = {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0}
        self.viewmodel.update_waypoint(
            "WP1",
            position,
            "PHOTO"
        )
        self.mock_service.update_waypoint.assert_called_once_with(
            "WP1",
            position,
            "PHOTO",
            None
        )

        # Wegpunkt mit Parametern aktualisieren
        self.viewmodel.update_waypoint(
            "WP1",
            position,
            "PHOTO",
            {"param": "value"}
        )
        self.mock_service.update_waypoint.assert_called_with(
            "WP1",
            position,
            "PHOTO",
            {"param": "value"}
        )

    def test_delete_waypoint(self):
        """Test Wegpunkt-Löschung."""
        # Wegpunkt löschen
        self.viewmodel.delete_waypoint("WP1")
        self.mock_service.delete_waypoint.assert_called_once_with("WP1")

    def test_mission_control(self):
        """Test Missions-Steuerung."""
        # Mission starten
        self.viewmodel.start_mission()
        self.mock_service.start_mission.assert_called_once()

        # Mission pausieren
        self.viewmodel.pause_mission()
        self.mock_service.pause_mission.assert_called_once()

        # Mission fortsetzen
        self.viewmodel.resume_mission()
        self.mock_service.resume_mission.assert_called_once()

        # Mission abschließen
        self.viewmodel.complete_mission()
        self.mock_service.complete_mission.assert_called_once()

        # Mission abbrechen
        self.viewmodel.abort_mission()
        self.mock_service.abort_mission.assert_called_once()

    def test_next_waypoint(self):
        """Test Nächster-Wegpunkt."""
        # Zum nächsten Wegpunkt gehen
        self.viewmodel.next_waypoint()
        self.mock_service.next_waypoint.assert_called_once()

    def test_error_handling(self):
        """Test Fehlerbehandlung."""
        # Service-Fehler
        self.mock_service.create_mission.side_effect = FlightPlanningError("Test error")
        with self.assertRaises(FlightPlanningError):
            self.viewmodel.create_mission("Test Mission")

        # Validierungs-Fehler
        self.mock_service.add_waypoint.side_effect = FlightPlanningValidationError("Invalid waypoint")
        with self.assertRaises(FlightPlanningValidationError):
            self.viewmodel.add_waypoint(
                "R1",
                "WAYPOINT",
                {'latitude': 48.137154, 'longitude': 11.576124, 'altitude': 100.0},
                "NONE"
            )

        # Kommando-Fehler
        self.mock_service.start_mission.side_effect = FlightPlanningCommandError("Invalid command")
        with self.assertRaises(FlightPlanningCommandError):
            self.viewmodel.start_mission()

        # Missions-Fehler
        self.mock_service.complete_mission.side_effect = FlightPlanningMissionError("Mission failed")
        with self.assertRaises(FlightPlanningMissionError):
            self.viewmodel.complete_mission()

if __name__ == '__main__':
    unittest.main() 