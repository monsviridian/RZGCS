import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Window {
    id: testWindow
    visible: true
    width: 400
    height: 300
    title: "RZGCS Test Window"

    Rectangle {
        anchors.fill: parent
        color: "#f0f0f0"

        Column {
            anchors.centerIn: parent
            spacing: 20

            Text {
                text: "Backend-Verbindung erfolgreich!"
                font.pixelSize: 24
                color: "green"
            }

            Button {
                text: "Verbinden"
                width: 150
                height: 50
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    if (typeof connectionViewModel !== "undefined" && connectionViewModel) {
                        console.log("Versuche zu verbinden...")
                        connectionViewModel.connect("COM1:115200")
                    } else {
                        console.log("connectionViewModel nicht verfügbar")
                    }
                }
            }
        }
    }
}
