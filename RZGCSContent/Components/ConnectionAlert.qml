import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../Utils"

Rectangle {
    id: root
    
    // Properties
    property bool isConnected: false
    property real packetLossRate: 0.0
    property real heartbeatFrequency: 0.0
    property string customStatusText: ""
    
    // Status-Berechnung
    readonly property color okColor: DroneTheme.successColor
    readonly property color warnColor: DroneTheme.warningColor
    readonly property color errorColor: DroneTheme.errorColor
    
    property int statusLevel: (!isConnected) ? 2 : 
                             (packetLossRate > 10) ? 1 : 
                             (heartbeatFrequency < 0.5) ? 1 : 0
    
    // Styling
    width: 200
    height: 50
    radius: DroneTheme.radiusSmall
    border.width: 2
    border.color: (statusLevel === 2) ? errorColor : 
                  (statusLevel === 1) ? warnColor : okColor
    color: Qt.rgba(0, 0, 0, 0.5)
    
    // Pulsing-Animation bei kritischem Status
    SequentialAnimation on scale {
        running: statusLevel === 2
        loops: Animation.Infinite
        NumberAnimation { 
            to: 1.1; 
            duration: 500;
            easing.type: Easing.InOutQuad
        }
        NumberAnimation { 
            to: 1.0; 
            duration: 500;
            easing.type: Easing.InOutQuad
        }
    }
    
    // Layout
    RowLayout {
        anchors.fill: parent
        anchors.margins: DroneTheme.spacingDefault
        spacing: DroneTheme.spacingDefault
        
        // Status-LED
        Rectangle {
            id: statusLed
            width: 16
            height: 16
            radius: 8
            color: statusLevel === 2 ? errorColor 
                   : statusLevel === 1 ? warnColor 
                   : okColor
            
            // Blinken bei kritischem Status
            Timer {
                interval: statusLevel === 2 ? 600 : 0
                running: statusLevel === 2
                repeat: true
                onTriggered: statusLed.opacity = statusLed.opacity === 1 ? 0.3 : 1
            }
            
            // Smooth transition für Status-Änderungen
            Behavior on color {
                ColorAnimation { duration: DroneTheme.animationDurationDefault }
            }
        }
        
        // Status-Text
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            
            Text {
                id: statusText
                text: customStatusText !== "" ? customStatusText : 
                      (root.statusLevel === 2) ? "KEINE VERBINDUNG" :
                      (root.statusLevel === 1) ? "SCHWACHE VERBINDUNG" : "VERBUNDEN"
                color: statusLevel === 2 ? errorColor 
                       : statusLevel === 1 ? warnColor 
                       : okColor
                font.pixelSize: DroneTheme.fontSizeMedium
                font.bold: true
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignLeft
            }
            
            Text {
                id: detailsText
                text: (statusLevel === 0) ? "Stabile Verbindung" :
                      (statusLevel === 1) ? "Paketverlust: " + packetLossRate.toFixed(1) + "%" :
                      "Verbindung getrennt"
                color: DroneTheme.textSecondaryColor
                font.pixelSize: DroneTheme.fontSizeSmall
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignLeft
                visible: statusLevel !== 0
            }
        }
    }
    
    // Öffentliche API
    function setStatus(connected, packetLoss, heartbeat) {
        isConnected = connected
        packetLossRate = packetLoss || 0
        heartbeatFrequency = heartbeat || 0
    }
    
    function setCustomStatus(text) {
        customStatusText = text
    }
    
    function getStatusLevel() {
        return statusLevel
    }
    
    function isCritical() {
        return statusLevel === 2
    }
    
    function isWarning() {
        return statusLevel === 1
    }
    
    function isOk() {
        return statusLevel === 0
    }
} 