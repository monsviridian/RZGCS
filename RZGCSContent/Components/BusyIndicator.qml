import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    
    // Eigenschaften, die von außen gesetzt werden können
    property string message: "Bitte warten..."
    property bool isVisible: false
    
    // Automatisch ein- und ausblenden basierend auf isVisible
    visible: isVisible
    opacity: isVisible ? 0.9 : 0.0
    
    // Animation für sanftes Ein- und Ausblenden
    Behavior on opacity {
        NumberAnimation { duration: 300 }
    }
    
    // Styling
    color: "#222222"
    border.color: "#444444"
    border.width: 1
    radius: 10
    anchors.centerIn: parent
    width: busyContent.width + 40
    height: busyContent.height + 40
    
    // Einfacher Rahmen statt Schatten-Effekt
    border.color: "#444444"
    border.width: 2
    
    // Inhalt (Spinner + Text)
    ColumnLayout {
        id: busyContent
        anchors.centerIn: parent
        spacing: 15
        
        BusyIndicator {
            Layout.alignment: Qt.AlignHCenter
            running: root.isVisible
            scale: 1.5
        }
        
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: root.message
            color: "white"
            font.pixelSize: 14
        }
    }
}
