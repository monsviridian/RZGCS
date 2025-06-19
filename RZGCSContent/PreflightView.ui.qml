/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls.Material 2.15
import QtQuick.Controls 2.15
import QtQuick.Window
import QtQuick.Layouts
import "./" as Local

Item {
    id: preflightview
    width: parent.width
    height: parent.height

    // Black background
    Rectangle {
        anchors.fill: parent
        color: "black"
        z: -1  // Behind all elements
    }

    // Status Bar
    Rectangle {
        id: statusBar
        width: parent.width
        height: 30
        color: "#2d2d2d"
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            spacing: 20
            
            Text {
                id: connectionStatus
                text: "Disconnected"
                color: "#ff0000"
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 14
            }
            
            Text {
                id: gpsStatus
                text: "GPS: No Fix"
                color: "#ff0000"
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 14
            }
            
            Text {
                id: batteryStatus
                text: "Battery: --"
                color: "#ffffff"
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 14
            }
            
            Item { Layout.fillWidth: true } // Spacer
        }
    }

    // Main content area
    Item {
        id: mainContent
        anchors.top: statusBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10

        // Grid Layout for Dashboard
        GridLayout {
            anchors.fill: parent
            columns: 2
            rowSpacing: 24
            columnSpacing: 24

            // Logo and Image
            Rectangle {
                Layout.row: 0; Layout.column: 0
                Layout.preferredWidth: 420
                Layout.preferredHeight: 180
                color: "#181f23"
                radius: 12
                border.color: "#23343b"
                border.width: 2
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 20
                    // Logo
                    ColumnLayout {
                        spacing: 0
                        Text {
                            text: "RZ"
                            color: "#3ee6ff"
                            font.pixelSize: 44
                            font.bold: true
                        }
                        Text {
                            text: "DRONE"
                            color: "#e6faff"
                            font.pixelSize: 36
                            font.bold: true
                        }
                        Text {
                            text: "SOLUTIONS"
                            color: "#e6faff"
                            font.pixelSize: 18
                            font.letterSpacing: 2
                        }
                    }
                    Rectangle {
                        width: 120; height: 80
                        color: "transparent"
                        border.color: "#3ee6ff"
                        border.width: 2
                        radius: 8
                        Text {
                            anchors.centerIn: parent
                            text: "\uD83D\uDE81"
                            color: "#3ee6ff"
                            font.pixelSize: 60
                        }
                    }
                }
            }

            // Map View
            Rectangle {
                Layout.row: 0; Layout.column: 1
                Layout.preferredWidth: 420
                Layout.preferredHeight: 180
                color: "#181f23"
                radius: 12
                border.color: "#23343b"
                border.width: 2

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8

                    Text {
                        text: "MAP VIEW"
                        color: "#7ee6ff"
                        font.pixelSize: 16
                    }

                    // Warzone-style map view
                    WarzoneFlightView {
                        id: mapView
                        anchors.fill: parent
                        showControlPanel: false  // Hide the control panel
                        
                        // Bind drone properties
                        droneLatitude: 50.110924  // Frankfurt coordinates
                        droneLongitude: 8.682127
                        droneAltitude: 100.0
                        droneHeading: 45.0
                        
                        // Map interactions
                        onMapClicked: {
                            console.log("Map clicked at: " + lat + ", " + lon)
                        }
                        
                        onAddWaypoint: {
                            console.log("Waypoint added at: " + lat + ", " + lon)
                        }
                    }
                }
            }

            // Camera View (replacing Telemetry)
            Rectangle {
                Layout.row: 1; Layout.column: 0
                Layout.preferredWidth: 420
                Layout.preferredHeight: 220
                color: "#181f23"
                radius: 12
                border.color: "#23343b"
                border.width: 2
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8
                    
                    Text {
                        text: "CAMERA FEED"
                        color: "#3ee6ff"
                        font.pixelSize: 18
                        font.bold: true
                    }
                    
                    // Camera View Area
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#0f1416"
                        radius: 8
                        
                        // Placeholder for camera feed
                        Text {
                            anchors.centerIn: parent
                            text: "No Camera Feed"
                            color: "#e6faff"
                            font.pixelSize: 16
                        }
                    }
                    
                    // Camera Controls
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Button {
                            text: "Snapshot"
                            enabled: false
                            Material.background: "#23343b"
                            Material.foreground: "#e6faff"
                        }
                        
                        Button {
                            text: "Record"
                            enabled: false
                            Material.background: "#23343b"
                            Material.foreground: "#e6faff"
                        }
                        
                        Item { Layout.fillWidth: true }  // Spacer
                        
                        Text {
                            text: "Disconnected"
                            color: "#ff0000"
                            font.pixelSize: 14
                        }
                    }
                }
            }

            // Status Values
            Rectangle {
                Layout.row: 1; Layout.column: 1
                Layout.preferredWidth: 420
                Layout.preferredHeight: 220
                color: "#181f23"
                radius: 12
                border.color: "#23343b"
                border.width: 2
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    // Altitude and Distance
                    RowLayout {
                        spacing: 32
                        ColumnLayout {
                            spacing: 0
                            Text { text: "ALTITUDE"; color: "#7ee6ff"; font.pixelSize: 14 }
                            Text { text: "120 m"; color: "#e6faff"; font.pixelSize: 32; font.bold: true }
                        }
                        ColumnLayout {
                            spacing: 0
                            Text { text: "DISTANCE"; color: "#7ee6ff"; font.pixelSize: 14 }
                            Text { text: "850 m"; color: "#e6faff"; font.pixelSize: 32; font.bold: true }
                        }
                    }

                    // Battery and Speed
                    RowLayout {
                        spacing: 32
                        // Battery Ring
                        Item {
                            width: 70; height: 70
                            Canvas {
                                anchors.fill: parent
                                property real percent: 0.78
                                onPaint: {
                                    var ctx = getContext("2d");
                                    ctx.reset();
                                    var w = width, h = height, r = Math.min(w,h)/2-6;
                                    var cx = w/2, cy = h/2;
                                    // Background circle
                                    ctx.beginPath();
                                    ctx.arc(cx, cy, r, 0, 2*Math.PI);
                                    ctx.strokeStyle = "#23343b";
                                    ctx.lineWidth = 8;
                                    ctx.stroke();
                                    // Progress
                                    ctx.beginPath();
                                    ctx.arc(cx, cy, r, -Math.PI/2, -Math.PI/2 + 2*Math.PI*percent);
                                    ctx.strokeStyle = "#3ee6ff";
                                    ctx.lineWidth = 8;
                                    ctx.stroke();
                                }
                            }
                            Text {
                                anchors.centerIn: parent
                                text: "78%"
                                color: "#e6faff"
                                font.pixelSize: 22
                                font.bold: true
                            }
                        }
                        // Speed
                        ColumnLayout {
                            spacing: 0
                            Text { text: "SPEED"; color: "#7ee6ff"; font.pixelSize: 14 }
                            Text { text: "2.8 km/h"; color: "#e6faff"; font.pixelSize: 32; font.bold: true }
                        }
                    }
                }
            }

            // FC Important Message Logs
            Rectangle {
                Layout.row: 2
                Layout.column: 0
                Layout.columnSpan: 2
                Layout.preferredHeight: 150
                Layout.fillWidth: true
                color: "#181f23"
                radius: 12
                border.color: "#23343b"
                border.width: 2

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8

                    // Header with icon and title
                    RowLayout {
                        spacing: 8
                        Text {
                            text: "⚠️"  // Warning icon
                            color: "#ffcc00"
                            font.pixelSize: 18
                        }
                        Text {
                            text: "FC Important Messages"
                            color: "#7ee6ff"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        Item { Layout.fillWidth: true }
                        // Log status indicator
                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: fcMessageArea.text.length > 0 ? "#00ff00" : "#ffcc00"
                            Layout.alignment: Qt.AlignVCenter
                        }
                    }

                    // Divider line
                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "#23343b"
                    }

                    // Log display area
                    ScrollView {
                        id: fcLogScrollView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        TextArea {
                            id: fcMessageArea
                            readOnly: true
                            wrapMode: TextArea.Wrap
                            selectByMouse: true
                            selectByKeyboard: true
                            color: "#e6faff"
                            font.pixelSize: 13
                            font.family: "Consolas"
                            
                            background: Rectangle {
                                color: "#0f1416"
                                radius: 6
                            }
                            
                            // Custom text selection color
                            selectionColor: "#3ee6ff44"
                            selectedTextColor: "#ffffff"
                            
                            // Custom scrollbar styling
                            ScrollBar.vertical: ScrollBar {
                                active: true
                                policy: ScrollBar.AsNeeded
                                
                                contentItem: Rectangle {
                                    implicitWidth: 6
                                    radius: 3
                                    color: parent.pressed ? "#3ee6ff" : "#7ee6ff"
                                }
                                
                                background: Rectangle {
                                    implicitWidth: 6
                                    color: "#23343b"
                                    radius: 3
                                }
                            }
                        }
                    }
                }

                // Property to add new messages
                property alias logText: fcMessageArea.text
                
                // Function to add new log messages
                function addLogMessage(message) {
                    var timestamp = new Date().toLocaleTimeString()
                    fcMessageArea.text = `[${timestamp}] ${message}\n` + fcMessageArea.text
                    // Auto-scroll to top
                    fcLogScrollView.ScrollBar.vertical.position = 0
                }
            }
        }
    }
    
    // Direct connection to the sensor model for real-time updates
    Connections {
        target: sensorModel
        function onDataChanged() {
            updateSensorData()
        }
    }
    
    // Connection to serialConnector for connection status
    Connections {
        target: serialConnector
        function onConnectedChanged() {
            // Update connection status
            connectionStatus.text = serialConnector.connected ? "Connected" : "Disconnected"
            connectionStatus.color = serialConnector.connected ? "#00ff00" : "#ff0000"
            
            // Update sensor data immediately when connected
            if (serialConnector.connected) {
                // Show default GPS and battery data when connected
                gpsStatus.text = "GPS: 50.110924, 8.682127 (Fixed)"
                gpsStatus.color = "#00ff00"
                batteryStatus.text = "Battery: 87% (16.2V)"
                batteryStatus.color = "#00ff00"
                
                updateSensorData()
            } else {
                // Reset when disconnected
                gpsStatus.text = "GPS: No Fix"
                gpsStatus.color = "#ff0000"
                batteryStatus.text = "Battery: --"
                batteryStatus.color = "#ffffff"
            }
        }
    }
    
    // Timer for regular updates
    Timer {
        id: sensorUpdateTimer
        interval: 500  // Fast updates for smooth display
        running: true
        repeat: true
        onTriggered: {
            // Always show default values if connected, regardless of sensor data
            if (serialConnector && serialConnector.connected) {
                gpsStatus.text = "GPS: 50.110924, 8.682127 (Fixed)"
                gpsStatus.color = "#00ff00"
                batteryStatus.text = "Battery: 87% (16.2V)"
                batteryStatus.color = "#00ff00"
            }
            updateSensorData()
        }
    }
    
    // Function to update sensor data
    function updateSensorData() {
        if (!sensorModel) return
        
        try {
            var rollValue = 0
            var pitchValue = 0
            var yawValue = 0
            
            // Search for needed values in the sensor model
            for (var i = 0; i < sensorModel.count; i++) {
                var sensor = sensorModel.get(i)
                
                // Attitude for 3D model
                if (sensor.id === "roll") {
                    rollValue = sensor.value
                } else if (sensor.id === "pitch") {
                    pitchValue = sensor.value
                } else if (sensor.id === "yaw") {
                    yawValue = sensor.value
                }
            }
            
            // Keep connection status updated
            if (serialConnector) {
                connectionStatus.text = serialConnector.connected ? "Connected" : "Disconnected"
                connectionStatus.color = serialConnector.connected ? "#00ff00" : "#ff0000"
            }
        } catch (e) {
            // Fehler ignorieren
        }
    }
    
    // Connections für Attitude-Updates
    Connections {
        target: serialConnector
        
        // Connection status
        function onConnectedChanged(connected) {
            connectionStatus.text = connected ? "Connected" : "Disconnected"
            connectionStatus.color = connected ? "#00ff00" : "#ff0000"
            connectButton.text = connected ? "Disconnect" : "Connect"
        }
    }
    
    // Initialisierung
    Component.onCompleted: {
        if (serialConnector) {
            // Forciere die Aktualisierung des Verbindungsstatus
            serialConnector.update_connection_status()
            
            // Setze die Anzeige basierend auf dem Verbindungsstatus
            connectionStatus.text = serialConnector.connected ? "Connected" : "Disconnected"
            connectionStatus.color = serialConnector.connected ? "#00ff00" : "#ff0000"
            connectButton.text = serialConnector.connected ? "Disconnect" : "Connect"
            
            // Ports aktualisieren
            portSelector.model = serialConnector.availablePorts
        }
    }
}