/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15

// ArduPilot Preflight View for MAVLink Integration
Item {
    id: preflightView
    width: parent.width
    height: parent.height

    // Timer für UI-Updates
    Timer {
        interval: 500
        running: true
        repeat: true
        onTriggered: {
            // Canvas-Updates für Gauges und Charts
            if (batteryGauge) batteryGauge.requestPaint()
            if (gpsGauge) gpsGauge.requestPaint()
            if (compassGauge) compassGauge.requestPaint()
            if (accelGauge) accelGauge.requestPaint()
        }
    }

    // Dunkler Hintergrund passend zur bestehenden UI
    Rectangle {
        id: background
        anchors.fill: parent
        color: "#10181c"  // Dunkles Blau/Schwarz passend zur bestehenden UI
        z: -1
    }

    // Hauptlayout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        // Kopfzeile
        Rectangle {
            id: headerRect
            Layout.fillWidth: true
            height: 50
            color: "#182328"
            radius: 8
            border.color: "#23343b"
            border.width: 2

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 16

                // Titel
                Text {
                    text: "ArduPilot Preflight Checks"
                    color: "#e6faff"
                    font.pixelSize: 22
                    font.bold: true
                }

                // Verbindungsstatus
                Rectangle {
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    width: 120
                    height: 30
                    radius: 4
                    color: serialConnector.isConnected ? "#1a5c36" : "#5c1a1a"
                    
                    Text {
                        anchors.centerIn: parent
                        text: serialConnector.isConnected ? "CONNECTED" : "DISCONNECTED"
                        color: "#ffffff"
                        font.pixelSize: 14
                        font.bold: true
                    }
                }
            }
        }

        // Hauptinhalt - Grid Layout für alle Komponenten
        GridLayout {
            id: mainContent
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: 3
            rowSpacing: 16
            columnSpacing: 16
            
            // System Status Panel (Spalte 0-1, Zeile 0)
            Rectangle {
                id: systemStatusPanel
                Layout.row: 0
                Layout.column: 0
                Layout.columnSpan: 2
                Layout.fillWidth: true
                height: 120
                color: "#182328"
                radius: 8
                border.color: "#23343b"
                border.width: 2
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 24
                    
                    // System Info Column
                    ColumnLayout {
                        Layout.fillHeight: true
                        spacing: 8
                        
                        Text {
                            text: "SYSTEM STATUS"
                            color: "#7ee6ff"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        
                        // ArduPilot Version
                        Row {
                            spacing: 8
                            Text { 
                                text: "Firmware:" 
                                color: "#e6faff"
                                font.pixelSize: 14
                            }
                            Text { 
                                // Bind to firmware version from SerialConnector/MAVLink
                                text: firmwareViewModel ? firmwareViewModel.firmwareVersion : "Unknown"
                                color: "#ffffff"
                                font.pixelSize: 14
                                font.bold: true 
                            }
                        }
                        
                        // Frame Type
                        Row {
                            spacing: 8
                            Text { 
                                text: "Frame Type:" 
                                color: "#e6faff"
                                font.pixelSize: 14
                            }
                            Text { 
                                // This would come from MAVLink HEARTBEAT message
                                text: {
                                    // Get frame type if available in sensorModel
                                    var frameSensor = sensorModel.findSensorByName("frame_type");
                                    if (frameSensor && frameSensor.value) {
                                        return frameSensor.value;
                                    }
                                    return "Quadcopter"; // Default value
                                }
                                color: "#ffffff"
                                font.pixelSize: 14
                                font.bold: true 
                            }
                        }
                    }
                    
                    // System Health
                    ColumnLayout {
                        Layout.fillHeight: true
                        spacing: 8
                        
                        Text {
                            text: "HEALTH"
                            color: "#7ee6ff"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        
                        // Status Text
                        Row {
                            spacing: 8
                            Rectangle {
                                width: 12
                                height: 12
                                radius: 6
                                // Color based on connection status
                                color: serialConnector.isConnected ? "#50C878" : "#FF5733"
                            }
                            Text { 
                                text: serialConnector.isConnected ? "System Ready" : "Not Connected"
                                color: "#ffffff"
                                font.pixelSize: 14
                                font.bold: true 
                            }
                        }
                        
                        // Mode
                        Row {
                            spacing: 8
                            Text { 
                                text: "Mode:" 
                                color: "#e6faff"
                                font.pixelSize: 14
                            }
                            Text { 
                                // This would come from MAVLink HEARTBEAT message
                                text: {
                                    var modeSensor = sensorModel.findSensorByName("flight_mode");
                                    return modeSensor ? modeSensor.value : "STABILIZE";
                                }
                                color: "#ffffff"
                                font.pixelSize: 14
                                font.bold: true 
                            }
                        }
                    }
                    
                    // Armed Status
                    ColumnLayout {
                        Layout.fillHeight: true
                        spacing: 8
                        
                        Text {
                            text: "STATUS"
                            color: "#7ee6ff"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        
                        // Armed Indicator
                        Rectangle {
                            width: 80
                            height: 30
                            radius: 4
                            // Color based on armed status
                            color: {
                                var armedSensor = sensorModel.findSensorByName("armed");
                                return (armedSensor && armedSensor.value) ? "#FF5733" : "#50C878";
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: {
                                    var armedSensor = sensorModel.findSensorByName("armed");
                                    return (armedSensor && armedSensor.value) ? "ARMED" : "DISARMED";
                                }
                                color: "#ffffff"
                                font.pixelSize: 14
                                font.bold: true
                            }
                        }
                    }
                }
            }
            
            // Battery Status (Spalte 2, Zeile 0)
            Rectangle {
                id: batteryStatus
                Layout.row: 0
                Layout.column: 2
                Layout.fillWidth: true
                height: 120
                color: "#182328"
                radius: 8
                border.color: "#23343b"
                border.width: 2
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 20
                    
                    // Battery Gauge
                    Item {
                        width: 80
                        height: 80
                        Layout.alignment: Qt.AlignVCenter
                        
                        Canvas {
                            id: batteryGauge
                            anchors.fill: parent
                            property real batteryPercent: {
                                var battery = sensorModel.findSensorByName("battery_percentage");
                                return battery ? battery.value / 100.0 : 0.0;
                            }
                            
                            onPaint: {
                                var ctx = getContext("2d");
                                ctx.reset();
                                var w = width;
                                var h = height;
                                var centerX = w / 2;
                                var centerY = h / 2;
                                var radius = Math.min(w, h) / 2 - 5;
                                
                                // Hintergrund-Kreis
                                ctx.beginPath();
                                ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
                                ctx.strokeStyle = "#23343b";
                                ctx.lineWidth = 7;
                                ctx.stroke();
                                
                                // Battery Level
                                ctx.beginPath();
                                ctx.arc(centerX, centerY, radius, -Math.PI/2, -Math.PI/2 + 2*Math.PI*batteryPercent);
                                
                                // Color based on battery level
                                if (batteryPercent > 0.5) {
                                    ctx.strokeStyle = "#3ee6ff"; // Blue for good battery
                                } else if (batteryPercent > 0.25) {
                                    ctx.strokeStyle = "#ffb84b"; // Orange for medium battery
                                } else {
                                    ctx.strokeStyle = "#ff4b4b"; // Red for low battery
                                }
                                
                                ctx.lineWidth = 7;
                                ctx.stroke();
                            }
                        }
                        
                        Text {
                            anchors.centerIn: parent
                            text: {
                                var battery = sensorModel.findSensorByName("battery_percentage");
                                return battery ? Math.round(battery.value) + "%" : "--";
                            }
                            color: "#ffffff"
                            font.pixelSize: 18
                            font.bold: true
                        }
                    }
                    
                    // Battery Info
                    ColumnLayout {
                        spacing: 8
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        
                        Text {
                            text: "BATTERY"
                            color: "#7ee6ff"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        
                        // Voltage
                        Row {
                            spacing: 8
                            Text {
                                text: "Voltage:"
                                color: "#e6faff"
                                font.pixelSize: 14
                            }
                            Text {
                                text: {
                                    var voltage = sensorModel.findSensorByName("battery_voltage");
                                    return voltage ? voltage.value.toFixed(1) + "V" : "--V";
                                }
                                color: "#ffffff"
                                font.pixelSize: 14
                                font.bold: true
                            }
                        }
                        
                        // Current
                        Row {
                            spacing: 8
                            Text {
                                text: "Current:"
                                color: "#e6faff"
                                font.pixelSize: 14
                            }
                            Text {
                                text: {
                                    var current = sensorModel.findSensorByName("battery_current");
                                    return current ? current.value.toFixed(1) + "A" : "--A";
                                }
                                color: "#ffffff"
                                font.pixelSize: 14
                                font.bold: true
                            }
                        }
                    }
                }
            }
            
            // Sensor Status (Spalte 0, Zeile 1)
            Rectangle {
                id: sensorStatus
                Layout.row: 1
                Layout.column: 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#182328"
                radius: 8
                border.color: "#23343b"
                border.width: 2
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    
                    Text {
                        text: "SENSOR STATUS"
                        color: "#7ee6ff"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    
                    // Sensor Status Grid
                    GridLayout {
                        columns: 2
                        rowSpacing: 12
                        columnSpacing: 16
                        Layout.fillWidth: true
                        
                        // Helper function to create sensor status items
                        function createSensorItem(parent, sensorName, icon, displayName) {
                            var component = Qt.createComponent("SensorStatusItem.qml");
                            if (component.status === Component.Ready) {
                                var item = component.createObject(parent, {
                                    "sensorName": sensorName,
                                    "icon": icon,
                                    "displayName": displayName
                                });
                                return item;
                            }
                            return null;
                        }
                        
                        // Compass Status
                        Item {
                            Layout.fillWidth: true
                            height: 40
                            
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 12
                                
                                Rectangle {
                                    width: 36
                                    height: 36
                                    radius: 18
                                    color: "#2a3e46"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "\uf14e" // Compass icon (FontAwesome)
                                        font.family: "FontAwesome"
                                        font.pixelSize: 18
                                        color: "#7ee6ff"
                                    }
                                }
                                
                                Column {
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 4
                                    
                                    Text {
                                        text: "Compass"
                                        font.pixelSize: 14
                                        color: "#e6faff"
                                    }
                                    
                                    Row {
                                        spacing: 6
                                        
                                        // Status indicator
                                        Rectangle {
                                            width: 10
                                            height: 10
                                            radius: 5
                                            anchors.verticalCenter: parent.verticalCenter
                                            color: {
                                                var compass = sensorModel.findSensorByName("compass_calibrated");
                                                if (compass && compass.value) {
                                                    return "#50C878"; // Green for calibrated
                                                } else {
                                                    return "#FF5733"; // Red for not calibrated
                                                }
                                            }
                                        }
                                        
                                        Text {
                                            text: {
                                                var compass = sensorModel.findSensorByName("compass_calibrated");
                                                if (compass && compass.value) {
                                                    return "Calibrated";
                                                } else {
                                                    return "Not Calibrated";
                                                }
                                            }
                                            font.pixelSize: 12
                                            color: "#ffffff"
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Accelerometer Status
                        Item {
                            Layout.fillWidth: true
                            height: 40
                            
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 12
                                
                                Rectangle {
                                    width: 36
                                    height: 36
                                    radius: 18
                                    color: "#2a3e46"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "\uf135" // Rocket icon (FontAwesome)
                                        font.family: "FontAwesome"
                                        font.pixelSize: 18
                                        color: "#7ee6ff"
                                    }
                                }
                                
                                Column {
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 4
                                    
                                    Text {
                                        text: "Accelerometer"
                                        font.pixelSize: 14
                                        color: "#e6faff"
                                    }
                                    
                                    Row {
                                        spacing: 6
                                        
                                        // Status indicator
                                        Rectangle {
                                            width: 10
                                            height: 10
                                            radius: 5
                                            anchors.verticalCenter: parent.verticalCenter
                                            color: {
                                                var accel = sensorModel.findSensorByName("accel_calibrated");
                                                if (accel && accel.value) {
                                                    return "#50C878"; // Green for calibrated
                                                } else {
                                                    return "#FF5733"; // Red for not calibrated
                                                }
                                            }
                                        }
                                        
                                        Text {
                                            text: {
                                                var accel = sensorModel.findSensorByName("accel_calibrated");
                                                if (accel && accel.value) {
                                                    return "Calibrated";
                                                } else {
                                                    return "Not Calibrated";
                                                }
                                            }
                                            font.pixelSize: 12
                                            color: "#ffffff"
                                        }
                                    }
                                }
                            }
                        }
                        
                        // GPS Status
                        Item {
                            Layout.fillWidth: true
                            height: 40
                            
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 12
                                
                                Rectangle {
                                    width: 36
                                    height: 36
                                    radius: 18
                                    color: "#2a3e46"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "\uf124" // Location marker icon (FontAwesome)
                                        font.family: "FontAwesome"
                                        font.pixelSize: 18
                                        color: "#7ee6ff"
                                    }
                                }
                                
                                Column {
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 4
                                    
                                    Text {
                                        text: "GPS"
                                        font.pixelSize: 14
                                        color: "#e6faff"
                                    }
                                    
                                    Row {
                                        spacing: 6
                                        
                                        // Status indicator
                                        Rectangle {
                                            width: 10
                                            height: 10
                                            radius: 5
                                            anchors.verticalCenter: parent.verticalCenter
                                            color: {
                                                var fixType = sensorModel.findSensorByName("gps_fix_type");
                                                // 3D fix is typically 3 or higher
                                                if (fixType && fixType.value >= 3) {
                                                    return "#50C878"; // Green for 3D fix
                                                } else if (fixType && fixType.value > 0) {
                                                    return "#ffb84b"; // Yellow for 2D fix
                                                } else {
                                                    return "#FF5733"; // Red for no fix
                                                }
                                            }
                                        }
                                        
                                        Text {
                                            text: {
                                                var fixType = sensorModel.findSensorByName("gps_fix_type");
                                                var numSats = sensorModel.findSensorByName("gps_num_sats");
                                                var satsText = numSats ? numSats.value + " Sats, " : "";
                                                
                                                if (fixType) {
                                                    if (fixType.value >= 3) {
                                                        return satsText + "3D Fix";
                                                    } else if (fixType.value == 2) {
                                                        return satsText + "2D Fix";
                                                    } else if (fixType.value == 1) {
                                                        return satsText + "No Fix";
                                                    }
                                                }
                                                return "No Fix";
                                            }
                                            font.pixelSize: 12
                                            color: "#ffffff"
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Barometer Status
                        Item {
                            Layout.fillWidth: true
                            height: 40
                            
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 12
                                
                                Rectangle {
                                    width: 36
                                    height: 36
                                    radius: 18
                                    color: "#2a3e46"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "\uf043" // Tint/drop icon (FontAwesome)
                                        font.family: "FontAwesome"
                                        font.pixelSize: 18
                                        color: "#7ee6ff"
                                    }
                                }
                                
                                Column {
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 4
                                    
                                    Text {
                                        text: "Barometer"
                                        font.pixelSize: 14
                                        color: "#e6faff"
                                    }
                                    
                                    Row {
                                        spacing: 6
                                        
                                        // Status indicator
                                        Rectangle {
                                            width: 10
                                            height: 10
                                            radius: 5
                                            anchors.verticalCenter: parent.verticalCenter
                                            color: {
                                                var baro = sensorModel.findSensorByName("baro_health");
                                                if (baro && baro.value) {
                                                    return "#50C878"; // Green for healthy
                                                } else {
                                                    return "#FF5733"; // Red for unhealthy
                                                }
                                            }
                                        }
                                        
                                        Text {
                                            text: {
                                                var baro = sensorModel.findSensorByName("baro_health");
                                                if (baro && baro.value) {
                                                    return "Healthy";
                                                } else {
                                                    return "Unhealthy";
                                                }
                                            }
                                            font.pixelSize: 12
                                            color: "#ffffff"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // PreArm Checks (Spalte 1, Zeile 1)
            Rectangle {
                id: preArmChecks
                Layout.row: 1
                Layout.column: 1
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#182328"
                radius: 8
                border.color: "#23343b"
                border.width: 2
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    
                    Row {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Text {
                            text: "PREARM CHECKS"
                            color: "#7ee6ff"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        
                        Rectangle {
                            width: 10
                            height: 10
                            radius: 5
                            anchors.verticalCenter: parent.verticalCenter
                            // Color based on prearm check status from sensorModel
                            color: {
                                var prearmCheck = sensorModel.findSensorByName("prearm_check_status");
                                if (prearmCheck && prearmCheck.value === "pass") {
                                    return "#50C878"; // Green for pass
                                } else {
                                    return "#FF5733"; // Red for fail
                                }
                            }
                        }
                        
                        Text {
                            text: {
                                var prearmCheck = sensorModel.findSensorByName("prearm_check_status");
                                if (prearmCheck && prearmCheck.value === "pass") {
                                    return "All Passed";
                                } else {
                                    return "Issues Found";
                                }
                            }
                            color: "#ffffff"
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                    
                    // Scroll area for PreArm check messages
                    ScrollView {
                        id: prearmScrollView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        ScrollBar.vertical.policy: ScrollBar.AsNeeded
                        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                        
                        ListView {
                            id: prearmMessageList
                            anchors.fill: parent
                            model: serialConnector.prearmMessages ? serialConnector.prearmMessages : []
                            delegate: Rectangle {
                                width: prearmScrollView.width
                                height: messageText.implicitHeight + 20
                                color: {
                                    if (modelData.severity === "critical" || modelData.text.toLowerCase().includes("fail")) {
                                        return "#402224"; // Dark red background for critical/fail messages
                                    } else if (modelData.severity === "warning" || modelData.text.toLowerCase().includes("warn")) {
                                        return "#403a22"; // Dark yellow background for warnings
                                    } else {
                                        return "#233a24"; // Dark green background for passed checks
                                    }
                                }
                                radius: 4
                                border.width: 1
                                border.color: {
                                    if (modelData.severity === "critical" || modelData.text.toLowerCase().includes("fail")) {
                                        return "#ff5733"; // Red border for critical/fail
                                    } else if (modelData.severity === "warning" || modelData.text.toLowerCase().includes("warn")) {
                                        return "#ffb84b"; // Yellow border for warning
                                    } else {
                                        return "#50c878"; // Green border for pass
                                    }
                                }
                                margin: 4
                                
                                Text {
                                    id: messageText
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    text: {
                                        if (modelData.timestamp) {
                                            return modelData.timestamp + ": " + modelData.text;
                                        } else {
                                            return modelData.text || modelData;
                                        }
                                    }
                                    font.pixelSize: 14
                                    color: "#ffffff"
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                        
                        // Fallback for empty list
                        Text {
                            anchors.centerIn: parent
                            text: "No PreArm Check Data Available"
                            visible: !serialConnector.prearmMessages || serialConnector.prearmMessages.length === 0
                            color: "#e6faff"
                            font.pixelSize: 14
                            font.italic: true
                        }
                    }
                    
                    // Status of PreArm Check
                    Row {
                        Layout.fillWidth: true
                        spacing: 8
                        
                        Rectangle {
                            width: 18
                            height: 18
                            color: "transparent"
                            border.width: 1
                            border.color: "#e6faff"
                            radius: 2
                            
                            Text {
                                anchors.centerIn: parent
                                text: "\uf00c" // Check mark icon (FontAwesome)
                                font.family: "FontAwesome"
                                color: "#50C878"
                                font.pixelSize: 12
                                visible: {
                                    var prearmCheck = sensorModel.findSensorByName("prearm_check_status");
                                    return prearmCheck && prearmCheck.value === "pass";
                                }
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: "\uf00d" // X mark icon (FontAwesome)
                                font.family: "FontAwesome"
                                color: "#FF5733"
                                font.pixelSize: 12
                                visible: {
                                    var prearmCheck = sensorModel.findSensorByName("prearm_check_status");
                                    return !prearmCheck || prearmCheck.value !== "pass";
                                }
                            }
                        }
                        
                        Text {
                            text: {
                                var prearmCheck = sensorModel.findSensorByName("prearm_check_status");
                                if (prearmCheck && prearmCheck.value === "pass") {
                                    return "Ready to Arm";
                                } else {
                                    return "Not Ready - Check Messages";
                                }
                            }
                            color: {
                                var prearmCheck = sensorModel.findSensorByName("prearm_check_status");
                                if (prearmCheck && prearmCheck.value === "pass") {
                                    return "#50C878"; // Green for pass
                                } else {
                                    return "#FF5733"; // Red for fail
                                }
                            }
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                }
            }
            
            // Log Section (Spalte 2, Zeile 1)
            Rectangle {
                id: logSection
                Layout.row: 1
                Layout.column: 2
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#182328"
                radius: 8
                border.color: "#23343b"
                border.width: 2
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    
                    Text {
                        text: "SYSTEM INFORMATION"
                        color: "#7ee6ff"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    
                    // Filtered Log View - 30% of height instead of 10% as per memory note
                    ScrollView {
                        id: logScrollView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        ScrollBar.vertical.policy: ScrollBar.AsNeeded
                        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                        
                        ListView {
                            id: filteredLogList
                            anchors.fill: parent
                            model: filterSystemInfo(serialConnector.logMessages || [])
                            
                            // Function to filter system information logs
                            function filterSystemInfo(messages) {
                                if (!messages || messages.length === 0) return [];
                                
                                // Filter for specific system information keys as per memory
                                var filtered = [];
                                var keyPhrases = [
                                    "frame-type", 
                                    "rcout", 
                                    "microair743", 
                                    "chibios", 
                                    "arducopter",
                                    "version",
                                    "prearm",
                                    "arm",
                                    "mode",
                                    "system",
                                    "init",
                                    "ready"
                                ];
                                
                                for (var i = 0; i < messages.length; i++) {
                                    var msg = messages[i];
                                    var text = msg.text ? msg.text.toLowerCase() : 
                                              (typeof msg === 'string' ? msg.toLowerCase() : "");
                                    
                                    // Check if message contains any of the key phrases
                                    for (var j = 0; j < keyPhrases.length; j++) {
                                        if (text.includes(keyPhrases[j])) {
                                            filtered.push(msg);
                                            break;
                                        }
                                    }
                                }
                                
                                return filtered;
                            }
                            
                            delegate: Rectangle {
                                width: filteredLogList.width
                                height: logText.implicitHeight + 20
                                color: {
                                    // Colorize based on content
                                    var text = (modelData.text || modelData).toLowerCase();
                                    if (text.includes("error") || text.includes("fail")) {
                                        return "#402224"; // Dark red background
                                    } else if (text.includes("warn")) {
                                        return "#403a22"; // Dark yellow background
                                    } else if (text.includes("init") || text.includes("ready")) {
                                        return "#233a24"; // Dark green background
                                    } else {
                                        return "#233242"; // Dark blue background for info
                                    }
                                }
                                radius: 4
                                border.width: 1
                                border.color: "#3a5a66"
                                margin: 4
                                
                                Text {
                                    id: logText
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    text: {
                                        if (modelData.timestamp) {
                                            return modelData.timestamp + ": " + modelData.text;
                                        } else {
                                            return modelData.text || modelData;
                                        }
                                    }
                                    // Using larger font (16px) with bold for better readability as per memory
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: "#ffffff"
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                        
                        // Fallback for empty list
                        Text {
                            anchors.centerIn: parent
                            text: "No System Information Available\nConnect to Flight Controller"
                            visible: filteredLogList.model.length === 0
                            color: "#e6faff"
                            font.pixelSize: 16
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                    
                    // Quick summary text
                    Text {
                        text: "System logs filtered for important information"
                        color: "#7e8a8d"
                        font.pixelSize: 12
                        font.italic: true
                        Layout.fillWidth: true
                    }
                }
            }
        }
    }
}
