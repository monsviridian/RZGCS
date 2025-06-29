import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Window {
    id: testWindow
    width: 400
    height: 300
    visible: true
    title: "RZGCS Test UI"
    
    Rectangle {
        anchors.fill: parent
        color: "darkgray"
        
        Column {
            anchors.centerIn: parent
            spacing: 10
            
            Text {
                text: "RZGCS Test UI"
                color: "white"
                font.pixelSize: 24
            }
            
            Button {
                text: "Test Button"
                onClicked: {
                    statusText.text = "Button wurde geklickt!"
                    if (typeof serialConnector !== "undefined") {
                        statusText.text += " SerialConnector verfügbar."
                    }
                }
            }
            
            Text {
                id: statusText
                text: "Status: Bereit"
                color: "white"
            }
        }
    }
}
