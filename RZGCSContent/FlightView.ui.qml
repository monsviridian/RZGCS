/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtLocation
import QtPositioning
import QtQuick3D 6.8

Rectangle {
    id: flightView
    color: "#1d1d1d"
    clip: true

    // Initialize map plugin
    Plugin {
        id: mapPlugin
        name: "osm"
        PluginParameter {
            name: "osm.mapping.custom.host"
            value: "https://tile.openstreetmap.org/"
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Math.max(5, parent.width * 0.005)
        spacing: Math.max(5, parent.height * 0.005)

        // Header
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(25, parent.height * 0.03)
            spacing: Math.max(5, parent.width * 0.005)

            Label {
                text: "Flugkarte"
                font.pixelSize: Math.max(10, parent.height * 0.015)
                color: "white"
            }

            Item { Layout.fillWidth: true }
        }

        // Map view
        Map {
            id: map
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: parent.height * 0.7
            plugin: mapPlugin
            center: QtPositioning.coordinate(51.1657, 10.4515)
            zoomLevel: 14

            // Add drone position marker
            MapQuickItem {
                id: droneMarker
                coordinate: QtPositioning.coordinate(51.1657, 10.4515)
                anchorPoint.x: image.width / 2
                anchorPoint.y: image.height / 2
                sourceItem: Image {
                    id: image
                    source: "qrc:/images/drone_marker.png"
                    width: 32
                    height: 32
                }
            }
        }

        // Control Panel
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(100, parent.height * 0.25)
            color: "#2d2d2d"
            radius: 4

            GridLayout {
                anchors.fill: parent
                anchors.margins: Math.max(5, parent.height * 0.05)
                columns: 4
                rowSpacing: Math.max(5, parent.height * 0.05)
                columnSpacing: Math.max(5, parent.width * 0.01)

                // Left side controls
                Button {
                    text: "Prearm"
                    Layout.preferredHeight: Math.max(30, parent.height * 0.3)
                    font.pixelSize: Math.max(10, parent.height * 0.15)
                }

                Button {
                    text: "Set Position"
                    Layout.preferredHeight: Math.max(30, parent.height * 0.3)
                    font.pixelSize: Math.max(10, parent.height * 0.15)
                }

                // Center controls
                TextField {
                    placeholderText: "Send Mission Plan"
                    Layout.preferredHeight: Math.max(30, parent.height * 0.3)
                    font.pixelSize: Math.max(10, parent.height * 0.15)
                    Layout.columnSpan: 2
                }

                // Right side controls
                Button {
                    text: "Reset"
                    Layout.preferredHeight: Math.max(30, parent.height * 0.3)
                    font.pixelSize: Math.max(10, parent.height * 0.15)
                }

                ComboBox {
                    Layout.preferredHeight: Math.max(30, parent.height * 0.3)
                    font.pixelSize: Math.max(10, parent.height * 0.15)
                    Layout.columnSpan: 2
                }

                // Bottom row
                Switch {
                    text: "Arm"
                    Layout.preferredHeight: Math.max(30, parent.height * 0.3)
                    font.pixelSize: Math.max(10, parent.height * 0.15)
                }

                Switch {
                    text: "Disarm"
                    Layout.preferredHeight: Math.max(30, parent.height * 0.3)
                    font.pixelSize: Math.max(10, parent.height * 0.15)
                }

                Slider {
                    Layout.preferredHeight: Math.max(30, parent.height * 0.3)
                    Layout.columnSpan: 2
                }
            }
        }
    }

    Rectangle {
        id: mapcommandrect
        y: 708
        height: 186
        color: "black"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: 0
        anchors.rightMargin: 642
        anchors.bottomMargin: 186

        Button {
            id: armbutton
            x: 286
            y: 8
            width: 183
            height: 76
            text: qsTr("Set Position")
        }

        DelayButton {
            id: prearm
            x: 107
            y: 25
            width: 113
            height: 37
            text: qsTr("Prearm")
        }

        Switch {
            id: armswitch
            x: 95
            y: 68
            width: 175
            height: 85
            text: qsTr("Arm")
        }

        Switch {
            id: disarmswitch
            x: 839
            y: 78
            width: 193
            height: 66
            text: qsTr("Disarm")
        }

        Slider {
            id: slider
            x: 570
            y: 63
            value: 0

        }

        TextField {
            id: textField
            x: 595
            y: 25
            width: 162
            height: 32
            placeholderText: qsTr("Send Mission Plan")
        }

        Button {
            id: button
            x: 801
            y: 18
            width: 197
            height: 66
            text: qsTr("Reset")
        }

        ComboBox {
            id: comboBox
            x: 1060
            y: 18
            width: 215
            height: 97

        }

        Control {
            id: control
            x: 948
            y: 41
            width: 76
            height: 86
        }
    }

    Item {
        id: __materialLibrary__
    }
}
