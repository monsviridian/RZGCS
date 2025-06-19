"""
Enumerationen für das Telemetrie-System.
Definiert die verschiedenen Status und Datentypen.
"""

from enum import Enum

class TelemetryStatus(Enum):
    """Status des Telemetrie-Systems"""
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    ERROR = "ERROR"

class TelemetryDataType(Enum):
    """Typen von Telemetrie-Daten"""
    # Flugzeug-Position
    LATITUDE = "LATITUDE"
    LONGITUDE = "LONGITUDE"
    ALTITUDE = "ALTITUDE"
    HEADING = "HEADING"
    
    # Flugzeug-Bewegung
    SPEED = "SPEED"
    VERTICAL_SPEED = "VERTICAL_SPEED"
    GROUND_SPEED = "GROUND_SPEED"
    AIR_SPEED = "AIR_SPEED"
    
    # Flugzeug-Orientierung
    ROLL = "ROLL"
    PITCH = "PITCH"
    YAW = "YAW"
    
    # Flugzeug-System
    BATTERY_LEVEL = "BATTERY_LEVEL"
    BATTERY_VOLTAGE = "BATTERY_VOLTAGE"
    BATTERY_CURRENT = "BATTERY_CURRENT"
    SIGNAL_STRENGTH = "SIGNAL_STRENGTH"
    
    # Flugzeug-Modus
    FLIGHT_MODE = "FLIGHT_MODE"
    ARM_STATE = "ARM_STATE"
    
    # Sensoren
    GPS_FIX = "GPS_FIX"
    GPS_SATELLITES = "GPS_SATELLITES"
    GPS_HDOP = "GPS_HDOP"
    
    # Wetter
    TEMPERATURE = "TEMPERATURE"
    PRESSURE = "PRESSURE"
    HUMIDITY = "HUMIDITY"
    WIND_SPEED = "WIND_SPEED"
    WIND_DIRECTION = "WIND_DIRECTION"

class TelemetryUnit(Enum):
    """Einheiten für Telemetrie-Daten"""
    # Längen
    METERS = "m"
    KILOMETERS = "km"
    FEET = "ft"
    
    # Geschwindigkeiten
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    KNOTS = "kt"
    
    # Winkel
    DEGREES = "°"
    RADIANS = "rad"
    
    # Elektrische Einheiten
    VOLTS = "V"
    AMPERES = "A"
    WATTS = "W"
    
    # Andere
    PERCENT = "%"
    CELSIUS = "°C"
    HECTOPASCAL = "hPa"
    DB = "dB" 