"""
ViewModel für die Telemetrie.
Implementiert die Präsentationslogik für die Telemetrie.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot, Property

from ..models.flight_data import Position, FlightState
from ..enums import FlightStatus, FlightMode
from ..services.telemetry_service import TelemetryService

class TelemetryViewModel(QObject):
    """Implementiert die Präsentationslogik für die Telemetrie"""
    
    # Signale
    state_updated = Signal(FlightState)
    position_updated = Signal(Position)
    mode_updated = Signal(FlightMode)
    status_updated = Signal(FlightStatus)
    parameters_updated = Signal(dict)
    error_occurred = Signal(str)
    
    # Spezifische Signale für QML-Komponenten
    altitudeChanged = Signal(float)  # Höhe in Metern
    groundSpeedChanged = Signal(float)  # Geschwindigkeit über Grund in m/s
    airSpeedChanged = Signal(float)  # Geschwindigkeit in der Luft in m/s
    verticalSpeedChanged = Signal(float)  # Vertikale Geschwindigkeit in m/s
    headingChanged = Signal(float)  # Kurs in Grad
    batteryPercentChanged = Signal(int)  # Batterie in Prozent (0-100)
    batteryVoltageChanged = Signal(float)  # Batteriespannung in Volt
    batteryCurrentChanged = Signal(float)  # Batteriestrom in Ampere
    distToWPChanged = Signal(float)  # Distanz zum Wegpunkt in Metern
    throttlePercentChanged = Signal(int)  # Gasregler in Prozent (0-100)
    
    def __init__(self):
        """Initialisiert das ViewModel"""
        super().__init__()
        
        # Initialisiere den Flugzustand
        from ..models.flight_data import FlightState, Position
        from ..enums import FlightMode, FlightStatus
        
        # Defensives Vorgehen zur FlightMode-Initialisierung
        try:
            default_mode = FlightMode.UNKNOWN
        except AttributeError:
            # Fallback, falls UNKNOWN nicht verfügbar ist
            # Versuche einen anderen Wert zu verwenden oder den ersten Wert der Enumeration
            try:
                default_mode = FlightMode.MANUAL
            except AttributeError:
                # Letzte Chance: Verwende den ersten Wert der Enumeration
                default_mode = list(FlightMode)[0] if list(FlightMode) else None
        
        self._state = FlightState(
            position=Position(0.0, 0.0, 0.0),
            mode=default_mode,  # Verwende den sicher ermittelten Modus
            armed=False,
            status=FlightStatus.DISCONNECTED,
            parameters={}
        )
        
        # Zusätzliche Dictionary-Felder für QML-Kompatibilität
        self._state._attitude_dict = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
        self._state._velocity_dict = {'groundspeed': 0.0, 'airspeed': 0.0, 'vertical_speed': 0.0}
        self._state._navigation_dict = {'distance_to_waypoint': 0.0}
        self._state._battery_dict = {'voltage': 0.0, 'current': 0.0, 'remaining': 0.0}
        self._state._vfr_hud_dict = {'groundspeed': 0.0, 'airspeed': 0.0, 'heading': 0.0, 'throttle': 0.0}
        
        # Telemetrie-Service (wird später gesetzt)
        self._telemetry_service = None
        
        # Sensor-Model (wird später gesetzt)
        self._sensor_model = None
        
    def set_telemetry_service(self, service: TelemetryService) -> None:
        """
        Setzt den Telemetrie-Service.
        
        Args:
            service: Telemetrie-Service
        """
        self._telemetry_service = service
        
        # Signale verbinden (camelCase-Konvention)
        self._telemetry_service.stateChanged.connect(self._on_state_updated)
        self._telemetry_service.telemetryUpdated.connect(self._on_position_updated)
        self._telemetry_service.modeChanged.connect(self._on_mode_updated)
        # Hinweis: status_updated entspricht im TelemetryService stateChanged
        self._telemetry_service.stateChanged.connect(self._on_status_updated)
        # Hinweis: parameters_updated ist Teil der telemetryUpdated
        self._telemetry_service.telemetryUpdated.connect(self._on_parameters_updated)
        self._telemetry_service.errorOccurred.connect(self._on_error)
        
    def set_sensor_model(self, sensor_model) -> None:
        """
        Setzt das Sensor-Model.
        
        Args:
            sensor_model: Das Sensor-Model für die Telemetriedaten
        """
        self._sensor_model = sensor_model
        
    # Properties
    @Property(FlightState, notify=state_updated)
    def state(self) -> FlightState:
        """Gibt den aktuellen Flugzustand zurück"""
        return self._state
        
    @Property(Position, notify=position_updated)
    def position(self) -> Position:
        """Gibt die aktuelle Position zurück"""
        return self._state.position
        
    @Property(FlightMode, notify=mode_updated)
    def mode(self) -> FlightMode:
        """Gibt den aktuellen Flugmodus zurück"""
        return self._state.mode
        
    @Property(FlightStatus, notify=status_updated)
    def status(self) -> FlightStatus:
        """Gibt den aktuellen Status zurück"""
        return self._state.status
        
    @Property(dict, notify=parameters_updated)
    def parameters(self) -> Dict[str, Any]:
        """Gibt die aktuellen Parameter zurück"""
        return self._state.parameters
        
    # Slots
    @Slot(str, object)
    def set_parameter(self, name: str, value: Any) -> bool:
        """
        Setzt einen Parameter.
        
        Args:
            name: Parametername
            value: Parameterwert
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._telemetry_service:
            self._on_error("Kein Telemetrie-Service verfügbar")
            return False
            
        return self._telemetry_service.set_parameter(name, value)
        
    @Slot(str)
    def get_parameter(self, name: str) -> Optional[Any]:
        """
        Gibt einen Parameter zurück.
        
        Args:
            name: Parametername
            
        Returns:
            Parameterwert oder None wenn nicht gefunden
        """
        if not self._telemetry_service:
            self._on_error("Kein Telemetrie-Service verfügbar")
            return None
            
        return self._telemetry_service.get_parameter(name)
        
    @Slot(str)
    def export_telemetry(self, file_path: str) -> bool:
        """
        Exportiert die Telemetriedaten.
        
        Args:
            file_path: Dateipfad
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._telemetry_service:
            self._on_error("Kein Telemetrie-Service verfügbar")
            return False
            
        return self._telemetry_service.export_telemetry(file_path)
        
    @Slot(str)
    def import_telemetry(self, file_path: str) -> bool:
        """
        Importiert Telemetriedaten.
        
        Args:
            file_path: Dateipfad
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._telemetry_service:
            self._on_error("Kein Telemetrie-Service verfügbar")
            return False
            
        return self._telemetry_service.import_telemetry(file_path)
        
    @Slot(float)
    def set_distance_to_waypoint(self, distance: float) -> None:
        """
        Aktualisiert die Distanz zum aktuellen Wegpunkt.
        
        Args:
            distance: Distanz zum Wegpunkt in Metern
        """
        # Aktualisiere das Dictionary für QML-Kompatibilität
        self._state._navigation_dict['distance_to_waypoint'] = distance
        
        # Emittiere spezifisches Signal für QML
        self.distToWPChanged.emit(distance)
        
        # Informiere die UI über Änderung
        self.state_updated.emit(self._state)
        
    # Signal-Handler
    def _on_state_updated(self, state: FlightState) -> None:
        """
        Aktualisiert den Zustand.
        
        Args:
            state: Neuer Zustand
        """
        self._state = state
        
        # Aktualisiere die Sensordaten
        if hasattr(self, '_sensor_model') and self._sensor_model:
            # Attitude
            if state.attitude:
                self._sensor_model.update_sensor("Roll", state.attitude.x, "°")
                self._sensor_model.update_sensor("Pitch", state.attitude.y, "°")
                self._sensor_model.update_sensor("Yaw", state.attitude.z, "°")
            
            # Velocity
            if state.velocity:
                self._sensor_model.update_sensor("Ground Speed", state.velocity.x, "m/s")
                self._sensor_model.update_sensor("Air Speed", state.velocity.y, "m/s")
                self._sensor_model.update_sensor("Vertical Speed", state.velocity.z, "m/s")
            
            # Position
            if state.position:
                self._sensor_model.update_sensor("Altitude", state.position.z, "m")
                self._sensor_model.update_sensor("Latitude", state.position.x, "°")
                self._sensor_model.update_sensor("Longitude", state.position.y, "°")
            
            # Battery
            if state.battery_level is not None:
                self._sensor_model.update_sensor("Battery", state.battery_level, "%")
            
            # GPS
            if state.gps_fix is not None:
                self._sensor_model.update_sensor("GPS Fix", "Yes" if state.gps_fix else "No", "")
            if state.gps_satellites is not None:
                self._sensor_model.update_sensor("GPS Satellites", state.gps_satellites, "")
            
            # Signal
            if state.signal_strength is not None:
                self._sensor_model.update_sensor("Signal", state.signal_strength, "%")
        
        # Emittiere die Signale
        self.state_updated.emit(self._state)
        if state.position:
            self.position_updated.emit(state.position)
        if state.mode:
            self.mode_updated.emit(state.mode)
        if state.status:
            self.status_updated.emit(state.status)
        if state.parameters:
            self.parameters_updated.emit(state.parameters)
        
    def _on_position_updated(self, position: Position) -> None:
        """
        Handler für Positionsaktualisierungen.
        
        Args:
            position: Neue Position
        """
        self._state.position = position
        self.position_updated.emit(position)
        
    def _on_mode_updated(self, mode: FlightMode) -> None:
        """
        Handler für Modusaktualisierungen.
        
        Args:
            mode: Neuer Modus
        """
        self._state.mode = mode
        self.mode_updated.emit(mode)
        
    def _on_status_updated(self, status: FlightStatus) -> None:
        """
        Handler für Statusaktualisierungen.
        
        Args:
            status: Neuer Status
        """
        self._state.status = status
        self.status_updated.emit(status)
        
    def _on_parameters_updated(self, parameters: Dict[str, Any]) -> None:
        """
        Handler für Parameteraktualisierungen.
        
        Args:
            parameters: Neue Parameter
        """
        self._state.parameters = parameters
        self.parameters_updated.emit(parameters)
        
    def _on_error(self, message: str) -> None:
        """
        Handler für Fehlermeldungen.
        
        Args:
            message: Fehlermeldung
        """
        self.error_occurred.emit(message) 
        
    # Direct sensor update methods for MAVLink integration
    @Slot(float, float, float)
    def set_attitude(self, roll: float, pitch: float, yaw: float) -> None:
        """
        Aktualisiert die Lage (Attitude) des Fluggeräts.
        
        Args:
            roll: Roll-Winkel in Grad
            pitch: Pitch-Winkel in Grad
            yaw: Yaw-Winkel in Grad (Heading)
        """
        # Aktualisiere das Dictionary für QML-Kompatibilität
        self._state._attitude_dict['roll'] = roll
        self._state._attitude_dict['pitch'] = pitch
        self._state._attitude_dict['yaw'] = yaw
        
        # Aktualisiere das Position-Objekt (x=roll, y=pitch, z=yaw)
        if self._state.attitude is None:
            self._state.attitude = Position(x=roll, y=pitch, z=yaw)
        else:
            self._state.attitude.x = roll
            self._state.attitude.y = pitch
            self._state.attitude.z = yaw
        
        # Aktualisiere das Sensor-Model
        if self._sensor_model:
            self._sensor_model.update_from_telemetry('attitude', {
                'roll': roll,
                'pitch': pitch,
                'yaw': yaw
            })
        
        # Emittiere spezifische Signale für QML
        self.headingChanged.emit(yaw)  # Yaw als Heading verwenden
        
        # Informiere die UI über Änderung
        self.state_updated.emit(self._state)
        
    @Slot(float, float, float)
    def set_gps_position(self, latitude: float, longitude: float, altitude: float) -> None:
        """
        Aktualisiert die GPS-Position.
        
        Args:
            latitude: Breitengrad
            longitude: Längengrad
            altitude: Höhe über Meeresspiegel
        """
        # Aktualisiere die Position im Zustand
        new_position = Position(latitude, longitude, altitude)
        self._state.position = new_position
        
        # Aktualisiere das Sensor-Model
        if self._sensor_model:
            self._sensor_model.update_from_telemetry('gps', {
                'lat': latitude,
                'lon': longitude,
                'alt': altitude
            })
        
        # Emittiere spezifische Signale für QML
        self.altitudeChanged.emit(altitude)
        
        # Informiere die UI über Änderung
        self.position_updated.emit(new_position)
        self.state_updated.emit(self._state)
        
    @Slot(float, float, float)
    def set_battery_status(self, voltage: float, current: float, remaining: float) -> None:
        """
        Aktualisiert den Batteriestatus.
        
        Args:
            voltage: Batteriespannung in Volt
            current: Batteriestrom in Ampere
            remaining: Verbleibende Kapazität in Prozent
        """
        # Aktualisiere das Dictionary für QML-Kompatibilität
        self._state._battery_dict['voltage'] = voltage
        self._state._battery_dict['current'] = current
        self._state._battery_dict['remaining'] = remaining
        
        # Aktualisiere das Sensor-Model
        if self._sensor_model:
            self._sensor_model.update_from_telemetry('battery', {
                'voltage': voltage,
                'current': current,
                'percentage': remaining
            })
        
        # Emittiere spezifische Signale für QML
        self.batteryVoltageChanged.emit(voltage)
        self.batteryCurrentChanged.emit(current)
        self.batteryPercentChanged.emit(int(remaining))
        
        # Informiere die UI über Änderung
        self.state_updated.emit(self._state)
        
    @Slot(float, float, float)
    def set_velocity(self, groundspeed: float, airspeed: float, vertical_speed: float) -> None:
        """
        Aktualisiert die Geschwindigkeitsdaten.
        
        Args:
            groundspeed: Geschwindigkeit über Grund in m/s
            airspeed: Geschwindigkeit in der Luft in m/s
            vertical_speed: Vertikale Geschwindigkeit in m/s
        """
        # Aktualisiere das Dictionary für QML-Kompatibilität
        self._state._velocity_dict['groundspeed'] = groundspeed
        self._state._velocity_dict['airspeed'] = airspeed
        self._state._velocity_dict['vertical_speed'] = vertical_speed
        
        # Aktualisiere das Sensor-Model
        if self._sensor_model:
            self._sensor_model.update_from_telemetry('velocity', {
                'groundspeed': groundspeed,
                'airspeed': airspeed,
                'vertical_speed': vertical_speed
            })
        
        # Emittiere spezifische Signale für QML
        self.groundSpeedChanged.emit(groundspeed)
        self.airSpeedChanged.emit(airspeed)
        self.verticalSpeedChanged.emit(vertical_speed)
        
        # Informiere die UI über Änderung
        self.state_updated.emit(self._state)
        
    @Slot(float, float, float, float)
    def set_vfr_hud(self, groundspeed: float, airspeed: float, heading: float, throttle: float) -> None:
        """
        Aktualisiert die VFR HUD Daten.
        
        Args:
            groundspeed: Geschwindigkeit über Grund in m/s
            airspeed: Geschwindigkeit in der Luft in m/s
            heading: Kurs in Grad
            throttle: Gas in Prozent
        """
        # Aktualisiere das Dictionary für QML-Kompatibilität
        self._state._vfr_hud_dict['groundspeed'] = groundspeed
        self._state._vfr_hud_dict['airspeed'] = airspeed
        self._state._vfr_hud_dict['heading'] = heading
        self._state._vfr_hud_dict['throttle'] = throttle
        
        # Aktualisiere das Sensor-Model
        if self._sensor_model:
            self._sensor_model.update_from_telemetry('vfr_hud', {
                'groundspeed': groundspeed,
                'airspeed': airspeed,
                'heading': heading,
                'throttle': throttle
            })
        
        # Emittiere spezifische Signale für QML
        self.groundSpeedChanged.emit(groundspeed)
        self.airSpeedChanged.emit(airspeed)
        self.headingChanged.emit(heading)
        self.throttlePercentChanged.emit(int(throttle))
        
        # Informiere die UI über Änderung
        self.state_updated.emit(self._state)
    