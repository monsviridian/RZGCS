import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: root
    title: "Kollisionsvermeidung"
    width: 800
    height: 600
    visible: true

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Steuerung
        GroupBox {
            title: "Steuerung"
            Layout.fillWidth: true

            RowLayout {
                anchors.fill: parent
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

        // Status
        GroupBox {
            title: "Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2

                Label { text: "Aktiv:" }
                Label { text: viewModel.is_active ? "Ja" : "Nein" }

                Label { text: "Fehler:" }
                Label { text: viewModel.is_error ? "Ja" : "Nein" }

                Label { text: "Fehlermeldung:" }
                Label { text: viewModel.error_message }

                Label { text: "Aktuelle Strategie:" }
                Label { text: viewModel.current_strategy }

                Label { text: "Ausweichmanöver läuft:" }
                Label { text: viewModel.avoidance_in_progress ? "Ja" : "Nein" }
            }
        }

        // Erkannte Objekte
        GroupBox {
            title: "Erkannte Objekte"
            Layout.fillWidth: true

            ListView {
                id: objectsList
                anchors.fill: parent
                model: viewModel.detected_objects
                delegate: Rectangle {
                    width: parent.width
                    height: 60
                    color: index % 2 === 0 ? "#f0f0f0" : "white"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        spacing: 5

                        Label {
                            text: "ID: " + modelData.id + " | Typ: " + modelData.type
                            font.bold: true
                        }

                        Label {
                            text: "Position: " + 
                                  "Lat: " + modelData.position.lat.toFixed(6) + ", " +
                                  "Lon: " + modelData.position.lon.toFixed(6) + ", " +
                                  "Alt: " + modelData.position.alt.toFixed(2) + "m"
                        }

                        Label {
                            text: "Geschwindigkeit: " +
                                  "Vx: " + modelData.velocity.vx.toFixed(2) + "m/s, " +
                                  "Vy: " + modelData.velocity.vy.toFixed(2) + "m/s, " +
                                  "Vz: " + modelData.velocity.vz.toFixed(2) + "m/s"
                        }

                        Label {
                            text: "Größe: " +
                                  "L: " + modelData.size.length.toFixed(2) + "m, " +
                                  "B: " + modelData.size.width.toFixed(2) + "m, " +
                                  "H: " + modelData.size.height.toFixed(2) + "m"
                        }

                        Label {
                            text: "Konfidenz: " + (modelData.confidence * 100).toFixed(1) + "%"
                        }
                    }
                }
            }
        }

        // Statistiken
        GroupBox {
            title: "Statistiken"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2

                Label { text: "Gesamterkennungen:" }
                Label { text: viewModel.statistics.total_detections }

                Label { text: "Statische Objekte:" }
                Label { text: viewModel.statistics.static_detections }

                Label { text: "Dynamische Objekte:" }
                Label { text: viewModel.statistics.dynamic_detections }

                Label { text: "Unbekannte Objekte:" }
                Label { text: viewModel.statistics.unknown_detections }

                Label { text: "Ausweichmanöver:" }
                Label { text: viewModel.statistics.avoidance_maneuvers }

                Label { text: "Erfolgreiche Manöver:" }
                Label { text: viewModel.statistics.successful_avoidance }

                Label { text: "Fehlgeschlagene Manöver:" }
                Label { text: viewModel.statistics.failed_avoidance }

                Label { text: "Durchschn. Reaktionszeit:" }
                Label { text: viewModel.statistics.average_response_time.toFixed(2) + " ms" }
            }
        }

        // Log
        GroupBox {
            title: "Log"
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: logList
                anchors.fill: parent
                model: viewModel.log_events
                delegate: Rectangle {
                    width: parent.width
                    height: 40
                    color: {
                        switch(modelData.severity) {
                            case "error": return "#ffebee"
                            case "warning": return "#fff3e0"
                            default: return index % 2 === 0 ? "#f5f5f5" : "white"
                        }
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        spacing: 10

                        Label {
                            text: modelData.timestamp
                            font.family: "monospace"
                        }

                        Label {
                            text: modelData.type
                            font.bold: true
                        }

                        Label {
                            text: modelData.description
                            Layout.fillWidth: true
                        }

                        Label {
                            text: modelData.severity
                            color: {
                                switch(modelData.severity) {
                                    case "error": return "#d32f2f"
                                    case "warning": return "#f57c00"
                                    default: return "black"
                                }
                            }
                        }
                    }
                }
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