import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: root
    title: "Geofencing"
    width: 800
    height: 600
    visible: true

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Geofence-Konfiguration
        GroupBox {
            title: "Geofence-Konfiguration"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                // Geofence-Typ
                ComboBox {
                    id: typeComboBox
                    Layout.fillWidth: true
                    model: ["Polygon", "Circle", "Rectangle"]
                    onCurrentTextChanged: {
                        // Parameter basierend auf Typ anpassen
                        switch (currentText) {
                            case "Polygon":
                                polygonParams.visible = true
                                circleParams.visible = false
                                rectangleParams.visible = false
                                break
                            case "Circle":
                                polygonParams.visible = false
                                circleParams.visible = true
                                rectangleParams.visible = false
                                break
                            case "Rectangle":
                                polygonParams.visible = false
                                circleParams.visible = false
                                rectangleParams.visible = true
                                break
                        }
                    }
                }

                // Polygon-Parameter
                GroupBox {
                    id: polygonParams
                    title: "Polygon-Parameter"
                    Layout.fillWidth: true
                    visible: true

                    GridLayout {
                        anchors.fill: parent
                        columns: 2

                        Label { text: "Vertices:" }
                        TextArea {
                            id: verticesText
                            Layout.fillWidth: true
                            placeholderText: "Format: lat,lon;lat,lon;..."
                        }

                        Label { text: "Min. Höhe (m):" }
                        SpinBox {
                            id: minAltitudeSpin
                            from: 0
                            to: 1000
                            value: 0
                        }

                        Label { text: "Max. Höhe (m):" }
                        SpinBox {
                            id: maxAltitudeSpin
                            from: 0
                            to: 1000
                            value: 100
                        }

                        Label { text: "Buffer (m):" }
                        SpinBox {
                            id: bufferSpin
                            from: 0
                            to: 100
                            value: 10
                        }
                    }
                }

                // Kreis-Parameter
                GroupBox {
                    id: circleParams
                    title: "Kreis-Parameter"
                    Layout.fillWidth: true
                    visible: false

                    GridLayout {
                        anchors.fill: parent
                        columns: 2

                        Label { text: "Zentrum (lat,lon):" }
                        TextField {
                            id: centerText
                            Layout.fillWidth: true
                            placeholderText: "Format: lat,lon"
                        }

                        Label { text: "Radius (m):" }
                        SpinBox {
                            id: radiusSpin
                            from: 0
                            to: 10000
                            value: 100
                        }

                        Label { text: "Min. Höhe (m):" }
                        SpinBox {
                            id: circleMinAltitudeSpin
                            from: 0
                            to: 1000
                            value: 0
                        }

                        Label { text: "Max. Höhe (m):" }
                        SpinBox {
                            id: circleMaxAltitudeSpin
                            from: 0
                            to: 1000
                            value: 100
                        }

                        Label { text: "Buffer (m):" }
                        SpinBox {
                            id: circleBufferSpin
                            from: 0
                            to: 100
                            value: 10
                        }
                    }
                }

                // Rechteck-Parameter
                GroupBox {
                    id: rectangleParams
                    title: "Rechteck-Parameter"
                    Layout.fillWidth: true
                    visible: false

                    GridLayout {
                        anchors.fill: parent
                        columns: 2

                        Label { text: "Nordwest (lat,lon):" }
                        TextField {
                            id: nwText
                            Layout.fillWidth: true
                            placeholderText: "Format: lat,lon"
                        }

                        Label { text: "Südost (lat,lon):" }
                        TextField {
                            id: seText
                            Layout.fillWidth: true
                            placeholderText: "Format: lat,lon"
                        }

                        Label { text: "Min. Höhe (m):" }
                        SpinBox {
                            id: rectMinAltitudeSpin
                            from: 0
                            to: 1000
                            value: 0
                        }

                        Label { text: "Max. Höhe (m):" }
                        SpinBox {
                            id: rectMaxAltitudeSpin
                            from: 0
                            to: 1000
                            value: 100
                        }

                        Label { text: "Buffer (m):" }
                        SpinBox {
                            id: rectBufferSpin
                            from: 0
                            to: 100
                            value: 10
                        }
                    }
                }
            }
        }

        // Aktionen
        GroupBox {
            title: "Aktionen"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                // Aktions-Typ
                ComboBox {
                    id: actionComboBox
                    Layout.fillWidth: true
                    model: ["Warn", "Return", "Land"]
                }

                // Warn-Parameter
                GroupBox {
                    id: warnParams
                    title: "Warn-Parameter"
                    Layout.fillWidth: true
                    visible: actionComboBox.currentText === "Warn"

                    GridLayout {
                        anchors.fill: parent
                        columns: 2

                        Label { text: "Warnung (m):" }
                        SpinBox {
                            id: warningDistanceSpin
                            from: 0
                            to: 100
                            value: 20
                        }

                        Label { text: "Intervall (s):" }
                        SpinBox {
                            id: warningIntervalSpin
                            from: 1
                            to: 60
                            value: 5
                        }
                    }
                }

                // Return-Parameter
                GroupBox {
                    id: returnParams
                    title: "Return-Parameter"
                    Layout.fillWidth: true
                    visible: actionComboBox.currentText === "Return"

                    GridLayout {
                        anchors.fill: parent
                        columns: 2

                        Label { text: "Höhe (m):" }
                        SpinBox {
                            id: returnAltitudeSpin
                            from: 0
                            to: 1000
                            value: 50
                        }

                        Label { text: "Geschwindigkeit (m/s):" }
                        SpinBox {
                            id: returnSpeedSpin
                            from: 1
                            to: 20
                            value: 5
                        }

                        Label { text: "Timeout (s):" }
                        SpinBox {
                            id: returnTimeoutSpin
                            from: 0
                            to: 3600
                            value: 300
                        }
                    }
                }

                // Land-Parameter
                GroupBox {
                    id: landParams
                    title: "Land-Parameter"
                    Layout.fillWidth: true
                    visible: actionComboBox.currentText === "Land"

                    GridLayout {
                        anchors.fill: parent
                        columns: 2

                        Label { text: "Sinkrate (m/s):" }
                        SpinBox {
                            id: sinkRateSpin
                            from: 1
                            to: 10
                            value: 2
                        }

                        Label { text: "Timeout (s):" }
                        SpinBox {
                            id: landTimeoutSpin
                            from: 0
                            to: 3600
                            value: 300
                        }
                    }
                }
            }
        }

        // Status
        GroupBox {
            title: "Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2

                Label { text: "Status:" }
                Label { text: viewModel.status }

                Label { text: "Aktiv:" }
                Label { text: viewModel.is_active ? "Ja" : "Nein" }

                Label { text: "Fehler:" }
                Label { text: viewModel.is_error ? "Ja" : "Nein" }

                Label { text: "Fehlermeldung:" }
                Label { text: viewModel.error_message }

                Label { text: "Distanz zur Grenze:" }
                Label { text: viewModel.distance_to_boundary.toFixed(2) + " m" }

                Label { text: "Höhenverletzung:" }
                Label { text: viewModel.altitude_violation ? "Ja" : "Nein" }

                Label { text: "Grenzüberschreitung:" }
                Label { text: viewModel.boundary_violation ? "Ja" : "Nein" }

                Label { text: "Aktion läuft:" }
                Label { text: viewModel.action_in_progress ? "Ja" : "Nein" }

                Label { text: "Aktion-Timeout:" }
                Label { text: viewModel.action_timeout ? "Ja" : "Nein" }
            }
        }

        // Statistiken
        GroupBox {
            title: "Statistiken"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2

                Label { text: "Grenzüberschreitungen:" }
                Label { text: viewModel.statistics.boundary_violations }

                Label { text: "Höhenverletzungen:" }
                Label { text: viewModel.statistics.altitude_violations }

                Label { text: "Warnungen:" }
                Label { text: viewModel.statistics.warnings }

                Label { text: "Aktionen:" }
                Label { text: viewModel.statistics.actions }

                Label { text: "Erfolgreiche Aktionen:" }
                Label { text: viewModel.statistics.successful_actions }

                Label { text: "Fehlgeschlagene Aktionen:" }
                Label { text: viewModel.statistics.failed_actions }

                Label { text: "Timeout-Aktionen:" }
                Label { text: viewModel.statistics.timeout_actions }
            }
        }

        // Steuerung
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "Aktivieren"
                enabled: !viewModel.is_active
                onClicked: viewModel.activate()
            }

            Button {
                text: "Deaktivieren"
                enabled: viewModel.is_active
                onClicked: viewModel.deactivate()
            }
        }
    }

    // Fehler-Dialog
    Dialog {
        id: errorDialog
        title: "Fehler"
        standardButtons: Dialog.Ok
        modal: true

        Label {
            text: viewModel.error_message
        }
    }

    // Signal-Handler
    Connections {
        target: viewModel

        function onError_occurred(error_message) {
            errorDialog.open()
        }
    }
} 