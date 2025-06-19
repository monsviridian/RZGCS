"""Flotten-Tests.

Diese Tests überprüfen die Flottensteuerung für die Multi-UAV Funktionalität.
"""

import unittest
from datetime import datetime
from typing import Dict, List, Any, Optional

from flight_control.models.fleet_data import (
    FleetStatus,
    FleetMode,
    UAVStatus,
    UAVMode,
    NetworkTopology,
    EncryptionStatus,
    PositionData,
    VelocityData,
    AttitudeData,
    SensorData,
    ResourceData,
    RoutingTable,
    BandwidthAllocation,
    CommunicationData,
    UAVData,
    FleetData,
    FleetError,
    FleetValidationError,
    FleetCommandError,
    FleetStateError
)
from flight_control.services.fleet_service import FleetService
from flight_control.viewmodels.fleet_viewmodel import FleetViewModel
from flight_control.views.fleet_view import FleetView
from flight_control.controllers.fleet_controller import FleetController

class TestFleetService(unittest.TestCase):
    """Tests für den Flotten-Service."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = FleetService()
    
    def test_initialize_fleet(self):
        """Test: Flotte initialisieren."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flottendaten überprüfen
        self.assertIsNotNone(self.service.fleet_data)
        self.assertEqual(self.service.fleet_data.fleet_id, "fleet_1")
        self.assertEqual(self.service.fleet_data.fleet_name, "Test Fleet")
        self.assertEqual(self.service.fleet_data.fleet_status, FleetStatus.ACTIVE)
        self.assertEqual(self.service.fleet_data.fleet_mode, FleetMode.COORDINATED)
        self.assertEqual(len(self.service.fleet_data.uavs), 0)
        self.assertEqual(self.service.fleet_data.resources.energy, 100.0)
        self.assertEqual(self.service.fleet_data.resources.bandwidth, 100.0)
        self.assertEqual(self.service.fleet_data.resources.load, 0.0)
        self.assertEqual(self.service.fleet_data.communication.network_topology, NetworkTopology.STAR)
        self.assertEqual(self.service.fleet_data.communication.encryption_status, EncryptionStatus.ENABLED)
        self.assertEqual(len(self.service.fleet_data.communication.routing_table.routes), 0)
        self.assertEqual(len(self.service.fleet_data.communication.bandwidth_allocation.allocations), 0)
    
    def test_add_uav(self):
        """Test: UAV zur Flotte hinzufügen."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # UAV hinzufügen
        self.service.add_uav({
            "uav_id": "uav_1",
            "uav_name": "Test UAV 1",
            "uav_mode": UAVMode.AUTONOMOUS.value
        })
        
        # UAV-Daten überprüfen
        self.assertEqual(len(self.service.fleet_data.uavs), 1)
        uav = self.service.fleet_data.uavs[0]
        self.assertEqual(uav.uav_id, "uav_1")
        self.assertEqual(uav.uav_name, "Test UAV 1")
        self.assertEqual(uav.uav_status, UAVStatus.ACTIVE)
        self.assertEqual(uav.uav_mode, UAVMode.AUTONOMOUS)
        self.assertEqual(uav.position.latitude, 0.0)
        self.assertEqual(uav.position.longitude, 0.0)
        self.assertEqual(uav.position.altitude, 0.0)
        self.assertEqual(uav.velocity.vx, 0.0)
        self.assertEqual(uav.velocity.vy, 0.0)
        self.assertEqual(uav.velocity.vz, 0.0)
        self.assertEqual(uav.attitude.roll, 0.0)
        self.assertEqual(uav.attitude.pitch, 0.0)
        self.assertEqual(uav.attitude.yaw, 0.0)
        self.assertEqual(uav.sensor_data.temperature, 0.0)
        self.assertEqual(uav.sensor_data.pressure, 0.0)
        self.assertEqual(uav.sensor_data.humidity, 0.0)
        self.assertEqual(uav.resources.energy, 100.0)
        self.assertEqual(uav.resources.bandwidth, 100.0)
        self.assertEqual(uav.resources.load, 0.0)
        
        # Routing-Tabelle überprüfen
        self.assertEqual(len(self.service.fleet_data.communication.routing_table.routes), 1)
        self.assertEqual(self.service.fleet_data.communication.routing_table.routes["uav_1"], [])
        
        # Bandbreiten-Allokation überprüfen
        self.assertEqual(len(self.service.fleet_data.communication.bandwidth_allocation.allocations), 1)
        self.assertEqual(self.service.fleet_data.communication.bandwidth_allocation.allocations["uav_1"], 0.0)
    
    def test_remove_uav(self):
        """Test: UAV aus Flotte entfernen."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # UAV hinzufügen
        self.service.add_uav({
            "uav_id": "uav_1",
            "uav_name": "Test UAV 1",
            "uav_mode": UAVMode.AUTONOMOUS.value
        })
        
        # UAV entfernen
        self.service.remove_uav("uav_1")
        
        # UAV-Daten überprüfen
        self.assertEqual(len(self.service.fleet_data.uavs), 0)
        
        # Routing-Tabelle überprüfen
        self.assertEqual(len(self.service.fleet_data.communication.routing_table.routes), 0)
        
        # Bandbreiten-Allokation überprüfen
        self.assertEqual(len(self.service.fleet_data.communication.bandwidth_allocation.allocations), 0)
    
    def test_coordinate_fleet(self):
        """Test: Flotte koordinieren."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # UAV hinzufügen
        self.service.add_uav({
            "uav_id": "uav_1",
            "uav_name": "Test UAV 1",
            "uav_mode": UAVMode.AUTONOMOUS.value
        })
        
        # Flotte koordinieren
        self.service.coordinate_fleet()
        
        # UAV-Daten überprüfen
        uav = self.service.fleet_data.uavs[0]
        self.assertEqual(uav.uav_status, UAVStatus.ACTIVE)
        self.assertEqual(uav.uav_mode, UAVMode.AUTONOMOUS)
    
    def test_manage_resources(self):
        """Test: Ressourcen verwalten."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # UAV hinzufügen
        self.service.add_uav({
            "uav_id": "uav_1",
            "uav_name": "Test UAV 1",
            "uav_mode": UAVMode.AUTONOMOUS.value
        })
        
        # Ressourcen verwalten
        self.service.manage_resources()
        
        # UAV-Daten überprüfen
        uav = self.service.fleet_data.uavs[0]
        self.assertEqual(uav.resources.energy, 100.0)
        self.assertEqual(uav.resources.bandwidth, 100.0)
        self.assertEqual(uav.resources.load, 0.0)
    
    def test_avoid_collisions(self):
        """Test: Kollisionen vermeiden."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # UAV hinzufügen
        self.service.add_uav({
            "uav_id": "uav_1",
            "uav_name": "Test UAV 1",
            "uav_mode": UAVMode.AUTONOMOUS.value
        })
        
        # Kollisionen vermeiden
        self.service.avoid_collisions()
        
        # UAV-Daten überprüfen
        uav = self.service.fleet_data.uavs[0]
        self.assertEqual(uav.position.latitude, 0.0)
        self.assertEqual(uav.position.longitude, 0.0)
        self.assertEqual(uav.position.altitude, 0.0)
        self.assertEqual(uav.velocity.vx, 0.0)
        self.assertEqual(uav.velocity.vy, 0.0)
        self.assertEqual(uav.velocity.vz, 0.0)
        self.assertEqual(uav.attitude.roll, 0.0)
        self.assertEqual(uav.attitude.pitch, 0.0)
        self.assertEqual(uav.attitude.yaw, 0.0)

class TestFleetViewModel(unittest.TestCase):
    """Tests für das Flotten-ViewModel."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = FleetService()
        self.viewmodel = FleetViewModel()
        self.viewmodel.set_service(self.service)
    
    def test_fleet_id(self):
        """Test: Flotten-ID."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flotten-ID überprüfen
        self.assertEqual(self.viewmodel.fleet_id, "fleet_1")
    
    def test_fleet_name(self):
        """Test: Flotten-Name."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flotten-Name überprüfen
        self.assertEqual(self.viewmodel.fleet_name, "Test Fleet")
    
    def test_fleet_status(self):
        """Test: Flotten-Status."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flotten-Status überprüfen
        self.assertEqual(self.viewmodel.fleet_status, FleetStatus.ACTIVE.value)
    
    def test_fleet_mode(self):
        """Test: Flotten-Modus."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flotten-Modus überprüfen
        self.assertEqual(self.viewmodel.fleet_mode, FleetMode.COORDINATED.value)
    
    def test_uavs(self):
        """Test: UAVs."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # UAV hinzufügen
        self.service.add_uav({
            "uav_id": "uav_1",
            "uav_name": "Test UAV 1",
            "uav_mode": UAVMode.AUTONOMOUS.value
        })
        
        # UAVs überprüfen
        self.assertEqual(len(self.viewmodel.uavs), 1)
        uav = self.viewmodel.uavs[0]
        self.assertEqual(uav["uav_id"], "uav_1")
        self.assertEqual(uav["uav_name"], "Test UAV 1")
        self.assertEqual(uav["uav_status"], UAVStatus.ACTIVE.value)
        self.assertEqual(uav["uav_mode"], UAVMode.AUTONOMOUS.value)
        self.assertEqual(uav["position"]["latitude"], 0.0)
        self.assertEqual(uav["position"]["longitude"], 0.0)
        self.assertEqual(uav["position"]["altitude"], 0.0)
        self.assertEqual(uav["velocity"]["vx"], 0.0)
        self.assertEqual(uav["velocity"]["vy"], 0.0)
        self.assertEqual(uav["velocity"]["vz"], 0.0)
        self.assertEqual(uav["attitude"]["roll"], 0.0)
        self.assertEqual(uav["attitude"]["pitch"], 0.0)
        self.assertEqual(uav["attitude"]["yaw"], 0.0)
        self.assertEqual(uav["resources"]["energy"], 100.0)
        self.assertEqual(uav["resources"]["bandwidth"], 100.0)
        self.assertEqual(uav["resources"]["load"], 0.0)
    
    def test_resources(self):
        """Test: Ressourcen."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Ressourcen überprüfen
        self.assertEqual(self.viewmodel.resources["energy"], 100.0)
        self.assertEqual(self.viewmodel.resources["bandwidth"], 100.0)
        self.assertEqual(self.viewmodel.resources["load"], 0.0)
    
    def test_communication(self):
        """Test: Kommunikation."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Kommunikation überprüfen
        self.assertEqual(self.viewmodel.communication["network_topology"], NetworkTopology.STAR.value)
        self.assertEqual(self.viewmodel.communication["encryption_status"], EncryptionStatus.ENABLED.value)

class TestFleetView(unittest.TestCase):
    """Tests für die Flotten-View."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = FleetService()
        self.viewmodel = FleetViewModel()
        self.viewmodel.set_service(self.service)
        self.view = FleetView()
        self.view.set_viewmodel(self.viewmodel)
    
    def test_fleet_id_label(self):
        """Test: Flotten-ID-Label."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flotten-ID-Label überprüfen
        self.assertEqual(self.view._fleet_id_label.text(), "fleet_1")
    
    def test_fleet_name_label(self):
        """Test: Flotten-Name-Label."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flotten-Name-Label überprüfen
        self.assertEqual(self.view._fleet_name_label.text(), "Test Fleet")
    
    def test_fleet_status_label(self):
        """Test: Flotten-Status-Label."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flotten-Status-Label überprüfen
        self.assertEqual(self.view._fleet_status_label.text(), FleetStatus.ACTIVE.value)
    
    def test_fleet_mode_combo(self):
        """Test: Flotten-Modus-Combo."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Flotten-Modus-Combo überprüfen
        self.assertEqual(self.view._fleet_mode_combo.currentText(), FleetMode.COORDINATED.value)
    
    def test_uav_table(self):
        """Test: UAV-Tabelle."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # UAV hinzufügen
        self.service.add_uav({
            "uav_id": "uav_1",
            "uav_name": "Test UAV 1",
            "uav_mode": UAVMode.AUTONOMOUS.value
        })
        
        # UAV-Tabelle überprüfen
        self.assertEqual(self.view._uav_table.rowCount(), 1)
        self.assertEqual(self.view._uav_table.item(0, 0).text(), "uav_1")
        self.assertEqual(self.view._uav_table.item(0, 1).text(), "Test UAV 1")
        self.assertEqual(self.view._uav_table.item(0, 2).text(), UAVStatus.ACTIVE.value)
        self.assertEqual(self.view._uav_table.item(0, 3).text(), UAVMode.AUTONOMOUS.value)
        self.assertEqual(self.view._uav_table.item(0, 4).text(), "Lat: 0.000000, Lon: 0.000000, Alt: 0.00")
        self.assertEqual(self.view._uav_table.item(0, 5).text(), "vx: 0.00, vy: 0.00, vz: 0.00")
        self.assertEqual(self.view._uav_table.item(0, 6).text(), "Roll: 0.00, Pitch: 0.00, Yaw: 0.00")
        self.assertEqual(self.view._uav_table.item(0, 7).text(), "E: 100.00, B: 100.00, L: 0.00")
    
    def test_energy_label(self):
        """Test: Energie-Label."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Energie-Label überprüfen
        self.assertEqual(self.view._energy_label.text(), "100.00")
    
    def test_bandwidth_label(self):
        """Test: Bandbreiten-Label."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Bandbreiten-Label überprüfen
        self.assertEqual(self.view._bandwidth_label.text(), "100.00")
    
    def test_load_label(self):
        """Test: Last-Label."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Last-Label überprüfen
        self.assertEqual(self.view._load_label.text(), "0.00")
    
    def test_network_topology_combo(self):
        """Test: Netzwerk-Topologie-Combo."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Netzwerk-Topologie-Combo überprüfen
        self.assertEqual(self.view._network_topology_combo.currentText(), NetworkTopology.STAR.value)
    
    def test_encryption_status_label(self):
        """Test: Verschlüsselungs-Status-Label."""
        # Flotte initialisieren
        self.service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # Verschlüsselungs-Status-Label überprüfen
        self.assertEqual(self.view._encryption_status_label.text(), EncryptionStatus.ENABLED.value)

class TestFleetController(unittest.TestCase):
    """Tests für den Flotten-Controller."""
    
    def setUp(self):
        """Test-Setup."""
        self.controller = FleetController()
    
    def test_show(self):
        """Test: View anzeigen."""
        # View anzeigen
        self.controller.show()
        
        # View überprüfen
        self.assertTrue(self.controller._view.isVisible())
    
    def test_update(self):
        """Test: Regelmäßiges Update."""
        # Flotte initialisieren
        self.controller._service.initialize_fleet({
            "fleet_id": "fleet_1",
            "fleet_name": "Test Fleet",
            "fleet_mode": FleetMode.COORDINATED.value
        })
        
        # UAV hinzufügen
        self.controller._service.add_uav({
            "uav_id": "uav_1",
            "uav_name": "Test UAV 1",
            "uav_mode": UAVMode.AUTONOMOUS.value
        })
        
        # Update auslösen
        self.controller._update()
        
        # UAV-Daten überprüfen
        uav = self.controller._service.fleet_data.uavs[0]
        self.assertEqual(uav.uav_status, UAVStatus.ACTIVE)
        self.assertEqual(uav.uav_mode, UAVMode.AUTONOMOUS)
        self.assertEqual(uav.resources.energy, 100.0)
        self.assertEqual(uav.resources.bandwidth, 100.0)
        self.assertEqual(uav.resources.load, 0.0)
        self.assertEqual(uav.position.latitude, 0.0)
        self.assertEqual(uav.position.longitude, 0.0)
        self.assertEqual(uav.position.altitude, 0.0)
        self.assertEqual(uav.velocity.vx, 0.0)
        self.assertEqual(uav.velocity.vy, 0.0)
        self.assertEqual(uav.velocity.vz, 0.0)
        self.assertEqual(uav.attitude.roll, 0.0)
        self.assertEqual(uav.attitude.pitch, 0.0)
        self.assertEqual(uav.attitude.yaw, 0.0)

if __name__ == "__main__":
    unittest.main() 