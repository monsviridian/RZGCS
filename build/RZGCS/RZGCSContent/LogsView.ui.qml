import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: logsView
    color: "#1d1d1d"
    clip: true

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Math.max(10, parent.width * 0.01)
        spacing: Math.max(10, parent.height * 0.01)

        // Header
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(40, parent.height * 0.05)
            spacing: Math.max(10, parent.width * 0.01)

            Label {
                text: "Logs"
                font.pixelSize: Math.max(20, parent.height * 0.03)
                color: "white"
            }

            Item { Layout.fillWidth: true }

            Button {
                Layout.preferredHeight: Math.max(30, parent.height * 0.04)
                font.pixelSize: Math.max(12, parent.height * 0.02)
                text: "Logs löschen"
                onClicked: {
                    if (logger) {
                        logger.clear()
                    }
                }
            }
        }

        // Log list with proper scaling
        ListView {
            id: logsList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Math.max(2, parent.height * 0.003)
            model: logger ? logger.logs : []

            // Background with proper scaling
            Rectangle {
                color: "#2d2d2d"
                anchors.fill: parent
                z: -1
            }

            delegate: LogsListDelegate {
                width: logsList.width
                height: Math.max(30, parent.height * 0.04)
            }

            ScrollBar.vertical: ScrollBar {
                active: true
                policy: ScrollBar.AsNeeded
                width: Math.max(10, parent.width * 0.01)
            }

            // Auto-scroll to bottom
            Connections {
                target: logger
                function onLogsChanged() {
                    logsList.positionViewAtEnd()
                }
            }
        }
    }
} 