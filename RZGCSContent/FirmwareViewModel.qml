import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RZGCS.Backend 1.0

QtObject {
    id: root
    
    // Eigenschaften für die UI-Bindung
    property string firmwareType: "ardupilot"  // "ardupilot" oder "px4"
    property bool wipeSettings: false
    property bool showDeveloperVersions: false
    property int selectedFirmwareIndex: -1
    property bool inProgress: false
    property int progress: 0
    property string statusMessage: "Nicht verbunden"
    property bool firmwareDownloaded: false
    
    // Geräteinformationen
    property var deviceInfo: null
    
    // Liste der verfügbaren Firmware-Varianten
    property var firmwareList: []
    
    // Referenz zum Backend
    property var backendFirmwareManager: null
    
    // Timer für Verbindungsversuche
    Timer {
        id: connectionTimer
        interval: 500  // 500ms zwischen Versuchen
        repeat: true
        running: !isConnected && !isInitialized && attempts < maxAttempts
        onTriggered: {
            attempts++
            console.log("FirmwareViewModel: Versuche Verbindung zum Backend... (Versuch " + attempts + ")")
            
            if (backendFirmwareManager) {
                isConnected = true
                isInitialized = true
                statusMessage = "Verbunden"
                connectionTimer.stop()
                console.log("FirmwareViewModel: Verbindung zum Backend hergestellt")
            } else if (attempts >= maxAttempts) {
                connectionTimer.stop()
                statusMessage = "Keine Verbindung zum Backend möglich"
                console.log("FirmwareViewModel: Maximale Anzahl an Verbindungsversuchen erreicht")
            }
        }
    }
    
    // Initialisierung
    Component.onCompleted: {
        console.log("FirmwareViewModel: Initialisierung")
        attempts = 0
        isInitialized = false
        isConnected = false
        statusMessage = "Initialisiere..."
        
        // Beispielhafte Firmware-Listen für die Vorschau
        // Diese werden später durch reale Daten vom Backend ersetzt
        updateFirmwareList()
    }
    
    // Registrierung beim Backend
    function registerWithBackend() {
        if (backendFirmwareManager) {
            // Registriere Callbacks für Backend-Signale
            backendFirmwareManager.progressChanged.connect(function(value) {
                progress = value
            })
            
            backendFirmwareManager.statusChanged.connect(function(message) {
                statusMessage = message
            })
            
            backendFirmwareManager.operationStarted.connect(function() {
                inProgress = true
            })
            
            backendFirmwareManager.operationFinished.connect(function(success) {
                inProgress = false
                if (success) {
                    statusMessage = "Operation erfolgreich abgeschlossen."
                } else {
                    statusMessage = "Operation fehlgeschlagen."
                }
            })
            
            backendFirmwareManager.firmwareDownloaded.connect(function(success) {
                firmwareDownloaded = success
                if (success) {
                    statusMessage = "Firmware erfolgreich heruntergeladen. Bereit zur Installation."
                } else {
                    statusMessage = "Firmware-Download fehlgeschlagen."
                }
            })
            
            backendFirmwareManager.deviceDetected.connect(function(info) {
                deviceInfo = info
            })
            
            // Registriere dieses ViewModel beim Backend
            backendFirmwareManager.registerViewModel(root)
            
            // Lade die anfängliche Firmware-Liste
            updateFirmwareList()
        }
    }
    
    // Aktualisiere die Firmware-Liste basierend auf dem ausgewählten Typ
    function updateFirmwareList() {
        if (firmwareType === "ardupilot") {
            // Beispielhafte ArduPilot-Firmwares
            firmwareList = [
                {
                    name: "ArduCopter",
                    version: "4.4.0 (Stable)",
                    description: "Stabile Version für Multicopter"
                },
                {
                    name: "ArduPlane",
                    version: "4.4.0 (Stable)",
                    description: "Stabile Version für Flächenflugzeuge"
                },
                {
                    name: "ArduRover",
                    version: "4.4.0 (Stable)",
                    description: "Stabile Version für Bodenfahrzeuge"
                },
                {
                    name: "ArduSub",
                    version: "4.4.0 (Stable)",
                    description: "Stabile Version für Unterwasserfahrzeuge"
                }
            ]
            
            if (showDeveloperVersions) {
                firmwareList.push(
                    {
                        name: "ArduCopter",
                        version: "4.5.0-dev (Entwicklung)",
                        description: "Entwicklungsversion für Multicopter"
                    },
                    {
                        name: "ArduPlane",
                        version: "4.5.0-dev (Entwicklung)",
                        description: "Entwicklungsversion für Flächenflugzeuge"
                    }
                )
            }
        } else if (firmwareType === "px4") {
            // Beispielhafte PX4-Firmwares
            firmwareList = [
                {
                    name: "PX4 Standard",
                    version: "1.14.0 (Stable)",
                    description: "Stabile Version für alle Fahrzeugtypen"
                },
                {
                    name: "PX4 VTOL",
                    version: "1.14.0 (Stable)",
                    description: "Optimiert für Senkrechtstart- und Landeflugzeuge"
                }
            ]
            
            if (showDeveloperVersions) {
                firmwareList.push(
                    {
                        name: "PX4 Standard",
                        version: "1.15.0-dev (Entwicklung)",
                        description: "Entwicklungsversion"
                    }
                )
            }
        }
        
        // Wenn es ein Backend gibt, rufe die realen Daten ab
        if (backendFirmwareManager) {
            var realFirmwareList = backendFirmwareManager.getFirmwareList(firmwareType, showDeveloperVersions)
            if (realFirmwareList && realFirmwareList.length > 0) {
                firmwareList = realFirmwareList
            }
        }
    }
    
    // Beobachte Änderungen an firmwareType und showDeveloperVersions
    onFirmwareTypeChanged: {
        updateFirmwareList()
        selectedFirmwareIndex = -1
        firmwareDownloaded = false
    }
    
    onShowDeveloperVersionsChanged: {
        updateFirmwareList()
    }
    
    // Verbindung zum Gerät herstellen
    function connectDevice() {
        statusMessage = "Verbinde mit Gerät..."
        // Hier würde die tatsächliche Verbindungslogik implementiert
    }
    
    // Firmware herunterladen
    function downloadFirmware() {
        if (selectedFirmwareIndex < 0 || selectedFirmwareIndex >= firmwareList.length) {
            statusMessage = "Bitte wählen Sie zuerst eine Firmware aus."
            return
        }
        
        var selectedFirmware = firmwareList[selectedFirmwareIndex]
        statusMessage = "Lade " + selectedFirmware.name + " " + selectedFirmware.version + " herunter..."
        progress = 0
        inProgress = true
        
        if (backendFirmwareManager) {
            backendFirmwareManager.downloadFirmware(selectedFirmwareIndex)
        } else {
            // Simuliere Download für die Vorschau
            var downloadTimer = Qt.createQmlObject(
                'import QtQuick; Timer { interval: 100; repeat: true; running: true }',
                root
            )
            
            downloadTimer.triggered.connect(function() {
                progress += 1
                if (progress >= 100) {
                    downloadTimer.stop()
                    inProgress = false
                    firmwareDownloaded = true
                    statusMessage = "Firmware erfolgreich heruntergeladen. Bereit zur Installation."
                    downloadTimer.destroy()
                }
            })
            
            downloadTimer.start()
        }
    }
    
    // Firmware flashen
    function flashFirmware() {
        if (!firmwareDownloaded) {
            statusMessage = "Bitte laden Sie zuerst die Firmware herunter."
            return
        }
        
        statusMessage = "Installiere Firmware..."
        progress = 0
        inProgress = true
        
        if (backendFirmwareManager) {
            backendFirmwareManager.flashFirmware(wipeSettings)
        } else {
            // Simuliere Installation für die Vorschau
            var flashTimer = Qt.createQmlObject(
                'import QtQuick; Timer { interval: 150; repeat: true; running: true }',
                root
            )
            
            flashTimer.triggered.connect(function() {
                progress += 1
                if (progress >= 100) {
                    flashTimer.stop()
                    inProgress = false
                    statusMessage = "Firmware erfolgreich installiert. Bitte starten Sie das Gerät neu."
                    flashTimer.destroy()
                }
            })
            
            flashTimer.start()
        }
    }
    
    // Operation abbrechen
    function cancelOperation() {
        if (backendFirmwareManager) {
            backendFirmwareManager.cancelOperation()
        }
        
        inProgress = false
        statusMessage = "Operation abgebrochen."
    }

    // Funktionen
    function initialize() {
        if (!isInitialized) {
            attempts = 0
            isConnected = false
            statusMessage = "Initialisiere..."
            connectionTimer.start()
        }
    }

    function reset() {
        isInitialized = false
        isConnected = false
        attempts = 0
        statusMessage = "Nicht verbunden"
    }
}
