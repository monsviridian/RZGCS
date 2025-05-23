import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    
    Rectangle {
        anchors.fill: parent
        color: "#2c2c2c"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15
            
            Text {
                Layout.fillWidth: true
                text: "3D Drohnen-Animation"
                font.pixelSize: 24
                font.bold: true
                color: "white"
            }
            
            Text {
                Layout.fillWidth: true
                text: "Eine stilisierte Visualisierung, bei der sich Partikel zu einer Drohne zusammensetzen."
                font.pixelSize: 16
                color: "#cccccc"
                wrapMode: Text.WordWrap
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#555555"
                Layout.topMargin: 10
                Layout.bottomMargin: 10
            }
            
            // Hier fügen wir die AnimView ein
            AnimView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }
}
