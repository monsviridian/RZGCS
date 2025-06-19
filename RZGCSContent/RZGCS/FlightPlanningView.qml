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
    title: "Flugplanung"

    // ViewModel-Instanz - verbunden mit dem im Backend registrierten flightPlanningViewModel
    property var viewModel: flightPlanningViewModel

    // Hauptlayout
    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Linke Seite: Missions- und Routenverwaltung
        ColumnLayout {
            Layout.preferredWidth: 300
            Layout.fillHeight: true
            spacing: 10

            // Missions-Panel
            GroupBox {
                title: "Mission"
                Layout.fillWidth: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Missions-Status
                    Label { text: "Status:" }
                    Label { 
                        text: viewModel.mission_status
                        color: {
                            switch(viewModel.mission_status) {
                                case "ACTIVE": return "green"
                                case "PAUSED": return "orange"
                                case "COMPLETED": return "blue"
                                case "ERROR": return "red"
                                default: return "black"
                            }
                        }
                    }

                    // Missions-Aktionen
                    Button {
                        text: "Neue Mission"
                        Layout.fillWidth: true
                        onClicked: newMissionDialog.open()
                    }

                    Button {
                        text: "Mission starten"
                        Layout.fillWidth: true
                        enabled: viewModel.has_mission && !viewModel.is_mission_active
                        onClicked: viewModel.start_mission()
                    }

                    Button {
                        text: viewModel.is_mission_paused ? "Fortsetzen" : "Pausieren"
                        Layout.fillWidth: true
                        enabled: viewModel.has_mission && (viewModel.is_mission_active || viewModel.is_mission_paused)
                        onClicked: {
                            if (viewModel.is_mission_paused) {
                                viewModel.resume_mission()
                            } else {
                                viewModel.pause_mission()
                            }
                        }
                    }

                    Button {
                        text: "Mission beenden"
                        Layout.fillWidth: true
                        enabled: viewModel.has_mission && viewModel.is_mission_active
                        onClicked: viewModel.complete_mission()
                    }

                    Button {
                        text: "Mission abbrechen"
                        Layout.fillWidth: true
                        enabled: viewModel.has_mission && (viewModel.is_mission_active || viewModel.is_mission_paused)
                        onClicked: viewModel.abort_mission()
                    }
                }
            }

            // Routen-Panel
            GroupBox {
                title: "Routen"
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Routen-Liste
                    ListView {
                        id: routesListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: viewModel.has_mission ? viewModel._mission.routes : []
                        delegate: ItemDelegate {
                            width: parent.width
                            text: modelData.name
                            highlighted: viewModel.has_route && viewModel.route_id === modelData.id
                            onClicked: {
                                viewModel._current_route = modelData
                                viewModel.route_changed()
                            }
                        }
                    }

                    // Routen-Aktionen
                    Button {
                        text: "Route hinzufügen"
                        Layout.fillWidth: true
                        enabled: viewModel.has_mission
                        onClicked: newRouteDialog.open()
                    }
                }
            }
        }

        // Mittlere Seite: Wegpunktverwaltung
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            // Wegpunkte-Panel
            GroupBox {
                title: "Wegpunkte"
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    // Wegpunkte-Liste
                    ListView {
                        id: waypointsListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: viewModel.has_route ? viewModel._current_route.waypoints : []
                        delegate: ItemDelegate {
                            width: parent.width
                            text: `${modelData.type.value} - ${modelData.action.value}`
                            highlighted: viewModel.has_waypoint && viewModel.waypoint_id === modelData.id
                            onClicked: {
                                viewModel._current_waypoint = modelData
                                viewModel.waypoint_changed()
                            }
                        }
                    }

                    // Wegpunkte-Aktionen
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 5

                        Button {
                            text: "Wegpunkt hinzufügen"
                            Layout.fillWidth: true
                            enabled: viewModel.has_route
                            onClicked: newWaypointDialog.open()
                        }

                        Button {
                            text: "Wegpunkt bearbeiten"
                            Layout.fillWidth: true
                            enabled: viewModel.has_waypoint
                            onClicked: editWaypointDialog.open()
                        }

                        Button {
                            text: "Wegpunkt löschen"
                            Layout.fillWidth: true
                            enabled: viewModel.has_waypoint
                            onClicked: viewModel.delete_waypoint(viewModel.waypoint_id)
                        }
                    }
                }
            }

            // Aktueller Wegpunkt
            GroupBox {
                title: "Aktueller Wegpunkt"
                Layout.fillWidth: true
                visible: viewModel.has_waypoint

                GridLayout {
                    anchors.fill: parent
                    columns: 2

                    Label { text: "ID:" }
                    Label { text: viewModel.waypoint_id }

                    Label { text: "Typ:" }
                    Label { text: viewModel.waypoint_type }

                    Label { text: "Aktion:" }
                    Label { text: viewModel.waypoint_action }

                    Label { text: "Position:" }
                    Label { 
                        text: viewModel.has_waypoint ? 
                            `Lat: ${viewModel.waypoint_position[0].toFixed(6)}, Lon: ${viewModel.waypoint_position[1].toFixed(6)}, Alt: ${viewModel.waypoint_position[2].toFixed(2)}` : 
                            ""
                    }
                }
            }
        }

        // Rechte Seite: Log und Steuerung
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

            // Steuerungs-Panel
            GroupBox {
                title: "Steuerung"
                Layout.fillWidth: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    Button {
                        text: "Nächster Wegpunkt"
                        Layout.fillWidth: true
                        enabled: viewModel.has_mission && viewModel.is_mission_active
                        onClicked: viewModel.next_waypoint()
                    }
                }
            }
        }
    }

    // Dialoge
    Dialog {
        id: newMissionDialog
        title: "Neue Mission"
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Label { text: "Name:" }
            TextField {
                id: missionNameField
                Layout.fillWidth: true
            }
        }

        onAccepted: {
            if (missionNameField.text) {
                viewModel.create_mission(missionNameField.text)
                missionNameField.text = ""
            }
        }
    }

    Dialog {
        id: newRouteDialog
        title: "Neue Route"
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Label { text: "Name:" }
            TextField {
                id: routeNameField
                Layout.fillWidth: true
            }
        }

        onAccepted: {
            if (routeNameField.text) {
                viewModel.add_route(routeNameField.text)
                routeNameField.text = ""
            }
        }
    }

    Dialog {
        id: newWaypointDialog
        title: "Neuer Wegpunkt"
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Label { text: "Typ:" }
            ComboBox {
                id: waypointTypeCombo
                Layout.fillWidth: true
                model: ["TAKEOFF", "LANDING", "WAYPOINT", "HOLD", "SURVEY", "ACTION"]
            }

            Label { text: "Aktion:" }
            ComboBox {
                id: waypointActionCombo
                Layout.fillWidth: true
                model: ["NONE", "PHOTO", "VIDEO", "SCAN", "DROP", "PICKUP"]
            }

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
        }

        onAccepted: {
            if (latitudeField.text && longitudeField.text && altitudeField.text) {
                viewModel.add_waypoint(
                    viewModel.route_id,
                    waypointTypeCombo.currentText,
                    {
                        'latitude': parseFloat(latitudeField.text),
                        'longitude': parseFloat(longitudeField.text),
                        'altitude': parseFloat(altitudeField.text)
                    },
                    waypointActionCombo.currentText
                )
                latitudeField.text = ""
                longitudeField.text = ""
                altitudeField.text = ""
            }
        }
    }

    Dialog {
        id: editWaypointDialog
        title: "Wegpunkt bearbeiten"
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Label { text: "Typ:" }
            ComboBox {
                id: editWaypointTypeCombo
                Layout.fillWidth: true
                model: ["TAKEOFF", "LANDING", "WAYPOINT", "HOLD", "SURVEY", "ACTION"]
                currentIndex: {
                    if (!viewModel.has_waypoint) return 0
                    return model.indexOf(viewModel.waypoint_type)
                }
            }

            Label { text: "Aktion:" }
            ComboBox {
                id: editWaypointActionCombo
                Layout.fillWidth: true
                model: ["NONE", "PHOTO", "VIDEO", "SCAN", "DROP", "PICKUP"]
                currentIndex: {
                    if (!viewModel.has_waypoint) return 0
                    return model.indexOf(viewModel.waypoint_action)
                }
            }

            Label { text: "Latitude:" }
            TextField {
                id: editLatitudeField
                Layout.fillWidth: true
                validator: DoubleValidator { bottom: -90.0; top: 90.0 }
                text: viewModel.has_waypoint ? viewModel.waypoint_position[0] : ""
            }

            Label { text: "Longitude:" }
            TextField {
                id: editLongitudeField
                Layout.fillWidth: true
                validator: DoubleValidator { bottom: -180.0; top: 180.0 }
                text: viewModel.has_waypoint ? viewModel.waypoint_position[1] : ""
            }

            Label { text: "Altitude:" }
            TextField {
                id: editAltitudeField
                Layout.fillWidth: true
                validator: DoubleValidator { bottom: 0.0 }
                text: viewModel.has_waypoint ? viewModel.waypoint_position[2] : ""
            }
        }

        onAccepted: {
            if (editLatitudeField.text && editLongitudeField.text && editAltitudeField.text) {
                viewModel.update_waypoint(
                    viewModel.waypoint_id,
                    {
                        'latitude': parseFloat(editLatitudeField.text),
                        'longitude': parseFloat(editLongitudeField.text),
                        'altitude': parseFloat(editAltitudeField.text)
                    },
                    editWaypointActionCombo.currentText
                )
            }
        }
    }
} 