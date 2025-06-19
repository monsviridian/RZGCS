import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtLocation 5.15
import QtPositioning 5.15
import "Components"
import "./" as Content
import "Components" as Components

/**
 * MissionPlannerView - Main view that mimics ArduPilot Mission Planner interface
 * Integrates map, artificial horizon and telemetry panels
 */
Item {
    id: root
    
    // Properties
    property var currentTelemetry: ({})  // Telemetry data
    
    // Debug the available context properties when loaded
    function debugAvailableProperties() {
        console.log("MissionPlannerView debugging context properties:");
        if (typeof missionPlannerStyle !== 'undefined' && missionPlannerStyle) {
            console.log("  - missionPlannerStyle is available!", missionPlannerStyle);
        } else {
            console.error("  - missionPlannerStyle is NOT available!");
        }
    }
    
    // Auto-connect timer - deaktiviert für manuellen Start
    Timer {
        id: autoConnectTimer
        interval: 2000
        repeat: false
        running: false // Deaktiviert, damit keine automatische Verbindung hergestellt wird
        onTriggered: {
            console.log("Manual connect is being executed");
            if (missionPlannerStyle && !missionPlannerStyle.connected) {
                console.log("Attempting to connect to SITL with:", connectionField.text);
                missionPlannerStyle.connect(connectionField.text);
            }
        }
    }
    
    // Component initialization
    Component.onCompleted: {
        console.log("MissionPlannerView loaded");
        
        // Call our debug function to check context properties
        debugAvailableProperties();
        
        // Nur Verfügbarkeit prüfen, aber nicht automatisch verbinden
        checkPropertyTimer.start();
        
        // Telemetry connectivity check
        console.log("Checking telemetryViewModel availability");
        if (typeof telemetryViewModel !== 'undefined' && telemetryViewModel) {
            console.log("SUCCESS: telemetryViewModel is available!");
            // Verbinde das TelemetryPanel mit dem Python-ViewModel
            telemetryConnection.targetPanel = telemetryDisplay;
            telemetryConnection.active = true;
        } else {
            console.error("WARNING: telemetryViewModel is NOT available!");
        }
    }
    
    // Timer to periodically check if the property is available
    Timer {
        id: checkPropertyTimer
        interval: 500
        repeat: true
        running: false
        property int retryCount: 0
        onTriggered: {
            retryCount++;
            console.log("Checking for missionPlannerStyle availability, attempt: " + retryCount);
            
            if (typeof missionPlannerStyle !== 'undefined' && missionPlannerStyle) {
                console.log("SUCCESS: missionPlannerStyle is now available!");
                checkPropertyTimer.stop();
                // Nicht mehr autoConnectTimer starten - manuelle Verbindung erwünscht
                // autoConnectTimer.start();
                statusBar.color = "#770000";
            } else if (retryCount > 10) {
                console.error("Failed to get missionPlannerStyle after 10 attempts, giving up");
                checkPropertyTimer.stop();
            }
        }
    }
    
    // Telemetry data update from backend
    Connections {
        target: missionPlannerStyle
        enabled: missionPlannerStyle !== null
        
        function onTelemetryUpdated(data) {
            // Log periodically but not every update to avoid console flooding
            if (Math.random() < 0.1) { // ~10% of updates
                console.log("Telemetry update received with keys:", Object.keys(data).join(", "));
                console.log("Sample values: lat=", data.latitude, "lon=", data.longitude, 
                          "alt=", data.altitude, "heading=", data.heading,
                          "battery=", data.battery_voltage, "wind=", data.wind_speed);
            }
            
            // Update our local telemetry object
            currentTelemetry = data;
            
            // Update map position and heading
            mapView.vehicleLat = data.latitude;
            mapView.vehicleLon = data.longitude;
            mapView.vehicleHeading = data.heading;
            
            // Update artificial horizon
            horizon.roll = data.roll;
            horizon.pitch = data.pitch;
            horizon.disarmed = !missionPlannerStyle.armed;
            
            // Update telemetry panel with all available data
            telemetryDisplay.altitude = data.relative_alt.toFixed(1);
            telemetryDisplay.groundSpeed = data.groundspeed.toFixed(1);
            telemetryDisplay.airSpeed = data.airspeed.toFixed(1);
            telemetryDisplay.verticalSpeed = data.vspeed.toFixed(1);
            telemetryDisplay.distToWP = data.wp_distance ? data.wp_distance.toFixed(1) : "--";
            telemetryDisplay.heading = Math.round(data.heading);
            telemetryDisplay.batteryPercent = Math.round(data.battery_remaining);
            telemetryDisplay.batteryVoltage = data.battery_voltage.toFixed(1);
            telemetryDisplay.batteryCurrent = data.battery_current.toFixed(1);
            telemetryDisplay.throttlePercent = Math.round(data.throttle);
            
            // Update environment panel
            if (environmentPanel) {
                environmentPanel.windSpeed = data.wind_speed ? data.wind_speed.toFixed(1) : "--";
                environmentPanel.windDirection = data.wind_direction ? Math.round(data.wind_direction) : "--";
                environmentPanel.turbulence = data.turbulence ? (data.turbulence * 100).toFixed(0) : "--";
                environmentPanel.temperature = data.temperature ? data.temperature.toFixed(1) : "--";
            }
            
            // Update mission information
            if (missionInfoDisplay) {
                missionInfoDisplay.currentWaypoint = data.current_wp;
                missionInfoDisplay.waypointCount = data.wp_count;
                missionInfoDisplay.distanceToWaypoint = data.wp_distance ? data.wp_distance.toFixed(1) : "--";
            }
        }
        
        function onVehicleConnected(connected) {
            mapView.isConnected = connected;
            
            // Update UI elements based on connection status
            if (connected) {
                statusBar.text = "Verbunden";
                statusBar.color = "#00FF00";
            } else {
                statusBar.text = "Nicht verbunden";
                statusBar.color = "#FF0000";
            }
        }
        
        function onArmStatusChanged(armed) {
            mapView.isArmed = armed;
        }
        
        function onModeChanged(mode) {
            modeSelector.currentIndex = modeSelector.find(mode);
            flightModeDisplay.text = mode;
        }
        
        function onStatusChanged(status) {
            statusMessage.text = status;
        }
    }
    
    // Top toolbar with connection controls
    Rectangle {
        id: topToolbar
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
        }
        height: 50
        color: "#202020"
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 5
            spacing: 10
            
            Label {
                text: "Verbindung:"
                color: "white"
            }
            
            Item { Layout.fillWidth: true }  // Spacer
            
            // Connection status
            Rectangle {
                id: statusBar
                Layout.preferredWidth: 120
                Layout.preferredHeight: 24
                radius: 4
                color: "#FF0000"  // Default to red (disconnected)
                
                Label {
                    anchors.centerIn: parent
                    text: "Nicht verbunden"
                    font.bold: true
                    color: "#FFFFFF"
                }
            }
            
            // Connection input
            TextField {
                id: connectionField
                Layout.preferredWidth: 200
                placeholderText: "tcp:localhost:5760"
                text: "tcp:localhost:5760"
            }
            
            // Connect button
            Button {
                text: missionPlannerStyle && missionPlannerStyle.connected ? "Trennen" : "Verbinden"
                Layout.preferredWidth: 100
                onClicked: {
                    console.log("Connection button clicked");
                    
                    // Use a try-catch to handle any QML/C++ boundary issues
                    try {
                        if (typeof missionPlannerStyle !== 'undefined' && missionPlannerStyle) {
                            if (missionPlannerStyle.connected) {
                                console.log("Disconnecting from SITL...");
                                missionPlannerStyle.disconnect();
                            } else {
                                const connString = connectionField.text;
                                console.log("Connecting to SITL with:", connString);
                                missionPlannerStyle.connect(connString);
                            }
                        } else {
                            console.error("ERROR: missionPlannerStyle is not available! Cannot connect.");
                            // Try to debug what's actually available in the root context
                            debugAvailableProperties();
                        }
                    } catch (e) {
                        console.error("Error during connection:", e);
                    }
                }
            }
        }
    }
    
    // Bottom status bar
    Rectangle {
        id: bottomStatusBar
        anchors {
            bottom: parent.bottom
            left: parent.left
            right: parent.right
        }
        height: 30
        color: "#222222"
        
        Label {
            id: statusMessage
            anchors.fill: parent
            anchors.margins: 5
            text: "Bereit"
            color: "#FFFFFF"
            font.pixelSize: 12
        }
    }
    
    // Main content area
    RowLayout {
        anchors {
            top: topToolbar.bottom
            bottom: bottomStatusBar.top
            left: parent.left
            right: parent.right
        }
        spacing: 0
        
        // Left side panel with HUD and telemetry
        Rectangle {
            Layout.preferredWidth: 300
            Layout.fillHeight: true
            color: "#222222"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                // Flight mode display
                Rectangle {
                    Layout.fillWidth: true
                    height: 40
                    color: "#555555"
                    radius: 4
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        
                        Label {
                            text: "Flight Mode:"
                            color: "white"
                            font.pixelSize: 14
                        }
                        
                        Label {
                            id: flightModeDisplay
                            text: "STABILIZE"
                            color: "#FFFF00"
                            font.bold: true
                            font.pixelSize: 16
                        }
                        
                        Item { Layout.fillWidth: true }  // Spacer
                        
                        ComboBox {
                            id: modeSelector
                            Layout.preferredWidth: 120
                            model: missionPlannerStyle ? missionPlannerStyle.getSupportedModes(missionPlannerStyle.vehicleType) : []
                            onActivated: {
                                if (missionPlannerStyle) {
                                    missionPlannerStyle.setMode(currentText);
                                }
                            }
                        }
                    }
                }
                
                // Artificial horizon
                ArtificialHorizon {
                    id: horizon
                    Layout.fillWidth: true
                    Layout.preferredHeight: width
                }
                
                // Arm/Disarm buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    
                    Button {
                        text: "ARM"
                        Layout.fillWidth: true
                        enabled: missionPlannerStyle && missionPlannerStyle.connected && !missionPlannerStyle.armed
                        highlighted: true
                        onClicked: {
                            if (missionPlannerStyle) {
                                missionPlannerStyle.arm();
                            }
                        }
                    }
                    
                    Button {
                        text: "DISARM"
                        Layout.fillWidth: true
                        enabled: missionPlannerStyle && missionPlannerStyle.connected && missionPlannerStyle.armed
                        highlighted: true
                        onClicked: {
                            if (missionPlannerStyle) {
                                missionPlannerStyle.disarm();
                            }
                        }
                    }
                }
                
                // Telemetry panel
                TelemetryPanel {
                    id: telemetryDisplay
                    Layout.fillWidth: true
                    Layout.preferredHeight: 180
                }
                
                // Telemetry Connection Component to bridge Python and QML
                Components.TelemetryConnection {
                    id: telemetryConnection
                    targetPanel: telemetryDisplay
                    active: true
                }
                
                // Environment panel
                EnvironmentPanel {
                    id: environmentPanel
                    Layout.fillWidth: true
                    Layout.preferredHeight: 160
                }
                
                // Mission info display
                MissionInfoDisplay {
                    id: missionInfoDisplay
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120
                }
            }
        }
        
        // Right side with map view
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#111111"
            
            // Verwende die Warzone-ähnliche Kartenansicht
            WarzoneFlightView {
                id: mapView
                anchors.fill: parent
                
                // Verbinde Drohneneigenschaften
                droneLatitude: 50.110924
                droneLongitude: 8.682127
                droneAltitude: missionPlannerStyle && missionPlannerStyle.connected ? 100.0 : 0
                droneHeading: 45.0
                
                // Wegpunkt-Modus
                property bool waypointMode: false
                property int waypointCount: 0
                
                // Wegpunkt-Funktionen für die Kompatibilität mit den bestehenden Steuerelementen
                function centerOnVehicle() {
                    followDrone = true
                }
                
                function centerOnHome() {
                    // Position auf die Home-Position setzen (Frankfurt)
                    followDrone = false
                }
                
                function clearWaypoints() {
                    // Waypoint löschen (wird direkt in der View angezeigt)
                    if (missionPlannerStyle) {
                        console.log("Lösche alle Wegpunkte")
                        waypointCount = 0
                    }
                }
                
                function addNewWaypoint(lat, lon, alt) {
                    console.log("Wegpunkt hinzugefügt bei: " + lat + ", " + lon + ", Höhe: " + alt)
                    waypointCount++
                }
                
                // Signale aus der Map verarbeiten
                onMapClicked: {
                    if (waypointMode && missionPlannerStyle && missionPlannerStyle.connected) {
                        addNewWaypoint(lat, lon, 50)  // Standard-Höhe: 50m
                        statusMessage.text = "Wegpunkt hinzugefügt: " + lat.toFixed(6) + ", " + lon.toFixed(6)
                    }
                }
            }
            
            // Map controls
            Column {
                anchors {
                    right: parent.right
                    top: parent.top
                    margins: 10
                }
                spacing: 5
                
                Button {
                    text: "Zentrieren"
                    width: 140
                    onClicked: mapView.centerOnVehicle()
                }
                
                Button {
                    text: "Home"
                    width: 140
                    onClicked: mapView.centerOnHome()
                }
                
                Button {
                    text: "Wegpunkt setzen"
                    width: 140
                    enabled: missionPlannerStyle && missionPlannerStyle.connected
                    onClicked: {
                        // Wegpunkt-Modus aktivieren/deaktivieren
                        mapView.waypointMode = !mapView.waypointMode;
                        if (mapView.waypointMode) {
                            // Visuelles Feedback für aktiven Modus
                            color = "#22AA22"
                        } else {
                            color = Button.background
                        }
                    }
                    // Tooltip für Erklärung
                    ToolTip.visible: hovered
                    ToolTip.text: "Aktivieren Sie diesen Modus und klicken Sie dann auf die Karte, um Wegpunkte zu setzen."
                }
                
                Button {
                    text: "Wegpunkte löschen"
                    width: 140
                    onClicked: mapView.clearWaypoints()
                }
                
                // Trennlinie
                Rectangle {
                    width: 140
                    height: 1
                    color: "#555555"
                }
                
                // Abstandshalter
                Item {
                    width: 140
                    height: 10
                }
                
                // Navigationssteuerungen
                Button {
                    text: "Starten"
                    width: 140
                    enabled: missionPlannerStyle && missionPlannerStyle.connected && missionPlannerStyle.armed
                    highlighted: true
                    onClicked: {
                        if (missionPlannerStyle) {
                            missionPlannerStyle.takeoff(10); // 10 Meter Höhe
                            statusMessage.text = "Starte auf 10m Höhe..."
                        }
                    }
                }
                
                Button {
                    text: "Landen"
                    width: 140
                    enabled: missionPlannerStyle && missionPlannerStyle.connected
                    highlighted: true
                    onClicked: {
                        if (missionPlannerStyle) {
                            missionPlannerStyle.land();
                            statusMessage.text = "Landung eingeleitet..."
                        }
                    }
                }
                
                Button {
                    text: "RTL (Heimkehr)"
                    width: 140
                    enabled: missionPlannerStyle && missionPlannerStyle.connected
                    highlighted: true
                    onClicked: {
                        if (missionPlannerStyle) {
                            missionPlannerStyle.returnToLaunch();
                            statusMessage.text = "RTL aktiviert - Kehre zum Startpunkt zurück"
                        }
                    }
                }
                
                Button {
                    text: "Mission starten"
                    width: 140
                    enabled: missionPlannerStyle && missionPlannerStyle.connected && mapView.waypointCount > 0
                    highlighted: true
                    onClicked: {
                        if (missionPlannerStyle) {
                            missionPlannerStyle.startMission();
                            statusMessage.text = "Mission gestartet"
                        }
                    }
                }
            }
        }
    }
    
    // Vehicle type selector at bottom
    Rectangle {
        id: vehicleSelector
        anchors {
            bottom: bottomStatusBar.top
            horizontalCenter: parent.horizontalCenter
        }
        width: 400
        height: 80
        color: "#333333"
        radius: 8
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 10
            
            // Quadcopter button
            Button {
                Layout.fillWidth: true
                Layout.fillHeight: true
                text: "Multicopter"
                highlighted: missionPlannerStyle && missionPlannerStyle.vehicleType === "copter"
                onClicked: {
                    if (missionPlannerStyle) {
                        missionPlannerStyle.setVehicleType("copter");
                    }
                }
            }
            
            // Plane button
            Button {
                Layout.fillWidth: true
                Layout.fillHeight: true
                text: "Plane"
                highlighted: missionPlannerStyle && missionPlannerStyle.vehicleType === "plane"
                onClicked: {
                    if (missionPlannerStyle) {
                        missionPlannerStyle.setVehicleType("plane");
                    }
                }
            }
            
            // Rover button
            Button {
                Layout.fillWidth: true
                Layout.fillHeight: true
                text: "Rover"
                highlighted: missionPlannerStyle && missionPlannerStyle.vehicleType === "rover"
                onClicked: {
                    if (missionPlannerStyle) {
                        missionPlannerStyle.setVehicleType("rover");
                    }
                }
            }
            
            // Helicopter button
            Button {
                Layout.fillWidth: true
                Layout.fillHeight: true
                text: "Helicopter"
                highlighted: missionPlannerStyle && missionPlannerStyle.vehicleType === "heli"
                onClicked: {
                    if (missionPlannerStyle) {
                        missionPlannerStyle.setVehicleType("heli");
                    }
                }
            }
        }
    }
}
