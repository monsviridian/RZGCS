import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import Components 1.0

Rectangle {
    id: root
    color: "#1e1e1e"
    border.color: "#404040"
    border.width: 1

    // Properties for connection to backend
    property var flightControlViewModel: null
    property var missionViewModel: null
    property var telemetryViewModel: null
    
    // Mission properties
    property var currentMission: null
    property int currentWaypointIndex: 0
    property int totalWaypoints: 0
    property bool missionActive: false
    
    // Flight status properties
    property bool isConnected: false
    property bool isArmed: false
    property string currentFlightMode: "STABILIZE"
    property real currentAltitude: 0.0
    property real currentGroundSpeed: 0.0
    property real currentHeading: 0.0
    property real currentBattery: 100.0

    // Main layout
    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Left panel - Flight instruments and telemetry
        ColumnLayout {
            Layout.fillHeight: true
            Layout.preferredWidth: 350
            spacing: 10

            // Connection status and flight mode
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 60
                color: "#2a2a2a"
                radius: 6
                border.color: "#404040"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10

                    // Connection indicator
                    Rectangle {
                        Layout.preferredWidth: 20
                        Layout.preferredHeight: 20
                        radius: 10
                        color: isConnected ? "#00ff00" : "#ff0000"
                        border.color: "#ffffff"
                        border.width: 2
                    }

                    Label {
                        text: isConnected ? "Connected" : "Disconnected"
                        color: isConnected ? "#00ff00" : "#ff0000"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    Item { Layout.fillWidth: true }

                    // Flight mode display
                    Label {
                        text: "Mode:"
                        color: "#cccccc"
                        font.pixelSize: 12
                    }

                    Label {
                        text: currentFlightMode
                        color: "#ffff00"
                        font.pixelSize: 16
                        font.bold: true
                    }
                }
            }

            // Artificial horizon
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 250
                color: "#2a2a2a"
                radius: 6
                border.color: "#404040"
                border.width: 1

                ArtificialHorizon {
                    id: artificialHorizon
                    anchors.centerIn: parent
                    width: Math.min(parent.width - 20, parent.height - 20)
                    height: width
                    roll: 0.0
                    pitch: 0.0
                    disarmed: !isArmed
                }
            }

            // Telemetry panel
            TelemetryPanel {
                id: telemetryPanel
                Layout.fillWidth: true
                Layout.preferredHeight: 200
                altitude: currentAltitude
                groundSpeed: currentGroundSpeed
                heading: currentHeading
                batteryPercent: currentBattery
            }

            // Mission info display
            MissionInfoDisplay {
                id: missionInfoDisplay
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                currentWaypoint: currentWaypointIndex
                waypointCount: totalWaypoints
                distanceToWaypoint: "0.0"
            }
        }

        // Center panel - Mission planning and map
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            // Mission planning toolbar
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                color: "#2a2a2a"
                radius: 6
                border.color: "#404040"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10

                    Label {
                        text: "Mission Planning"
                        color: "#ffffff"
                        font.pixelSize: 16
                        font.bold: true
                    }

                    Item { Layout.fillWidth: true }

                    // Mission control buttons
                    Button {
                        text: "New Mission"
                        Layout.preferredWidth: 100
                        enabled: isConnected
                        onClicked: newMissionDialog.open()
                    }

                    Button {
                        text: "Load Mission"
                        Layout.preferredWidth: 100
                        enabled: isConnected
                        onClicked: loadMissionDialog.open()
                    }

                    Button {
                        text: "Save Mission"
                        Layout.preferredWidth: 100
                        enabled: currentMission !== null
                        onClicked: saveMissionDialog.open()
                    }

                    Button {
                        text: "Upload Mission"
                        Layout.preferredWidth: 100
                        enabled: currentMission !== null && isConnected
                        onClicked: {
                            if (missionViewModel) {
                                missionViewModel.uploadMission(currentMission)
                            }
                        }
                    }
                }
            }

            // Map view placeholder
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#1a1a1a"
                radius: 6
                border.color: "#404040"
                border.width: 1

                // Placeholder for map component
                Text {
                    anchors.centerIn: parent
                    text: "Map View\nMission Planning Interface"
                    color: "#666666"
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                }

                // Mission waypoints list overlay
                Rectangle {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 10
                    width: 250
                    height: Math.min(300, parent.height - 20)
                    color: "#2a2a2a"
                    radius: 6
                    border.color: "#404040"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 5

                        Label {
                            text: "Waypoints"
                            color: "#ffffff"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.fillWidth: true
                        }

                        ListView {
                            id: waypointListView
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            model: ListModel {
                                // Will be populated with waypoints
                            }

                            delegate: Rectangle {
                                width: parent.width
                                height: 40
                                color: index === currentWaypointIndex ? "#4a4a4a" : "transparent"
                                radius: 4

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 5
                                    spacing: 10

                                    Label {
                                        text: "WP " + (index + 1)
                                        color: "#ffffff"
                                        font.pixelSize: 12
                                        font.bold: true
                                    }

                                    Label {
                                        text: model.latitude.toFixed(6) + ", " + model.longitude.toFixed(6)
                                        color: "#cccccc"
                                        font.pixelSize: 10
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: model.altitude + "m"
                                        color: "#00aaff"
                                        font.pixelSize: 10
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        currentWaypointIndex = index
                                        // TODO: Center map on waypoint
                                    }
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 5

                            Button {
                                text: "Add WP"
                                Layout.fillWidth: true
                                enabled: isConnected
                                onClicked: {
                                    // TODO: Add waypoint at current position
                                }
                            }

                            Button {
                                text: "Remove WP"
                                Layout.fillWidth: true
                                enabled: waypointListView.count > 0
                                onClicked: {
                                    // TODO: Remove selected waypoint
                                }
                            }
                        }
                    }
                }
            }
        }

        // Right panel - Flight controls
        ColumnLayout {
            Layout.fillHeight: true
            Layout.preferredWidth: 300
            spacing: 10

            // Flight mode selection
            GroupBox {
                title: "Flight Mode"
                Layout.fillWidth: true
                color: "#2a2a2a"
                font.pixelSize: 12

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10

                    ComboBox {
                        id: flightModeCombo
                        Layout.fillWidth: true
                        model: ["STABILIZE", "ALT_HOLD", "LOITER", "RTL", "AUTO", "GUIDED"]
                        enabled: isConnected
                        onActivated: {
                            if (flightControlViewModel) {
                                flightControlViewModel.setMode(currentText)
                            }
                        }
                    }

                    Button {
                        text: "Set Mode"
                        Layout.fillWidth: true
                        enabled: isConnected
                        onClicked: {
                            if (flightControlViewModel) {
                                flightControlViewModel.setMode(flightModeCombo.currentText)
                            }
                        }
                    }
                }
            }

            // Arm/Disarm controls
            GroupBox {
                title: "Vehicle Control"
                Layout.fillWidth: true
                color: "#2a2a2a"
                font.pixelSize: 12

                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    columnSpacing: 10
                    rowSpacing: 10

                    Button {
                        text: "ARM"
                        Layout.fillWidth: true
                        enabled: isConnected && !isArmed
                        highlighted: true
                        onClicked: {
                            if (flightControlViewModel) {
                                flightControlViewModel.arm()
                            }
                        }
                    }

                    Button {
                        text: "DISARM"
                        Layout.fillWidth: true
                        enabled: isConnected && isArmed
                        highlighted: true
                        onClicked: {
                            if (flightControlViewModel) {
                                flightControlViewModel.disarm()
                            }
                        }
                    }

                    Button {
                        text: "Takeoff"
                        Layout.fillWidth: true
                        enabled: isConnected && isArmed
                        onClicked: {
                            if (flightControlViewModel) {
                                flightControlViewModel.takeoff()
                            }
                        }
                    }

                    Button {
                        text: "Land"
                        Layout.fillWidth: true
                        enabled: isConnected && isArmed
                        onClicked: {
                            if (flightControlViewModel) {
                                flightControlViewModel.land()
                            }
                        }
                    }

                    Button {
                        text: "RTL"
                        Layout.fillWidth: true
                        enabled: isConnected && isArmed
                        onClicked: {
                            if (flightControlViewModel) {
                                flightControlViewModel.returnToLaunch()
                            }
                        }
                    }

                    Button {
                        text: "Hold Position"
                        Layout.fillWidth: true
                        enabled: isConnected && isArmed
                        onClicked: {
                            if (flightControlViewModel) {
                                flightControlViewModel.holdPosition()
                            }
                        }
                    }
                }
            }

            // Mission control
            GroupBox {
                title: "Mission Control"
                Layout.fillWidth: true
                color: "#2a2a2a"
                font.pixelSize: 12

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10

                    Button {
                        text: "Start Mission"
                        Layout.fillWidth: true
                        enabled: isConnected && isArmed && currentMission !== null && !missionActive
                        highlighted: true
                            onClicked: {
                            if (missionViewModel) {
                                missionViewModel.startMission(currentMission.id)
                            }
                            }
                        }

                        Button {
                        text: "Pause Mission"
                            Layout.fillWidth: true
                        enabled: missionActive
                            onClicked: {
                            if (missionViewModel) {
                                missionViewModel.pauseMission()
                            }
                            }
                        }

                        Button {
                        text: "Resume Mission"
                            Layout.fillWidth: true
                        enabled: currentMission !== null && !missionActive
                            onClicked: {
                            if (missionViewModel) {
                                missionViewModel.resumeMission()
                            }
                            }
                        }

                        Button {
                        text: "Abort Mission"
                            Layout.fillWidth: true
                        enabled: missionActive
                        highlighted: true
                            onClicked: {
                            if (missionViewModel) {
                                missionViewModel.abortMission()
                            }
                        }
                    }
                }
            }

            // Status indicators
            GroupBox {
                title: "Status"
                Layout.fillWidth: true
                color: "#2a2a2a"
                font.pixelSize: 12

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 5

                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: "Connection:"
                            color: "#cccccc"
                            font.pixelSize: 10
                        }
                        Label {
                            text: isConnected ? "Connected" : "Disconnected"
                            color: isConnected ? "#00ff00" : "#ff0000"
                            font.pixelSize: 10
                            font.bold: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: "Armed:"
                            color: "#cccccc"
                            font.pixelSize: 10
                        }
                        Label {
                            text: isArmed ? "Yes" : "No"
                            color: isArmed ? "#00ff00" : "#ff0000"
                            font.pixelSize: 10
                            font.bold: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: "Mission:"
                            color: "#cccccc"
                            font.pixelSize: 10
                        }
                        Label {
                            text: missionActive ? "Active" : "Inactive"
                            color: missionActive ? "#00ff00" : "#ffaa00"
                            font.pixelSize: 10
                            font.bold: true
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: "Battery:"
                            color: "#cccccc"
                            font.pixelSize: 10
                        }
                        Label {
                            text: currentBattery.toFixed(1) + "%"
                            color: currentBattery > 20 ? "#00ff00" : "#ff0000"
                            font.pixelSize: 10
                            font.bold: true
                        }
                    }
                }
            }
        }
    }

    // Dialogs
    Dialog {
        id: newMissionDialog
        title: "New Mission"
        width: 400
        height: 200
        modal: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Label {
                text: "Mission Name:"
                Layout.fillWidth: true
            }

            TextField {
                id: missionNameInput
                Layout.fillWidth: true
                placeholderText: "Enter mission name"
            }

            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                Button {
                    text: "Cancel"
                    onClicked: newMissionDialog.close()
                }
                Button {
                    text: "Create"
                            onClicked: {
                        if (missionViewModel && missionNameInput.text.trim() !== "") {
                            missionViewModel.createMission(missionNameInput.text.trim(), [])
                            newMissionDialog.close()
                        }
                    }
                }
            }
        }
    }

    FileDialog {
        id: loadMissionDialog
        title: "Load Mission"
        nameFilters: ["Mission files (*.json)", "All files (*)"]
        onAccepted: {
            if (missionViewModel) {
                missionViewModel.importMission(fileUrl)
            }
        }
    }

    FileDialog {
        id: saveMissionDialog
        title: "Save Mission"
        nameFilters: ["Mission files (*.json)", "All files (*)"]
        onAccepted: {
            if (missionViewModel && currentMission) {
                missionViewModel.exportMission(currentMission, fileUrl)
            }
        }
    }

    // Connections to backend
    Connections {
        target: flightControlViewModel
        enabled: flightControlViewModel !== null

        function onStateChanged() {
            // Update flight state
        }

        function onModeChanged(mode) {
            currentFlightMode = mode
            flightModeCombo.currentIndex = flightModeCombo.find(mode)
        }
    }

    Connections {
        target: missionViewModel
        enabled: missionViewModel !== null

        function onMissionCreated(mission) {
            currentMission = mission
            totalWaypoints = mission.waypoints.length
        }

        function onMissionStarted(mission) {
            missionActive = true
        }

        function onMissionCompleted(mission) {
            missionActive = false
        }

        function onMissionAborted(mission) {
            missionActive = false
        }

        function onWaypointReached(waypoint) {
            currentWaypointIndex++
        }
    }

    Connections {
        target: telemetryViewModel
        enabled: telemetryViewModel !== null

        function onAltitudeChanged(altitude) {
            currentAltitude = altitude
        }

        function onGroundSpeedChanged(speed) {
            currentGroundSpeed = speed
        }

        function onHeadingChanged(heading) {
            currentHeading = heading
        }

        function onBatteryChanged(battery) {
            currentBattery = battery
        }
    }
} 