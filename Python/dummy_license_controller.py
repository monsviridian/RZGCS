from PySide6.QtCore import QObject, Signal, Slot, Property

class DummyLicenseController(QObject):
    """
    Dummy-Implementierung des LicenseController für UI-Testing
    """
    # Signale
    licenseAcceptedChanged = Signal()
    licenseVersionChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._license_accepted = False
        self._license_version = "1.0.0"
        print("DummyLicenseController initialisiert")
    
    @Property(bool, notify=licenseAcceptedChanged)
    def licenseAccepted(self):
        return self._license_accepted
    
    @licenseAccepted.setter
    def licenseAccepted(self, accepted):
        if self._license_accepted != accepted:
            self._license_accepted = accepted
            self.licenseAcceptedChanged.emit()
    
    @Property(str, notify=licenseVersionChanged)
    def licenseVersion(self):
        return self._license_version
    
    @Slot(str)
    def setLicenseVersion(self, version):
        if self._license_version != version:
            self._license_version = version
            self.licenseVersionChanged.emit()
    
    @Slot(bool)
    def acceptLicense(self, accepted):
        self.licenseAccepted = accepted
        print(f"Lizenz {'akzeptiert' if accepted else 'abgelehnt'}")
