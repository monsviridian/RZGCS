"""
Globale Test-Konfiguration und Fixtures für die RZ Ground Control Station-Tests.
"""
import os
import sys
import pytest
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

# Stellt sicher, dass die Python-Module gefunden werden
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Globale Test-Fixtures
@pytest.fixture(scope="session")
def app():
    """Fixture für die QApplication, die für alle Qt-Tests benötigt wird."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Aufräumen am Ende der Testsitzung
    QTimer.singleShot(0, app.quit)

@pytest.fixture
def qml_engine(app):
    """Fixture für die QML-Engine, die für UI-Tests benötigt wird."""
    engine = QQmlApplicationEngine()
    yield engine
    # Aufräumen nach jedem Test
    engine.clearComponentCache()
    
@pytest.fixture
def mock_serial_port():
    """Mockt einen seriellen Port für Tests ohne echte Hardware."""
    class MockSerialPort:
        def __init__(self):
            self.is_open = False
            self.data_to_read = bytearray()
            self.written_data = bytearray()
            
        def open(self):
            self.is_open = True
            return True
            
        def close(self):
            self.is_open = False
            
        def write(self, data):
            self.written_data.extend(data)
            return len(data)
            
        def read(self, size=1):
            if not self.data_to_read:
                return bytearray()
            result = self.data_to_read[:size]
            self.data_to_read = self.data_to_read[size:]
            return result
            
        def inWaiting(self):
            return len(self.data_to_read)
            
        def add_data(self, data):
            """Hilfsmethode zum Hinzufügen von Mock-Daten zum Lesen."""
            if isinstance(data, str):
                data = data.encode('utf-8')
            self.data_to_read.extend(data)
    
    return MockSerialPort()

@pytest.fixture
def mock_mavlink_message_factory():
    """Mockt eine MAVLink-Nachrichtenfabrik für Tests ohne echte MAVLink-Kommunikation."""
    class MockMAVLinkMessage:
        def __init__(self, message_type, **kwargs):
            self.message_type = message_type
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class MockMAVLinkMessageFactory:
        def __init__(self):
            self.messages = []
            
        def heartbeat_message(self, system_status=0):
            msg = MockMAVLinkMessage('HEARTBEAT', system_status=system_status)
            self.messages.append(msg)
            return msg
            
        def attitude_message(self, roll=0, pitch=0, yaw=0):
            msg = MockMAVLinkMessage('ATTITUDE', roll=roll, pitch=pitch, yaw=yaw)
            self.messages.append(msg)
            return msg
            
        def gps_raw_int_message(self, fix_type=0, lat=0, lon=0, alt=0):
            msg = MockMAVLinkMessage('GPS_RAW_INT', fix_type=fix_type, lat=lat, lon=lon, alt=alt)
            self.messages.append(msg)
            return msg
    
    return MockMAVLinkMessageFactory()
