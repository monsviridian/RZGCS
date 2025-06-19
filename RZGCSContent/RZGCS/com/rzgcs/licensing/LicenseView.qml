import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#2C2C2C"
    radius: 5
    border.color: "gray"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Label {
            text: "License Management"
            color: "white"
            font.pixelSize: 20
            font.bold: true
        }

        // License Status
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: "#404040"
            radius: 5

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Label {
                    text: "Status:"
                    color: "white"
                }

                Label {
                    text: "Valid"
                    color: "#00FF00"
                }
            }
        }

        // License Actions
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "Activate License"
                Layout.fillWidth: true
            }

            Button {
                text: "Deactivate License"
                Layout.fillWidth: true
            }
        }
    }
} 