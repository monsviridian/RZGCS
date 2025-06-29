"""
DroneKit Sensor ViewModel für RZGCS
Stellt Sensor- und Telemetriedaten aus DroneKit für die QML-UI bereit
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, Qt

class DroneKitSensorViewModel(QObject):
    """
    ViewModel für Sensordaten aus DroneKit.
    Empfängt Telemetriedaten vom DroneKitConnector und stellt
    sie als Properties und Signale für die QML-UI bereit.
    """
    
    # Signale für UI-Updates
    sensorUpdated = Signal(str, float)
    attitudeChanged = Signal(float, float, float)
    gpsChanged = Signal(float, float, float)
    batteryChanged = Signal(float, float, float)
    
    # UI-Update-Signale
    rollChanged = Signal()
    pitchChanged = Signal()
    yawChanged = Signal()
    latChanged = Signal()
    lonChanged = Signal()
    altChanged = Signal()
    voltageChanged = Signal()
    currentChanged = Signal()
    batteryPercentChanged = Signal()
    
    def __init__(self, drone_connector=None, parent=None):
        """Initialisiert das ViewModel mit optionaler Verbindung zum Connector"""
        super().__init__(parent)
        self._drone_connector = drone_connector
        
        # Initialisiere Standardwerte
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._lat = 0.0
        self._lon = 0.0
        self._alt = 0.0
        self._voltage = 0.0
        self._current = 0.0
        self._battery_percent = 0.0
        
        # UI-Einstellungen
        self._decimals = 1  # Anzahl der Dezimalstellen für die UI
        
        # Verbinde DroneKit-Signale wenn Connector vorhanden
        if self._drone_connector:
            self._connect_signals()
            
        print("DroneKitSensorViewModel initialisiert")
    
    def set_drone_connector(self, drone_connector):
        """Setzt den DroneKit-Connector und verbindet die Signale"""
        self._drone_connector = drone_connector
        self._connect_signals()
    
    def _connect_signals(self):
        """Verbindet alle DroneKit-Signale mit lokalen Slots"""
        if not self._drone_connector:
            return
            
        try:
            # Verbinde DroneKit-Connector-Signale mit unseren Slots
            self._drone_connector.attitudeChanged.connect(self.set_attitude)
            self._drone_connector.gpsChanged.connect(self.set_gps_position)
            self._drone_connector.batteryChanged.connect(self.set_battery_status)
            
            # Weitere Signale können hier verbunden werden
        except Exception as e:
            print(f"Fehler beim Verbinden der DroneKit-Signale: {e}")
    
    def update_from_telemetry(self, telemetry_type, telemetry_data):
        """
        Aktualisiert die Sensordaten aus einem strukturierten Telemetrie-Dictionary
        
        :param telemetry_type: Art der Telemetrie ('attitude', 'gps', 'battery', etc.)
        :param telemetry_data: Dictionary mit den Telemetriedaten
        """
        if telemetry_type == "attitude" and isinstance(telemetry_data, dict):
            roll = telemetry_data.get("roll", 0.0)
            pitch = telemetry_data.get("pitch", 0.0)
            yaw = telemetry_data.get("yaw", 0.0)
            self.set_attitude(roll, pitch, yaw)
            
        elif telemetry_type == "gps" and isinstance(telemetry_data, dict):
            lat = telemetry_data.get("lat", 0.0)
            lon = telemetry_data.get("lon", 0.0)
            alt = telemetry_data.get("alt", 0.0)
            self.set_gps_position(lat, lon, alt)
            
        elif telemetry_type == "battery" and isinstance(telemetry_data, dict):
            voltage = telemetry_data.get("voltage", 0.0)
            current = telemetry_data.get("current", 0.0)
            remaining = telemetry_data.get("level", 0.0)
            self.set_battery_status(voltage, current, remaining)
    
    def update_sensor_value(self, sensor_id, value):
        """
        Aktualisiert einen einzelnen Sensorwert (Legacy-Methode für Kompatibilität)
        """
        # Konvertiert den Wert zu float
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return
        
        # Aktualisiert den entsprechenden Sensor
        if sensor_id == "roll":
            self._roll = float_value
            self.rollChanged.emit()
        elif sensor_id == "pitch":
            self._pitch = float_value
            self.pitchChanged.emit()
        elif sensor_id == "yaw":
            self._yaw = float_value
            self.yawChanged.emit()
        elif sensor_id == "lat":
            self._lat = float_value
            self.latChanged.emit()
        elif sensor_id == "lon":
            self._lon = float_value
            self.lonChanged.emit()
        elif sensor_id == "alt":
            self._alt = float_value
            self.altChanged.emit()
        elif sensor_id == "voltage":
            self._voltage = float_value
            self.voltageChanged.emit()
        elif sensor_id == "current":
            self._current = float_value
            self.currentChanged.emit()
        elif sensor_id == "battery_percent":
            self._battery_percent = float_value
            self.batteryPercentChanged.emit()
        
        # Signal für generische Sensor-Updates
        self.sensorUpdated.emit(sensor_id, float_value)
    
    # Attitude (Roll, Pitch, Yaw)
    @Property(float, notify=rollChanged)
    def roll(self):
        return round(self._roll, self._decimals)
    
    @Property(float, notify=pitchChanged)
    def pitch(self):
        return round(self._pitch, self._decimals)
    
    @Property(float, notify=yawChanged)
    def yaw(self):
        return round(self._yaw, self._decimals)
    
    # GPS Position (Lat, Lon, Alt)
    @Property(float, notify=latChanged)
    def lat(self):
        return round(self._lat, self._decimals)
    
    @Property(float, notify=lonChanged)
    def lon(self):
        return round(self._lon, self._decimals)
    
    @Property(float, notify=altChanged)
    def alt(self):
        return round(self._alt, self._decimals)
    
    # Battery Status (Voltage, Current, Percent)
    @Property(float, notify=voltageChanged)
    def voltage(self):
        return round(self._voltage, self._decimals)
    
    @Property(float, notify=currentChanged)
    def current(self):
        return round(self._current, self._decimals)
    
    @Property(float, notify=batteryPercentChanged)
    def battery_percent(self):
        return round(self._battery_percent, self._decimals)
    
    # === Setter-Methoden ===
    
    @Slot(float, float, float)
    def set_attitude(self, roll, pitch, yaw):
        """Setzt die Attitude-Werte (in Grad)"""
        if self._roll != roll or self._pitch != pitch or self._yaw != yaw:
            self._roll = roll
            self._pitch = pitch
            self._yaw = yaw
            
            # Signale emittieren
            self.rollChanged.emit()
            self.pitchChanged.emit()
            self.yawChanged.emit()
            self.attitudeChanged.emit(roll, pitch, yaw)
            
            # Einzelne Sensor-Updates emittieren
            self.sensorUpdated.emit("roll", roll)
            self.sensorUpdated.emit("pitch", pitch)
            self.sensorUpdated.emit("yaw", yaw)
    
    @Slot(float, float, float)
    def set_gps_position(self, lat, lon, alt):
        """Setzt die GPS-Positionswerte"""
        if self._lat != lat or self._lon != lon or self._alt != alt:
            self._lat = lat
            self._lon = lon
            self._alt = alt
            
            # Signale emittieren
            self.latChanged.emit()
            self.lonChanged.emit()
            self.altChanged.emit()
            self.gpsChanged.emit(lat, lon, alt)
            
            # Einzelne Sensor-Updates emittieren
            self.sensorUpdated.emit("lat", lat)
            self.sensorUpdated.emit("lon", lon)
            self.sensorUpdated.emit("alt", alt)
    
    @Slot(float, float, float)
    def set_battery_status(self, voltage, current, remaining):
        """Setzt die Batterie-Statuswerte"""
        if self._voltage != voltage or self._current != current or self._battery_percent != remaining:
            self._voltage = voltage
            self._current = current
            self._battery_percent = remaining
            
            # Signale emittieren
            self.voltageChanged.emit()
            self.currentChanged.emit()
            self.batteryPercentChanged.emit()
            self.batteryChanged.emit(voltage, current, remaining)
            
            # Einzelne Sensor-Updates emittieren
            self.sensorUpdated.emit("voltage", voltage)
            self.sensorUpdated.emit("current", current)
            self.sensorUpdated.emit("battery_percent", remaining)
