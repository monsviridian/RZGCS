from PySide6.QtCore import QObject, Signal, Property, Slot
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "RZGCS.Backend"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class FirmwareViewModel(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._firmware_type = "ardupilot"
        self._wipe_settings = False
        self._show_developer_versions = False
        self._selected_firmware_index = -1
        self._in_progress = False
        self._progress = 0
        self._status_message = "Nicht verbunden"
        self._firmware_downloaded = False
        self._device_info = None
        self._firmware_list = []
        self._backend_firmware_manager = None
        self._is_connected = False
        self._is_initialized = False
        self._attempts = 0
        self._max_attempts = 10

    # Properties
    @Property(str)
    def firmware_type(self):
        return self._firmware_type

    @firmware_type.setter
    def firmware_type(self, value):
        if self._firmware_type != value:
            self._firmware_type = value
            self.firmware_type_changed.emit()
            self.update_firmware_list()

    @Property(bool)
    def wipe_settings(self):
        return self._wipe_settings

    @wipe_settings.setter
    def wipe_settings(self, value):
        if self._wipe_settings != value:
            self._wipe_settings = value
            self.wipe_settings_changed.emit()

    @Property(bool)
    def show_developer_versions(self):
        return self._show_developer_versions

    @show_developer_versions.setter
    def show_developer_versions(self, value):
        if self._show_developer_versions != value:
            self._show_developer_versions = value
            self.show_developer_versions_changed.emit()
            self.update_firmware_list()

    @Property(int)
    def selected_firmware_index(self):
        return self._selected_firmware_index

    @selected_firmware_index.setter
    def selected_firmware_index(self, value):
        if self._selected_firmware_index != value:
            self._selected_firmware_index = value
            self.selected_firmware_index_changed.emit()

    @Property(bool)
    def in_progress(self):
        return self._in_progress

    @Property(int)
    def progress(self):
        return self._progress

    @Property(str)
    def status_message(self):
        return self._status_message

    @Property(bool)
    def firmware_downloaded(self):
        return self._firmware_downloaded

    @Property('QVariant')
    def device_info(self):
        return self._device_info

    @Property('QVariantList')
    def firmware_list(self):
        return self._firmware_list

    # Signals
    firmware_type_changed = Signal()
    wipe_settings_changed = Signal()
    show_developer_versions_changed = Signal()
    selected_firmware_index_changed = Signal()
    in_progress_changed = Signal()
    progress_changed = Signal(int)
    status_message_changed = Signal(str)
    firmware_downloaded_changed = Signal(bool)
    device_info_changed = Signal('QVariant')
    firmware_list_changed = Signal('QVariantList')

    # Slots
    @Slot()
    def initialize(self):
        """Initialisiert das ViewModel"""
        self._attempts = 0
        self._is_initialized = False
        self._is_connected = False
        self._status_message = "Initialisiere..."
        self.status_message_changed.emit(self._status_message)
        self.update_firmware_list()

    @Slot()
    def register_with_backend(self):
        """Registriert das ViewModel beim Backend"""
        if self._backend_firmware_manager:
            # Hier würden wir die Backend-Signale verbinden
            self.update_firmware_list()

    @Slot()
    def update_firmware_list(self):
        """Aktualisiert die Firmware-Liste basierend auf dem ausgewählten Typ"""
        if self._firmware_type == "ardupilot":
            self._firmware_list = [
                {
                    "name": "ArduCopter",
                    "version": "4.4.0 (Stable)",
                    "description": "Stabile Version für Multicopter"
                },
                {
                    "name": "ArduPlane",
                    "version": "4.4.0 (Stable)",
                    "description": "Stabile Version für Flächenflugzeuge"
                },
                {
                    "name": "ArduRover",
                    "version": "4.4.0 (Stable)",
                    "description": "Stabile Version für Bodenfahrzeuge"
                },
                {
                    "name": "ArduSub",
                    "version": "4.4.0 (Stable)",
                    "description": "Stabile Version für Unterwasserfahrzeuge"
                }
            ]
            
            if self._show_developer_versions:
                self._firmware_list.extend([
                    {
                        "name": "ArduCopter",
                        "version": "4.5.0-dev (Entwicklung)",
                        "description": "Entwicklungsversion für Multicopter"
                    },
                    {
                        "name": "ArduPlane",
                        "version": "4.5.0-dev (Entwicklung)",
                        "description": "Entwicklungsversion für Flächenflugzeuge"
                    }
                ])
        elif self._firmware_type == "px4":
            self._firmware_list = [
                {
                    "name": "PX4 Standard",
                    "version": "1.14.0 (Stable)",
                    "description": "Stabile Version für alle Fahrzeugtypen"
                },
                {
                    "name": "PX4 VTOL",
                    "version": "1.14.0 (Stable)",
                    "description": "Optimiert für Senkrechtstart- und Landeflugzeuge"
                }
            ]
            
            if self._show_developer_versions:
                self._firmware_list.append({
                    "name": "PX4 Standard",
                    "version": "1.15.0-dev (Entwicklung)",
                    "description": "Entwicklungsversion"
                })

        self.firmware_list_changed.emit(self._firmware_list)

    @Slot()
    def connect_device(self):
        """Verbindet mit dem Gerät"""
        self._status_message = "Verbinde mit Gerät..."
        self.status_message_changed.emit(self._status_message)
        # Hier würde die tatsächliche Verbindungslogik implementiert 