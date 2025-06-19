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

        // Checkliste
        GroupBox {
            title: "Preflight Checklist"
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 5

                // Batterie
                CheckBox {
                    text: "Battery fully charged"
                    checked: false
                }

                // Propeller
                CheckBox {
                    text: "Propellers securely attached"
                    checked: false
                }

                // GPS
                CheckBox {
                    text: "GPS signal acquired"
                    checked: false
                }

                // IMU
                CheckBox {
                    text: "IMU calibrated"
                    checked: false
                }

                // RC
                CheckBox {
                    text: "RC transmitter connected"
                    checked: false
                }

                // Flight Mode
                CheckBox {
                    text: "Flight mode set to STABILIZE"
                    checked: false
                }

                // Failsafe
                CheckBox {
                    text: "Failsafe configured"
                    checked: false
                }

                // Geofence
                CheckBox {
                    text: "Geofence configured"
                    checked: false
                }

                // Mission
                CheckBox {
                    text: "Mission uploaded (if applicable)"
                    checked: false
                }

                // Weather
                CheckBox {
                    text: "Weather conditions suitable"
                    checked: false
                }

                // Area
                CheckBox {
                    text: "Flight area clear"
                    checked: false
                }

                // Emergency
                CheckBox {
                    text: "Emergency procedures reviewed"
                    checked: false
                }
            }
        }

        // Status
        GroupBox {
            title: "System Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                Label { text: "Battery Voltage:" }
                Label { text: "0.0V" }

                Label { text: "GPS Satellites:" }
                Label { text: "0" }

                Label { text: "GPS Fix:" }
                Label { text: "No Fix" }

                Label { text: "IMU Status:" }
                Label { text: "Not Ready" }

                Label { text: "RC Status:" }
                Label { text: "Not Connected" }

                Label { text: "Flight Mode:" }
                Label { text: "Unknown" }
            }
        }

        // Aktionen
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "Run Preflight Checks"
                Layout.fillWidth: true
                onClicked: {
                    // TODO: Implement preflight checks
                }
            }

            Button {
                text: "Clear Checklist"
                Layout.fillWidth: true
                onClicked: {
                    // TODO: Clear all checkboxes
                }
            }
        }
    }
} 