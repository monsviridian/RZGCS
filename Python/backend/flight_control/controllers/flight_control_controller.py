"""Flugsteuerungs-Controller.

Dieser Controller stellt die Verbindung zwischen dem Flugsteuerungs-ViewModel und der View her.
Er initialisiert die Komponenten und verbindet sie miteinander.
"""

from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from ..viewmodels.flight_control_viewmodel import FlightControlViewModel
from ..services.flight_control_service import FlightControlService

# QmlElement und QmlSingleton temporär deaktiviert, da QML_IMPORT_NAME fehlt
# @QmlElement
# @QmlSingleton
class FlightControlController(QObject):
    """Flugsteuerungs-Controller.
    
    Dieser Controller stellt die Verbindung zwischen dem Flugsteuerungs-ViewModel und der View her.
    
    Attributes:
        _view_model: Flugsteuerungs-ViewModel
        _service: Flugsteuerungs-Service
    """
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._view_model = None
        self._service = None
    
    @Slot(result=object)
    def get_view_model(self) -> FlightControlViewModel:
        """ViewModel zurückgeben.
        
        Returns:
            Das Flugsteuerungs-ViewModel
        """
        if not self._view_model:
            self._initialize()
        return self._view_model
    
    def _initialize(self):
        """Komponenten initialisieren."""
        # Service erstellen
        self._service = FlightControlService()
        
        # ViewModel erstellen und Service setzen
        self._view_model = FlightControlViewModel()
        self._view_model.set_service(self._service) 