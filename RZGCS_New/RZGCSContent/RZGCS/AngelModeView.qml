import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#303030"
    border.color: "#404040"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Angel Mode Status
        GroupBox {
            title: "Angel Mode Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                Label { text: "Status:" }
                Label { text: "Inactive" }

                Label { text: "Current Altitude:" }
                Label { text: "0.0 m" }

                Label { text: "Target Altitude:" }
                Label { text: "0.0 m" }

                Label { text: "Vertical Speed:" }
                Label { text: "0.0 m/s" }
            }
        }

        // Angel Mode Steuerung
        GroupBox {
            title: "Angel Mode Control"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                // Höhensteuerung
                GroupBox {
                    title: "Altitude Control"
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        Label {
                            text: "Target Altitude"
                            Layout.fillWidth: true
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            Slider {
                                id: altitudeSlider
                                Layout.fillWidth: true
                                from: 0
                                to: 100
                                value: 0
                                enabled: false
                            }

                            Label {
                                text: altitudeSlider.value.toFixed(1) + " m"
                                Layout.preferredWidth: 60
                            }
                        }

                        Button {
                            text: "Set Altitude"
                            Layout.fillWidth: true
                            enabled: false
                            onClicked: {
                                // TODO: Set target altitude
                            }
                        }
                    }
                }

                // Geschwindigkeitssteuerung
                GroupBox {
                    title: "Speed Control"
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        Label {
                            text: "Vertical Speed"
                            Layout.fillWidth: true
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            Slider {
                                id: speedSlider
                                Layout.fillWidth: true
                                from: -5
                                to: 5
                                value: 0
                                enabled: false
                            }

                            Label {
                                text: speedSlider.value.toFixed(1) + " m/s"
                                Layout.preferredWidth: 60
                            }
                        }

                        Button {
                            text: "Set Speed"
                            Layout.fillWidth: true
                            enabled: false
                            onClicked: {
                                // TODO: Set vertical speed
                            }
                        }
                    }
                }
            }
        }

        // Angel Mode Aktionen
        GroupBox {
            title: "Angel Mode Actions"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 10

                Button {
                    text: "Enable Angel Mode"
                    Layout.fillWidth: true
                    enabled: false
                    onClicked: {
                        // TODO: Enable angel mode
                    }
                }

                Button {
                    text: "Disable Angel Mode"
                    Layout.fillWidth: true
                    enabled: false
                    onClicked: {
                        // TODO: Disable angel mode
                    }
                }

                Button {
                    text: "Hover"
                    Layout.fillWidth: true
                    enabled: false
                    onClicked: {
                        // TODO: Hover at current altitude
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
            }
        }

        // Sicherheits-Einstellungen
        GroupBox {
            title: "Safety Settings"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 5

                CheckBox {
                    text: "Enable Altitude Hold"
                    checked: true
                    enabled: false
                }

                CheckBox {
                    text: "Enable Speed Limit"
                    checked: true
                    enabled: false
                }

                CheckBox {
                    text: "Enable Geofence"
                    checked: true
                    enabled: false
                }

                CheckBox {
                    text: "Enable Low Battery Protection"
                    checked: true
                    enabled: false
                }
            }
        }
    }
} 