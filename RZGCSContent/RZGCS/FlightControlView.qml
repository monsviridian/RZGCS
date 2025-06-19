import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Dialogs

Window {
    id: root
    width: 1200
    height: 800
    visible: true
    title: "Flugsteuerung"

    // ViewModel-Instanz
    property var viewModel

    // Hauptlayout
    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Linke Seite: Flugmodus und Steuerungsmodus
        ColumnLayout {
            Layout.preferredWidth: 300
            Layout.fillHeight: true
            spacing: 10

            // Flugmodus-Panel
            GroupBox {
                title: "Flugmodus"
                Layout.fillWidth: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Flugmodus-Status
                    Label { text: "Aktueller Modus:" }
                    Label { 
                        text: viewModel.flight_mode
                        color: {
                            switch(viewModel.flight_mode) {
                                case "MANUAL": return "blue"
                                case "ASSISTED": return "green"
                                case "AUTONOMOUS": return "purple"
                                case "EMERGENCY": return "red"
                                default: return "black"
                            }
                        }
                    }

                    // Flugmodus-Aktionen
                    Button {
                        text: "Manuell"
                        Layout.fillWidth: true
                        enabled: !viewModel.is_manual_mode
                        onClicked: viewModel.set_mode("MANUAL")
                    }

                    Button {
                        text: "Unterstützt"
                        Layout.fillWidth: true
                        enabled: !viewModel.is_assisted_mode
                        onClicked: viewModel.set_mode("ASSISTED")
                    }

                    Button {
                        text: "Autonom"
                        Layout.fillWidth: true
                        enabled: !viewModel.is_autonomous_mode
                        onClicked: viewModel.set_mode("AUTONOMOUS")
                    }

                    Button {
                        text: "Notfall"
                        Layout.fillWidth: true
                        enabled: !viewModel.is_emergency_mode
                        onClicked: viewModel.set_mode("EMERGENCY")
                    }
                }
            }

            // Steuerungsmodus-Panel
            GroupBox {
                title: "Steuerungsmodus"
                Layout.fillWidth: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Steuerungsmodus-Status
                    Label { text: "Aktueller Modus:" }
                    Label { 
                        text: viewModel.control_mode
                        color: {
                            switch(viewModel.control_mode) {
                                case "POSITION": return "blue"
                                case "VELOCITY": return "green"
                                case "ATTITUDE": return "purple"
                                case "RATE": return "orange"
                                default: return "black"
                            }
                        }
                    }

                    // Steuerungsmodus-Aktionen
                    Button {
                        text: "Position"
                        Layout.fillWidth: true
                        enabled: viewModel.control_mode !== "POSITION"
                        onClicked: viewModel.set_control_mode("POSITION")
                    }

                    Button {
                        text: "Geschwindigkeit"
                        Layout.fillWidth: true
                        enabled: viewModel.control_mode !== "VELOCITY"
                        onClicked: viewModel.set_control_mode("VELOCITY")
                    }

                    Button {
                        text: "Attitude"
                        Layout.fillWidth: true
                        enabled: viewModel.control_mode !== "ATTITUDE"
                        onClicked: viewModel.set_control_mode("ATTITUDE")
                    }

                    Button {
                        text: "Rate"
                        Layout.fillWidth: true
                        enabled: viewModel.control_mode !== "RATE"
                        onClicked: viewModel.set_control_mode("RATE")
                    }
                }
            }
        }

        // Mittlere Seite: Steuerung
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            // Steuerungs-Panel
            GroupBox {
                title: "Steuerung"
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Positionssteuerung
                    GroupBox {
                        title: "Position"
                        Layout.fillWidth: true
                        visible: viewModel.control_mode === "POSITION"

                        GridLayout {
                            anchors.fill: parent
                            columns: 2

                            Label { text: "Latitude:" }
                            TextField {
                                id: latitudeField
                                Layout.fillWidth: true
                                validator: DoubleValidator { bottom: -90.0; top: 90.0 }
                            }

                            Label { text: "Longitude:" }
                            TextField {
                                id: longitudeField
                                Layout.fillWidth: true
                                validator: DoubleValidator { bottom: -180.0; top: 180.0 }
                            }

                            Label { text: "Altitude:" }
                            TextField {
                                id: altitudeField
                                Layout.fillWidth: true
                                validator: DoubleValidator { bottom: 0.0 }
                            }

                            Button {
                                text: "Position halten"
                                Layout.fillWidth: true
                                enabled: !viewModel.is_manual_mode
                                onClicked: viewModel.hold_position()
                            }

                            Button {
                                text: "Zu Position bewegen"
                                Layout.fillWidth: true
                                enabled: !viewModel.is_manual_mode
                                onClicked: {
                                    if (latitudeField.text && longitudeField.text && altitudeField.text) {
                                        viewModel.move_to_position({
                                            'latitude': parseFloat(latitudeField.text),
                                            'longitude': parseFloat(longitudeField.text),
                                            'altitude': parseFloat(altitudeField.text)
                                        })
                                    }
                                }
                            }
                        }
                    }

                    // Attitudensteuerung
                    GroupBox {
                        title: "Attitude"
                        Layout.fillWidth: true
                        visible: viewModel.control_mode === "ATTITUDE"

                        GridLayout {
                            anchors.fill: parent
                            columns: 2

                            Label { text: "Roll:" }
                            TextField {
                                id: rollField
                                Layout.fillWidth: true
                                validator: DoubleValidator { bottom: -180.0; top: 180.0 }
                            }

                            Label { text: "Pitch:" }
                            TextField {
                                id: pitchField
                                Layout.fillWidth: true
                                validator: DoubleValidator { bottom: -90.0; top: 90.0 }
                            }

                            Label { text: "Yaw:" }
                            TextField {
                                id: yawField
                                Layout.fillWidth: true
                                validator: DoubleValidator { bottom: -180.0; top: 180.0 }
                            }

                            Button {
                                text: "Zu Attitude rotieren"
                                Layout.fillWidth: true
                                enabled: !viewModel.is_manual_mode
                                onClicked: {
                                    if (rollField.text && pitchField.text && yawField.text) {
                                        viewModel.rotate_to_attitude({
                                            'roll': parseFloat(rollField.text),
                                            'pitch': parseFloat(pitchField.text),
                                            'yaw': parseFloat(yawField.text)
                                        })
                                    }
                                }
                            }
                        }
                    }

                    // Schubsteuerung
                    GroupBox {
                        title: "Schub"
                        Layout.fillWidth: true

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 5

                            Slider {
                                id: thrustSlider
                                Layout.fillWidth: true
                                from: 0.0
                                to: 1.0
                                value: 0.0
                                onValueChanged: viewModel.set_thrust(value)
                            }

                            Label {
                                text: "Schub: " + (thrustSlider.value * 100).toFixed(0) + "%"
                                Layout.fillWidth: true
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }
            }

            // Status-Panel
            GroupBox {
                title: "Status"
                Layout.fillWidth: true

                GridLayout {
                    anchors.fill: parent
                    columns: 2

                    Label { text: "Flugmodus:" }
                    Label { 
                        text: viewModel.flight_mode
                        color: {
                            switch(viewModel.flight_mode) {
                                case "MANUAL": return "blue"
                                case "ASSISTED": return "green"
                                case "AUTONOMOUS": return "purple"
                                case "EMERGENCY": return "red"
                                default: return "black"
                            }
                        }
                    }

                    Label { text: "Steuerungsmodus:" }
                    Label { 
                        text: viewModel.control_mode
                        color: {
                            switch(viewModel.control_mode) {
                                case "POSITION": return "blue"
                                case "VELOCITY": return "green"
                                case "ATTITUDE": return "purple"
                                case "RATE": return "orange"
                                default: return "black"
                            }
                        }
                    }

                    Label { text: "Status:" }
                    Label { 
                        text: viewModel.control_status
                        color: {
                            switch(viewModel.control_status) {
                                case "IDLE": return "gray"
                                case "ACTIVE": return "green"
                                case "COMPLETED": return "blue"
                                case "ERROR": return "red"
                                default: return "black"
                            }
                        }
                    }
                }
            }
        }

        // Rechte Seite: Log und Notfall
        ColumnLayout {
            Layout.preferredWidth: 300
            Layout.fillHeight: true
            spacing: 10

            // Log-Panel
            GroupBox {
                title: "Log"
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Log-Liste
                    ListView {
                        id: logListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: viewModel.log_events
                        delegate: Text {
                            text: modelData
                            color: "black"
                            font.pixelSize: 12
                        }
                        clip: true
                    }

                    // Letztes Event
                    Label {
                        text: "Letztes Event: " + viewModel.last_event
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }
                }
            }

            // Notfall-Panel
            GroupBox {
                title: "Notfall"
                Layout.fillWidth: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    Button {
                        text: "NOTSTOPP"
                        Layout.fillWidth: true
                        background: Rectangle {
                            color: "red"
                        }
                        contentItem: Text {
                            text: "NOTSTOPP"
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.bold: true
                            font.pixelSize: 16
                        }
                        onClicked: viewModel.emergency_stop()
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
            wrapMode: Text.WordWrap
        }
    }

    // Fehler-Handler
    Connections {
        target: viewModel
        function onErrorChanged(isError, message) {
            if (isError) {
                errorDialog.open()
            }
        }
    }
} 