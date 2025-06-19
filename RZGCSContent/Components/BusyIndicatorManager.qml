pragma Singleton
import QtQuick

Item {
    id: root
    
    // Signale für den BusyIndicator-Status
    signal showBusyRequested(string message)
    signal hideBusyRequested()
    
    // Funktion zum Anzeigen des BusyIndicators
    function showBusy(message) {
        showBusyRequested(message || "Bitte warten...")
    }
    
    // Funktion zum Ausblenden des BusyIndicators
    function hideBusy() {
        hideBusyRequested()
    }
}
