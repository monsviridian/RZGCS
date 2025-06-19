import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Dialogs

import "qrc:/flight_control/views"

Window {
    id: root
    title: qsTr("Autonome Flugmodi")
    width: 800
    height: 600
    visible: true
    
    // Verbinde das ViewModel
    property var viewModel
    
    // Layout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // Modus-Auswahl
        GroupBox {
            title: qsTr("Flugmodus")
            Layout.fillWidth: true
            
            RowLayout {
                anchors.fill: parent
                
                ComboBox {
                    id: modeComboBox
                    model: ["Position Hold", "Return to Launch", "Follow Me", "Waypoint"]
                    currentIndex: 0
                    Layout.fillWidth: true
                    
                    onCurrentIndexChanged: {
                        switch (currentIndex) {
                            case 0:
                                viewModel.set_mode(AutonomousMode.POSITION_HOLD)
                                break
                            case 1:
                                viewModel.set_mode(AutonomousMode.RETURN_TO_LAUNCH)
                                break
                            case 2:
                                viewModel.set_mode(AutonomousMode.FOLLOW_ME)
                                break
                            case 3:
                                viewModel.set_mode(AutonomousMode.WAYPOINT)
                                break
                        }
                    }
                }
                
                Button {
                    text: viewModel.is_active ? qsTr("Deaktivieren") : qsTr("Aktivieren")
                    enabled: !viewModel.is_error
                    
                    onClicked: {
                        if (viewModel.is_active) {
                            viewModel.deactivate()
                        } else {
                            viewModel.activate()
                        }
                    }
                }
            }
        }
        
        // Parameter
        GroupBox {
            title: qsTr("Parameter")
            Layout.fillWidth: true
            visible: !viewModel.is_active
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 5
                
                // Position Hold Parameter
                GridLayout {
                    columns: 2
                    visible: viewModel.mode === AutonomousMode.POSITION_HOLD
                    
                    Label { text: qsTr("Zielhöhe:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.target_altitude || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.target_altitude = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Zielkurs:") }
                    SpinBox {
                        from: 0
                        to: 360
                        value: viewModel.parameters.target_heading || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.target_heading = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Positionstoleranz:") }
                    SpinBox {
                        from: 0
                        to: 10
                        value: viewModel.parameters.position_tolerance || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.position_tolerance = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Kurstoleranz:") }
                    SpinBox {
                        from: 0
                        to: 10
                        value: viewModel.parameters.heading_tolerance || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.heading_tolerance = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Max. Geschwindigkeit:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.max_speed || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.max_speed = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    CheckBox {
                        text: qsTr("Windkompensation")
                        checked: viewModel.parameters.wind_compensation || false
                        onCheckedChanged: {
                            var params = viewModel.parameters
                            params.wind_compensation = checked
                            viewModel.set_parameters(params)
                        }
                    }
                }
                
                // Return to Launch Parameter
                GridLayout {
                    columns: 2
                    visible: viewModel.mode === AutonomousMode.RETURN_TO_LAUNCH
                    
                    Label { text: qsTr("Rückkehrhöhe:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.return_altitude || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.return_altitude = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Anflughöhe:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.approach_altitude || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.approach_altitude = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Anfluggeschwindigkeit:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.approach_speed || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.approach_speed = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Landegeschwindigkeit:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.landing_speed || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.landing_speed = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Max. Geschwindigkeit:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.max_speed || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.max_speed = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Abbruchhöhe:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.abort_altitude || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.abort_altitude = value
                            viewModel.set_parameters(params)
                        }
                    }
                }
                
                // Follow Me Parameter
                GridLayout {
                    columns: 2
                    visible: viewModel.mode === AutonomousMode.FOLLOW_ME
                    
                    Label { text: qsTr("Zieldistanz:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.target_distance || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.target_distance = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Zielhöhe:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.target_altitude || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.target_altitude = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Max. Geschwindigkeit:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.max_speed || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.max_speed = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Min. Distanz:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.min_distance || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.min_distance = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Max. Distanz:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.max_distance || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.max_distance = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Höhenoffset:") }
                    SpinBox {
                        from: -100
                        to: 100
                        value: viewModel.parameters.altitude_offset || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.altitude_offset = value
                            viewModel.set_parameters(params)
                        }
                    }
                }
                
                // Waypoint Parameter
                GridLayout {
                    columns: 2
                    visible: viewModel.mode === AutonomousMode.WAYPOINT
                    
                    Label { text: qsTr("Waypoint-Radius:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.waypoint_radius || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.waypoint_radius = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Waypoint-Geschwindigkeit:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.waypoint_speed || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.waypoint_speed = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Waypoint-Höhe:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.waypoint_altitude || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.waypoint_altitude = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Waypoint-Kurs:") }
                    SpinBox {
                        from: 0
                        to: 360
                        value: viewModel.parameters.waypoint_heading || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.waypoint_heading = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Loiter-Zeit:") }
                    SpinBox {
                        from: 0
                        to: 3600
                        value: viewModel.parameters.waypoint_loiter_time || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.waypoint_loiter_time = value
                            viewModel.set_parameters(params)
                        }
                    }
                    
                    Label { text: qsTr("Loiter-Radius:") }
                    SpinBox {
                        from: 0
                        to: 100
                        value: viewModel.parameters.waypoint_loiter_radius || 0
                        onValueChanged: {
                            var params = viewModel.parameters
                            params.waypoint_loiter_radius = value
                            viewModel.set_parameters(params)
                        }
                    }
                }
            }
        }
        
        // Status
        GroupBox {
            title: qsTr("Status")
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 5
                
                Label {
                    text: qsTr("Status: ") + viewModel.status
                    color: viewModel.is_error ? "red" : "black"
                }
                
                Label {
                    text: qsTr("Fehler: ") + (viewModel.error_message || qsTr("Keine"))
                    color: "red"
                    visible: viewModel.is_error
                }
                
                Label {
                    text: qsTr("Fortschritt: ") + Math.round(viewModel.progress * 100) + "%"
                }
                
                Label {
                    text: qsTr("Verbleibende Zeit: ") + Math.round(viewModel.remaining_time) + "s"
                    visible: viewModel.remaining_time > 0
                }
                
                Label {
                    text: qsTr("Verbleibende Distanz: ") + Math.round(viewModel.remaining_distance) + "m"
                    visible: viewModel.remaining_distance > 0
                }
            }
        }
        
        // Position
        GroupBox {
            title: qsTr("Position")
            Layout.fillWidth: true
            
            GridLayout {
                columns: 2
                anchors.fill: parent
                
                Label { text: qsTr("Aktuelle Position:") }
                Label {
                    text: "Lat: " + viewModel.current_position.lat.toFixed(6) + 
                          ", Lon: " + viewModel.current_position.lon.toFixed(6) + 
                          ", Alt: " + viewModel.current_position.alt.toFixed(2) + "m"
                }
                
                Label { text: qsTr("Zielposition:") }
                Label {
                    text: "Lat: " + viewModel.target_position.lat.toFixed(6) + 
                          ", Lon: " + viewModel.target_position.lon.toFixed(6) + 
                          ", Alt: " + viewModel.target_position.alt.toFixed(2) + "m"
                }
                
                Label { text: qsTr("Aktueller Kurs:") }
                Label { text: viewModel.current_heading.toFixed(1) + "°" }
                
                Label { text: qsTr("Zielkurs:") }
                Label { text: viewModel.target_heading.toFixed(1) + "°" }
                
                Label { text: qsTr("Aktuelle Geschwindigkeit:") }
                Label { text: viewModel.current_speed.toFixed(1) + "m/s" }
                
                Label { text: qsTr("Zielgeschwindigkeit:") }
                Label { text: viewModel.target_speed.toFixed(1) + "m/s" }
                
                Label { text: qsTr("Aktuelle Höhe:") }
                Label { text: viewModel.current_altitude.toFixed(1) + "m" }
                
                Label { text: qsTr("Zielhöhe:") }
                Label { text: viewModel.target_altitude.toFixed(1) + "m" }
            }
        }
        
        // Statistiken
        GroupBox {
            title: qsTr("Statistiken")
            Layout.fillWidth: true
            
            GridLayout {
                columns: 2
                anchors.fill: parent
                
                Label { text: qsTr("Gesamtflugzeit:") }
                Label { text: Math.round(viewModel.statistics.total_flight_time) + "s" }
                
                Label { text: qsTr("Gesamtdistanz:") }
                Label { text: Math.round(viewModel.statistics.total_distance) + "m" }
                
                Label { text: qsTr("Durchschnittsgeschwindigkeit:") }
                Label { text: viewModel.statistics.average_speed.toFixed(1) + "m/s" }
                
                Label { text: qsTr("Max. Geschwindigkeit:") }
                Label { text: viewModel.statistics.max_speed.toFixed(1) + "m/s" }
                
                Label { text: qsTr("Min. Geschwindigkeit:") }
                Label { text: viewModel.statistics.min_speed.toFixed(1) + "m/s" }
                
                Label { text: qsTr("Durchschnittshöhe:") }
                Label { text: viewModel.statistics.average_altitude.toFixed(1) + "m" }
                
                Label { text: qsTr("Max. Höhe:") }
                Label { text: viewModel.statistics.max_altitude.toFixed(1) + "m" }
                
                Label { text: qsTr("Min. Höhe:") }
                Label { text: viewModel.statistics.min_altitude.toFixed(1) + "m" }
                
                Label { text: qsTr("Moduswechsel:") }
                Label { text: viewModel.statistics.mode_changes }
                
                Label { text: qsTr("Fehler:") }
                Label { text: viewModel.statistics.error_count }
                
                Label { text: qsTr("Erfolgsrate:") }
                Label { text: (viewModel.statistics.success_rate * 100).toFixed(1) + "%" }
                
                Label { text: qsTr("Batterieverbrauch:") }
                Label { text: viewModel.statistics.battery_usage.toFixed(1) + "%" }
                
                Label { text: qsTr("Windkompensationszeit:") }
                Label { text: Math.round(viewModel.statistics.wind_compensation_time) + "s" }
                
                Label { text: qsTr("Position Hold Zeit:") }
                Label { text: Math.round(viewModel.statistics.position_hold_time) + "s" }
                
                Label { text: qsTr("Return to Launch Zeit:") }
                Label { text: Math.round(viewModel.statistics.return_to_launch_time) + "s" }
                
                Label { text: qsTr("Follow Me Zeit:") }
                Label { text: Math.round(viewModel.statistics.follow_me_time) + "s" }
                
                Label { text: qsTr("Waypoint Zeit:") }
                Label { text: Math.round(viewModel.statistics.waypoint_time) + "s" }
            }
        }
    }
    
    // Fehler-Dialog
    Dialog {
        id: errorDialog
        title: qsTr("Fehler")
        standardButtons: Dialog.Ok
        
        Label {
            text: viewModel.error_message
            color: "red"
        }
    }
    
    // Verbinde die Signale
    Connections {
        target: viewModel
        
        function onErrorOccurred(error_message) {
            errorDialog.open()
        }
    }
} 