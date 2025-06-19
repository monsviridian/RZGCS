#!/usr/bin/env python3
"""
RZGCS mit MAVSDK-MVVM-Integration
Startskript, das die neue MVVM-Architektur verwendet
"""

import os
import sys
from pathlib import Path

# Stellen Sie sicher, dass Python die Module finden kann
sys.path.insert(0, str(Path(__file__).resolve().parent / "Python"))

# Importiere die bestehende Hauptfunktion
from mavsdk_rzgcs_main import main

# Startmeldung ausgeben
print("Starte RZGCS mit MAVSDK-MVVM-Integration...")
print("Alle MVVM-Komponenten befinden sich im Ordner Python/rzgcs/mvvm/")
print("- Model: drone_model.py")
print("- Service: mavsdk_connector_service.py, mavsdk_connection_helper.py")
print("- ViewModel: mavsdk_drone_viewmodel.py")

# Anwendung starten
if __name__ == "__main__":
    sys.exit(main())
