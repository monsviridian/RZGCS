
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

Window {
    id: window
    visible: true
    title: "QML Style Test"
    width: 400
    height: 300
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        
        Label {
            text: "Testing Material Style"
            font.pixelSize: 20
            Layout.fillWidth: true
        }
        
        Button {
            text: "Test Button"
            Layout.fillWidth: true
            contentItem: Text {
                text: parent.text
                font.pixelSize: 16
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}
