import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: window
    width: 800
    height: 600
    visible: true
    title: "Minimaler MAVSDK MVVM Test"
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 10
        
        Text {
            text: "MAVSDK MVVM Verbindungstest"
            font.pixelSize: 24
            font.bold: true
            Layout.fillWidth: true
        }
        
        Rectangle {
            Layout.fillWidth: true
            height: 2
            color: "#cccccc"
        }
        
        GridLayout {
            columns: 2
            Layout.fillWidth: true
            columnSpacing: 10
            rowSpacing: 10
            
            Text { text: "COM-Port:" }
            TextField {
                id: portField
                text: "COM8"
                Layout.fillWidth: true
                placeholderText: "z.B. COM8 oder COM8:115200"
            }
            
            Text { text: "Verbindungsstatus:" }
            Text {
                id: connectionStatus
                text: serialConnector.connected ? "Verbunden" : "Nicht verbunden"
                color: serialConnector.connected ? "green" : "red"
                font.bold: true
            }
            
            Button {
                text: serialConnector.connected ? "Trennen" : "Verbinden"
                Layout.columnSpan: 2
                Layout.fillWidth: true
                onClicked: {
                    if (serialConnector.connected) {
                        serialConnector.disconnectDrone();
                    } else {
                        // Versuche zuerst connectToDrone und falle auf connect zurück
                        try {
                            if (typeof serialConnector.connectToDrone === "function") {
                                serialConnector.connectToDrone(portField.text);
                            } else {
                                serialConnector.connect(portField.text);
                            }
                        } catch (e) {
                            console.error("Verbindungsfehler:", e);
                        }
                    }
                }
            }
        }
        
        Rectangle {
            Layout.fillWidth: true
            height: 2
            color: "#cccccc"
            Layout.topMargin: 10
        }
        
        Text {
            text: "Telemetrie-Daten:"
            font.pixelSize: 18
            font.bold: true
        }
        
        GridLayout {
            columns: 2
            Layout.fillWidth: true
            columnSpacing: 10
            rowSpacing: 5
            
            Text { text: "Position:" }
            Text { 
                id: positionText 
                text: "Warte auf Daten..."
                Connections {
                    target: serialConnector
                    function onPositionChanged(position) {
                        if (position && typeof position === 'object' && 'latitude_deg' in position) {
                            positionText.text = "Lat: " + position.latitude_deg.toFixed(6) + 
                                              ", Lon: " + position.longitude_deg.toFixed(6) + 
                                              ", Alt: " + position.absolute_altitude_m.toFixed(1) + "m";
                        } else {
                            positionText.text = "Positionsdaten nicht verfügbar";
                        }
                    }
                }
            }
            
            Text { text: "Batterie:" }
            Text { 
                id: batteryText 
                text: "Warte auf Daten..."
                Connections {
                    target: serialConnector
                    function onBatteryChanged(battery) {
                        if (battery && typeof battery === 'object' && 'remaining_percent' in battery) {
                            batteryText.text = (battery.remaining_percent * 100).toFixed(1) + "%, " + 
                                             battery.voltage_v.toFixed(2) + "V";
                            if ('current_a' in battery) {
                                batteryText.text += ", " + battery.current_a.toFixed(1) + "A";
                            }
                        } else {
                            batteryText.text = "Batteriedaten nicht verfügbar";
                        }
                    }
                }
            }
            
            Text { text: "GPS:" }
            Text { 
                id: gpsText 
                text: "Warte auf Daten..."
                Connections {
                    target: serialConnector
                    function onGpsInfoChanged(gps) {
                        if (gps && typeof gps === 'object' && 'num_satellites' in gps) {
                            gpsText.text = "Satelliten: " + gps.num_satellites;
                            if ('fix_type' in gps) {
                                gpsText.text += ", Fix: " + gps.fix_type;
                            }
                        } else {
                            gpsText.text = "GPS-Daten nicht verfügbar";
                        }
                    }
                }
            }
            
            Text { text: "Gesundheit:" }
            Text { 
                id: healthText 
                text: "Warte auf Daten..."
                Connections {
                    target: serialConnector
                    function onHealthChanged(health) {
                        if (health && typeof health === 'object') {
                            var healthInfo = [];
                            if ('is_gyrometer_calibration_ok' in health) {
                                healthInfo.push("Gyro: " + (health.is_gyrometer_calibration_ok ? "OK" : "Kalibrieren"));
                            }
                            if ('is_accelerometer_calibration_ok' in health) {
                                healthInfo.push("Accel: " + (health.is_accelerometer_calibration_ok ? "OK" : "Kalibrieren"));
                            }
                            if ('is_magnetometer_calibration_ok' in health) {
                                healthInfo.push("Mag: " + (health.is_magnetometer_calibration_ok ? "OK" : "Kalibrieren"));
                            }
                            if ('is_local_position_ok' in health) {
                                healthInfo.push("Position: " + (health.is_local_position_ok ? "OK" : "Ungenau"));
                            }
                            
                            healthText.text = healthInfo.join(", ");
                        } else {
                            healthText.text = "Gesundheitsdaten nicht verfügbar";
                        }
                    }
                }
            }
        }
        
        Rectangle {
            Layout.fillWidth: true
            height: 2
            color: "#cccccc"
            Layout.topMargin: 10
        }
        
        Text {
            text: "Log-Nachrichten:"
            font.pixelSize: 18
            font.bold: true
        }
        
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            border.color: "#cccccc"
            border.width: 1
            
            ScrollView {
                anchors.fill: parent
                anchors.margins: 5
                clip: true
                
                TextArea {
                    id: logArea
                    readOnly: true
                    text: ""
                    wrapMode: TextEdit.Wrap
                    
                    // Logger-Verbindung direkt mit dem serialConnector
                    Connections {
                        target: serialConnector
                        function onFcImportantMessageReceived(message) {
                            logArea.append("[FC] " + message);
                        }
                    }
                    
                    Connections {
                        target: serialConnector
                        function onFcImportantMessageReceived(message) {
                            logArea.append("[FC MESSAGE] " + message);
                        }
                    }
                }
            }
        }
    }
}
