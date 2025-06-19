# Flottensteuerung

Die Flottensteuerung ermöglicht die koordinierte Steuerung mehrerer UAVs.

## Installation

```bash
pip install -r requirements.txt
```

## Verwendung

```python
from flight_control.controllers.fleet_controller import FleetController

# Controller erstellen
controller = FleetController()

# View anzeigen
controller.show()
```

## Komponenten

- [Modelle](fleet.md#modelle)
- [Services](fleet.md#service)
- [ViewModels](fleet.md#viewmodel)
- [Views](fleet.md#view)
- [Controller](fleet.md#controller)
- [Tests](fleet.md#tests)

## Lizenz

MIT 