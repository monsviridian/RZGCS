import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#303030"
    border.color: "#404040"
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Linke Seite
        ColumnLayout {
            Layout.fillHeight: true
            Layout.preferredWidth: 300
            spacing: 10

            // Telemetrie-Panel
            TelemetryPanel {
                id: telemetryPanel
                Layout.fillWidth: true
                Layout.preferredHeight: 200
            }

            // Künstlicher Horizont
            ArtificialHorizon {
                id: artificialHorizon
                Layout.fillWidth: true
                Layout.preferredHeight: 200
            }

            // Missions-Info
            MissionInfoDisplay {
                id: missionInfoDisplay
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        // Rechte Seite
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            // Flugmodus
            GroupBox {
                title: "Flight Mode"
                Layout.fillWidth: true

                RowLayout {
                    anchors.fill: parent
                    spacing: 10

                    ComboBox {
                        id: flightModeCombo
                        model: ["STABILIZE", "ALT_HOLD", "LOITER", "RTL", "AUTO", "GUIDED"]
                        Layout.fillWidth: true
                        enabled: false
                        onActivated: {
                            // TODO: Set flight mode
                        }
                    }

                    Button {
                        text: "Set Mode"
                        Layout.preferredWidth: 100
                        enabled: false
                        onClicked: {
                            // TODO: Set flight mode
                        }
                    }
                }
            }

            // Steuerung
            GroupBox {
                title: "Control"
                Layout.fillWidth: true

                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    columnSpacing: 10
                    rowSpacing: 10

                    // Arm/Disarm
                    Button {
                        text: "ARM"
                        Layout.fillWidth: true
                        enabled: false
                        onClicked: {
                            // TODO: Arm vehicle
                        }
                    }

                    Button {
                        text: "DISARM"
                        Layout.fillWidth: true
                        enabled: false
                        onClicked: {
                            // TODO: Disarm vehicle
                        }
                    }

                    // Takeoff/Land
                    Button {
                        text: "Takeoff"
                        Layout.fillWidth: true
                        enabled: false
                        onClicked: {
                            // TODO: Takeoff
                        }
                    }

                    Button {
                        text: "Land"
                        Layout.fillWidth: true
                        enabled: false
                        onClicked: {
                            // TODO: Land
                        }
                    }

                    // RTL/Auto
                    Button {
                        text: "RTL"
                        Layout.fillWidth: true
                        enabled: false
                        onClicked: {
                            // TODO: Return to launch
                        }
                    }

                    Button {
                        text: "Auto"
                        Layout.fillWidth: true
                        enabled: false
                        onClicked: {
                            // TODO: Start auto mission
                        }
                    }
                }
            }

            // Missions-Planer
            GroupBox {
                title: "Mission Planner"
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10

                    // Missions-Aktionen
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Button {
                            text: "New Mission"
                            Layout.fillWidth: true
                            enabled: false
                            onClicked: {
                                // TODO: Create new mission
                            }
                        }

                        Button {
                            text: "Load Mission"
                            Layout.fillWidth: true
                            enabled: false
                            onClicked: {
                                // TODO: Load mission
                            }
                        }

                        Button {
                            text: "Save Mission"
                            Layout.fillWidth: true
                            enabled: false
                            onClicked: {
                                // TODO: Save mission
                            }
                        }

                        Button {
                            text: "Upload Mission"
                            Layout.fillWidth: true
                            enabled: false
                            onClicked: {
                                // TODO: Upload mission
                            }
                        }
                    }

                    // Missions-Liste
                    ListView {
                        id: missionListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: ListModel {
                            // TODO: Add mission waypoints
                        }
                        delegate: ItemDelegate {
                            width: parent.width
                            text: "Waypoint " + (index + 1)
                            onClicked: {
                                // TODO: Select waypoint
                            }
                        }
                    }
                }
            }
        }
    }
} 