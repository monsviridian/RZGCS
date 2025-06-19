import QtQuick 2.15
import QtQuick.Controls 2.15

/**
 * TelemetryConnection - Verbindungskomponente zwischen Python-TelemetryViewModel und TelemetryPanel
 * Kann als Singleton oder als eingebettete Komponente verwendet werden
 */
Item {
    id: telemetryConnection
    
    // Da wir ein Item sind, können wir es unsichtbar machen
    visible: false
    width: 0
    height: 0
    
    // Ziel-TelemetryPanel, das aktualisiert werden soll
    property var targetPanel: null
    
    // Aktiv-Status der Verbindung
    property bool active: true
    
    // Verbindung zum Python-TelemetryViewModel
    Connections {
        target: telemetryViewModel
        enabled: telemetryConnection.active && telemetryConnection.targetPanel !== null
        
        // Höhe
        function onAltitudeChanged(altitude) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.altitude = altitude;
            }
        }
        
        // Geschwindigkeit
        function onGroundSpeedChanged(groundSpeed) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.groundSpeed = groundSpeed;
            }
        }
        
        function onAirSpeedChanged(airSpeed) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.airSpeed = airSpeed;
            }
        }
        
        function onVerticalSpeedChanged(verticalSpeed) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.verticalSpeed = verticalSpeed;
            }
        }
        
        // Kurs
        function onHeadingChanged(heading) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.heading = heading;
            }
        }
        
        // Batterie
        function onBatteryPercentChanged(batteryPercent) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.batteryPercent = batteryPercent;
            }
        }
        
        function onBatteryVoltageChanged(batteryVoltage) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.batteryVoltage = batteryVoltage;
            }
        }
        
        function onBatteryCurrentChanged(batteryCurrent) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.batteryCurrent = batteryCurrent;
            }
        }
        
        // Wegpunkte
        function onDistToWPChanged(distToWP) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.distToWP = distToWP;
            }
        }
        
        // Gasregler
        function onThrottlePercentChanged(throttlePercent) {
            if (telemetryConnection.targetPanel) {
                telemetryConnection.targetPanel.throttlePercent = throttlePercent;
            }
        }
    }
}
