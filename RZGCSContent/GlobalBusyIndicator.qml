import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Diese Komponente wurde direkt in die Anwendung eingebettet, um Importprobleme zu vermeiden
Item {
    id: root
    anchors.fill: parent
    
    // Expose public API
    function show(message) {
        busyMessage = message || "Bitte warten..."
        busyActive = true
    }
    
    function hide() {
        busyActive = false
    }
    
    // Private properties
    property bool busyActive: false
    property string busyMessage: "Bitte warten..."
    
    // Actual implementation - darkened background with centered busy indicator
    Rectangle {
        id: background
        anchors.fill: parent
        color: "#80000000" // Halbdurchsichtiger schwarzer Hintergrund
        visible: root.busyActive
        z: 999999 // Extrem hoher z-Index, über ALLEM anderen
        
        // Animation für sanftes Ein- und Ausblenden
        opacity: root.busyActive ? 0.9 : 0.0
        Behavior on opacity {
            NumberAnimation { duration: 200 }
        }
        
        // Der eigentliche Indikator
        Rectangle {
            width: content.width + 40
            height: content.height + 40
            radius: 10
            color: "#222222"
            border.color: "#444444"
            border.width: 2
            anchors.centerIn: parent
            
            ColumnLayout {
                id: content
                anchors.centerIn: parent
                spacing: 15
                
                BusyIndicator {
                    Layout.alignment: Qt.AlignHCenter
                    running: root.busyActive
                    scale: 1.5
                }
                
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: root.busyMessage
                    color: "white"
                    font.pixelSize: 14
                }
            }
        }
    }
}
