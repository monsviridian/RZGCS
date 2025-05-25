from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement

from .license_manager import LicenseManager

QML_IMPORT_NAME = "com.rzgcs.licensing"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class LicenseController(QObject):
    licenseStatusChanged = Signal(bool)
    licenseTypeChanged = Signal(str)
    licenseExpiryChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._license_manager = LicenseManager()
        
        # Signale verbinden
        self._license_manager.licenseStatusChanged.connect(self.licenseStatusChanged)
        self._license_manager.licenseTypeChanged.connect(self.licenseTypeChanged)
        self._license_manager.licenseExpiryChanged.connect(self.licenseExpiryChanged)
    
    @Property(bool, notify=licenseStatusChanged)
    def isLicensed(self):
        return self._license_manager.license_valid
    
    @Property(str, notify=licenseTypeChanged)
    def licenseType(self):
        return self._license_manager.license_type
    
    @Property(str, notify=licenseExpiryChanged)
    def licenseExpiry(self):
        return self._license_manager.license_expiry
    
    @Slot(str, result=bool)
    def activateLicense(self, license_key):
        return self._license_manager.activate_license(license_key)
    
    @Slot(result=bool)
    def deactivateLicense(self):
        return self._license_manager.deactivate_license()
    
    @Slot(str, result=bool)
    def isFeatureEnabled(self, feature_name):
        return self._license_manager.is_feature_enabled(feature_name)
