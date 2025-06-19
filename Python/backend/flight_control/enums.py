"""
Enums für die Flugsteuerung.
Definiert die Aufzählungstypen für die Flugsteuerung.
"""

from enum import Enum, auto

class FlightStatus(Enum):
    """Flugstatus"""
    DISCONNECTED = auto()  # Nicht verbunden
    CONNECTED = auto()     # Verbunden
    ARMED = auto()        # Scharf
    DISARMED = auto()     # Entscharft
    FLYING = auto()       # Im Flug
    LANDED = auto()       # Gelandet
    ERROR = auto()        # Fehler
    TAKEOFF = auto()      # Start
    LANDING = auto()      # Landung
    RTL = auto()          # Return to Launch
    HOLD = auto()         # Position halten
    FOLLOW_PATH = auto()  # Pfad folgen
    ORBIT = auto()        # Orbit fliegen
    MANEUVER = auto()     # Manöver ausführen
    FORMATION = auto()    # Formation setzen
    EMERGENCY = auto()    # Notfall
    
class FlightMode(Enum):
    """Flugmodus"""
    MANUAL = auto()       # Manuell
    STABILIZE = auto()    # Stabilisiert
    ALT_HOLD = auto()     # Höhenhaltung
    LOITER = auto()       # Kreisen
    RTL = auto()          # Return to Launch
    AUTO = auto()         # Automatisch
    GUIDED = auto()       # Geführt
    
class ConnectionStatus(Enum):
    """Verbindungsstatus"""
    DISCONNECTED = auto() # Nicht verbunden
    CONNECTING = auto()   # Verbindungsaufbau
    CONNECTED = auto()    # Verbunden
    ERROR = auto()        # Fehler
    
class ConnectionType(Enum):
    """Verbindungstyp"""
    NONE = auto()         # Keine Verbindung
    SERIAL = auto()       # Serielle Verbindung
    UDP = auto()          # UDP-Verbindung
    TCP = auto()          # TCP-Verbindung
    
class WaypointType(Enum):
    """Wegpunkttyp"""
    WAYPOINT = auto()     # Wegpunkt
    LOITER = auto()       # Kreisen
    LAND = auto()         # Landen
    TAKEOFF = auto()      # Starten
    RTL = auto()          # Return to Launch
    
class MissionStatus(Enum):
    """Missionsstatus"""
    IDLE = auto()         # Inaktiv
    RUNNING = auto()      # Läuft
    PAUSED = auto()       # Pausiert
    COMPLETED = auto()    # Abgeschlossen
    ABORTED = auto()      # Abgebrochen
    ERROR = auto()        # Fehler

class ControlMode(Enum):
    """Steuerungsmodi"""
    BASIC = auto()         # Einfache Steuerung
    ADVANCED = auto()      # Fortgeschrittene Steuerung
    AUTONOMOUS = auto()    # Autonome Steuerung

class CommandType(Enum):
    """Befehlstypen"""
    TAKEOFF = auto()       # Start
    LAND = auto()          # Landung
    RTL = auto()           # Return to Launch
    HOLD = auto()          # Position halten
    SET_ALTITUDE = auto()  # Höhe setzen
    SET_HEADING = auto()   # Kurs setzen
    SET_SPEED = auto()     # Geschwindigkeit setzen
    FOLLOW_PATH = auto()   # Pfad folgen
    ORBIT = auto()         # Kreisbahn fliegen
    MANEUVER = auto()      # Manöver ausführen
    FORMATION = auto()     # Formation setzen
    EMERGENCY = auto()     # Notfallprozedur

class ManeuverType(Enum):
    """Manövertypen"""
    TURN = auto()          # Kurve
    CLIMB = auto()         # Steigflug
    DESCENT = auto()       # Sinkflug
    ROLL = auto()          # Rolle
    LOOP = auto()          # Looping
    IMMELMANN = auto()     # Immelmann
    SPLIT_S = auto()       # Split-S
    HAMMERHEAD = auto()    # Hammerhead
    CUBAN_EIGHT = auto()   # Cuban Eight
    CHANDELLE = auto()     # Chandelle
    LAZY_EIGHT = auto()    # Lazy Eight

class FormationType(Enum):
    """Formationstypen"""
    LINE = auto()          # Linie
    VEE = auto()           # V-Formation
    DIAMOND = auto()       # Diamant
    CIRCLE = auto()        # Kreis
    ECHELON = auto()       # Staffel
    WEDGE = auto()         # Keil
    COLUMN = auto()        # Kolonne
    STAGGERED = auto()     # Gestaffelt

class EmergencyProcedure(Enum):
    """Notfallprozeduren"""
    ABORT = auto()         # Abbruch
    EMERGENCY_LAND = auto() # Notlandung
    PARACHUTE = auto()     # Fallschirm
    FAILSAFE = auto()      # Failsafe
    SYSTEM_RESET = auto()  # System-Reset

class ValidationResult(Enum):
    """Validierungsergebnisse"""
    VALID = auto()         # Gültig
    INVALID = auto()       # Ungültig
    WARNING = auto()       # Warnung
    ERROR = auto()         # Fehler 