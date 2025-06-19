"""
Telemetrie-Paket für RZGCS.
Enthält Komponenten zur Verarbeitung und Verwaltung von Telemetriedaten.
"""

# Mache MAVLinkTelemetryAdapter verfügbar
from .mavlink_telemetry_adapter import MAVLinkTelemetryAdapter

__all__ = ['MAVLinkTelemetryAdapter']
