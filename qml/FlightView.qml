import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: flightView
    color: "#1d1d1d"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Flight data
        GroupBox {
            title: "Flight Data"
            Layout.fillWidth: true

            GridLayout {
                columns: 2
                anchors.fill: parent

                Label { text: "Altitude:" }
                Label {
                    text: "0.0 m"
                    color: "#BDBDBD"
                }

                Label { text: "Speed:" }
                Label {
                    text: "0.0 m/s"
                    color: "#BDBDBD"
                }

                Label { text: "Heading:" }
                Label {
                    text: "0°"
                    color: "#BDBDBD"
                }

                Label { text: "Battery:" }
                Label {
                    text: "100%"
                    color: "#4CAF50"
                }
            }
        }

        // Flight controls
        GroupBox {
            title: "Flight Controls"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                // Flight mode selection
                ComboBox {
                    id: flightModeComboBox
                    Layout.fillWidth: true
                    model: ["Stabilize", "AltHold", "Loiter", "RTL", "Auto"]
                }

                // Action buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Button {
                        text: "Arm"
                        onClicked: {
                            // Arm the drone
                        }
                    }

                    Button {
                        text: "Disarm"
                        onClicked: {
                            // Disarm the drone
                        }
                    }

                    Button {
                        text: "Take Off"
                        onClicked: {
                            // Take off
                        }
                    }

                    Button {
                        text: "Land"
                        onClicked: {
                            // Land the drone
                        }
                    }
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
                    ListElement { message: "System ready" }
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