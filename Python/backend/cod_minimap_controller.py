from PySide6.QtCore import QObject, Slot, Signal, Property, QTimer
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "RZGCS"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class CoDMinimapController(QObject):
    """
    Controller für die Call of Duty-ähnliche Minimap.
    Stellt Verbindungen zwischen den Drohnendaten und der Minimap-Anzeige her.
    """
    
    # Signale für Updates an die Minimap
    positionChanged = Signal(float, float, float)  # lat, lon, alt
    headingChanged = Signal(float)  # 0-360 Grad
    waypointsChanged = Signal(list)  # Liste von Wegpunkten
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._latitude = 51.505600  # Default Position (wie in SimpleMapView)
        self._longitude = 7.452400
        self._altitude = 100.0
        self._heading = 0.0
        self._waypoints = []
        self._map_style = "satellite"  # Optionen: "satellite", "terrain", "night"
        self._zoom_level = 1.0
        
    @Property(float)
    def latitude(self):
        return self._latitude
        
    @latitude.setter
    def latitude(self, value):
        if self._latitude != value:
            self._latitude = value
            self.positionChanged.emit(self._latitude, self._longitude, self._altitude)
            
    @Property(float)
    def longitude(self):
        return self._longitude
        
    @longitude.setter
    def longitude(self, value):
        if self._longitude != value:
            self._longitude = value
            self.positionChanged.emit(self._latitude, self._longitude, self._altitude)
            
    @Property(float)
    def altitude(self):
        return self._altitude
        
    @altitude.setter
    def altitude(self, value):
        if self._altitude != value:
            self._altitude = value
            self.positionChanged.emit(self._latitude, self._longitude, self._altitude)
            
    @Property(float)
    def heading(self):
        return self._heading
        
    @heading.setter
    def heading(self, value):
        if self._heading != value:
            self._heading = value
            self.headingChanged.emit(self._heading)
            
    @Property(str)
    def mapStyle(self):
        return self._map_style
        
    @mapStyle.setter
    def mapStyle(self, value):
        if value in ["satellite", "terrain", "night"] and self._map_style != value:
            self._map_style = value
            
    @Property(float)
    def zoomLevel(self):
        return self._zoom_level
        
    @zoomLevel.setter
    def zoomLevel(self, value):
        if 0.5 <= value <= 5.0 and self._zoom_level != value:
            self._zoom_level = value
    
    @Slot(float, float, float)
    def updatePosition(self, lat, lon, alt):
        """Aktualisiert die Position der Drohne."""
        self.latitude = lat
        self.longitude = lon
        self.altitude = alt
    
    @Slot(float)
    def updateHeading(self, heading):
        """Aktualisiert die Ausrichtung der Drohne."""
        self.heading = heading
    
    @Slot(list)
    def setWaypoints(self, waypoints):
        """Setzt die Wegpunkte auf der Karte."""
        self._waypoints = waypoints
        self.waypointsChanged.emit(self._waypoints)
    
    @Slot(str)
    def setMapStyle(self, style):
        """Setzt den Kartenstil (satellite, terrain, night)."""
        self.mapStyle = style
    
    @Slot(float)
    def setZoomLevel(self, zoom):
        """Setzt den Zoom-Level der Karte."""
        self.zoomLevel = zoom
    
    @Slot()
    def toggleMapStyle(self):
        """Wechselt zwischen den verschiedenen Kartenstilen."""
        styles = ["satellite", "terrain", "night"]
        current_index = styles.index(self._map_style)
        next_index = (current_index + 1) % len(styles)
        self.mapStyle = styles[next_index]
        return self._map_style
