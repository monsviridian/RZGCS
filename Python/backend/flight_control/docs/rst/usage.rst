Usage
=====

To use flight_control in a project::

    import flight_control

Flottensteuerung
---------------

Die Flottensteuerung ermöglicht die koordinierte Steuerung mehrerer UAVs.

.. code-block:: python

    from flight_control.controllers.fleet_controller import FleetController

    # Controller erstellen
    controller = FleetController()

    # View anzeigen
    controller.show()

Komponenten
----------

- Modelle
- Services
- ViewModels
- Views
- Controller
- Tests

Modelle
-------

- FleetStatus: Status der Flotte
- FleetMode: Modus der Flotte
- UAVStatus: Status eines UAVs
- UAVMode: Modus eines UAVs
- NetworkTopology: Netzwerk-Topologie
- EncryptionStatus: Verschlüsselungs-Status
- PositionData: Positionsdaten
- VelocityData: Geschwindigkeitsdaten
- AttitudeData: Attitudedaten
- SensorData: Sensordaten
- ResourceData: Ressourcendaten
- RoutingTable: Routing-Tabelle
- BandwidthAllocation: Bandbreiten-Allokation
- CommunicationData: Kommunikationsdaten
- UAVData: UAV-Daten
- FleetData: Flottendaten

Services
--------

- FleetService: Flotten-Service

ViewModels
----------

- FleetViewModel: Flotten-ViewModel

Views
-----

- FleetView: Flotten-View

Controller
----------

- FleetController: Flotten-Controller

Tests
-----

.. code-block:: bash

    python -m unittest discover tests 