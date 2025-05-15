import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: preflightView
    color: "#1d1d1d"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Preflight checklist
        GroupBox {
            title: "Preflight Checklist"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                CheckBox {
                    text: "Battery fully charged"
                    checked: false
                }

                CheckBox {
                    text: "Propellers installed correctly"
                    checked: false
                }

                CheckBox {
                    text: "GPS signal available"
                    checked: false
                }

                CheckBox {
                    text: "Radio control calibrated"
                    checked: false
                }

                CheckBox {
                    text: "Flight mode set correctly"
                    checked: false
                }

                CheckBox {
                    text: "Weather conditions suitable"
                    checked: false
                }
            }
        }

        // System status
        GroupBox {
            title: "System Status"
            Layout.fillWidth: true

            GridLayout {
                columns: 2
                anchors.fill: parent

                Label { text: "Battery:" }
                Label {
                    text: "100%"
                    color: "#4CAF50"
                }

                Label { text: "GPS:" }
                Label {
                    text: "3D Fix"
                    color: "#4CAF50"
                }

                Label { text: "Radio:" }
                Label {
                    text: "Connected"
                    color: "#4CAF50"
                }

                Label { text: "Flight Mode:" }
                Label {
                    text: "Stabilize"
                    color: "#BDBDBD"
                }
            }
        }

        // Action buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "Start Preflight Check"
                onClicked: {
                    // Start preflight check
                }
            }

            Button {
                text: "Reset Checklist"
                onClicked: {
                    // Reset checklist
                }
            }
        }

        // Status messages
        GroupBox {
            title: "Status Messages"
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: statusListView
                anchors.fill: parent
                model: ListModel {
                    ListElement { message: "System ready for preflight check" }
                    ListElement { message: "Waiting for GPS signal" }
                    ListElement { message: "Radio control connected" }
                }
                delegate: Text {
                    text: model.message
                    color: "#BDBDBD"
                    wrapMode: Text.WordWrap
                }
                ScrollBar.vertical: ScrollBar {}
            }
        }
    }
} 