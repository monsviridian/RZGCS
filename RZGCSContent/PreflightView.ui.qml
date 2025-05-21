/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick3D 6.8
import QtQuick3D.Helpers 6.8
import QtQuick3D.AssetUtils
import QtQuick.Window
import QtQuick.Layouts

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
            }
            
            Text {
                id: gpsStatus
                text: "GPS: No Fix"
                color: "#ff0000"
                Layout.alignment: Qt.AlignVCenter
            }
            
            Text {
                id: batteryStatus
                text: "Battery: --"
                color: "#ffffff"
                Layout.alignment: Qt.AlignVCenter
            }
            
            Item { Layout.fillWidth: true } // Spacer
        }
    }

    // Hauptbereich - 2-teiliger Aufbau (große 3D-Ansicht oben, kleine Logs unten)
    Item {
        id: mainContent
        anchors.top: statusBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10
        
        // Große 3D-Ansicht (90% der Höhe)
        Rectangle {
            id: modelView
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: parent.height * 0.9
            color: "#0a0a0a"
            border.color: "#3c3c3c"
            border.width: 1
            
            // Connection-Steuerung (oben links)
            Row {
                id: connectionControls
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 10
                spacing: 10
                z: 10
                
                ComboBox {
                    id: portSelector
                    width: 120
                    height: 30
                    model: []
                    
                    background: Rectangle {
                        color: "#1a1a1a"
                        border.color: "gray"
                        border.width: 1
                        radius: 3
                    }
                    
                    contentItem: Text {
                        text: portSelector.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 10
                    }
                    
                    popup.background: Rectangle {
                        color: "#1a1a1a"
                        border.color: "gray"
                    }
                    
                    delegate: ItemDelegate {
                        width: portSelector.width
                        contentItem: Text {
                            text: modelData
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: highlighted ? "#2a2a2a" : "#1a1a1a"
                        }
                        highlighted: portSelector.highlightedIndex === index
                    }
                    
                    onActivated: {
                        if (serialConnector) {
                            serialConnector.setPort(currentText)
                        }
                    }
                }
                
                Button {
                    id: connectButton
                    text: "Connect"
                    width: 100
                    height: 30
                    
                    background: Rectangle {
                        color: "#1e90ff"
                        radius: 3
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        if (serialConnector) {
                            if (!serialConnector.connected) {
                                serialConnector.connect()
                            } else {
                                serialConnector.disconnect()
                            }
                        }
                    }
                }
            }
            
            // 3D-Ansicht
            View3D {
                id: view3D
                anchors.fill: parent
                focus: true
                
                // Kamera
                PerspectiveCamera {
                    id: camera
                    position: Qt.vector3d(0, 150, 350)
                    eulerRotation: Qt.vector3d(-15, 0, 0)
                    clipFar: 2000.0
                    clipNear: 0.1
                    fieldOfView: 45
                }
                
                // Beleuchtung
                DirectionalLight {
                    id: mainLight
                    eulerRotation: Qt.vector3d(-45, 0, 0)
                    brightness: 1.5
                    castsShadow: true
                    shadowFactor: 25
                    shadowMapQuality: Light.ShadowMapQualityMedium
                }
                
                DirectionalLight {
                    id: fillLight
                    eulerRotation: Qt.vector3d(45, 45, 0)
                    brightness: 0.8
                    castsShadow: false
                }
                
                DirectionalLight {
                    id: backLight
                    eulerRotation: Qt.vector3d(0, 180, 0)
                    brightness: 0.6
                    castsShadow: false
                }
                
                // Erdboden
                Model {
                    id: ground
                    source: "#Rectangle"
                    scale: Qt.vector3d(400, 1, 400)
                    position: Qt.vector3d(0, -50, 0)
                    eulerRotation: Qt.vector3d(90, 0, 0)
                    materials: [
                        PrincipledMaterial {
                            baseColor: "#1a3d69"
                            roughness: 0.8
                            opacity: 0.5
                            alphaMode: PrincipledMaterial.Blend
                        }
                    ]
                }
                
                // Drohnenmodell
                Node {
                    id: droneModelNode
                    position: Qt.vector3d(0, 20, 0)
                    
                    // Schwebeananimation
                    SequentialAnimation on y {
                        id: hoverAnimation
                        loops: Animation.Infinite
                        running: true
                        NumberAnimation { 
                            from: 20; to: 25
                            duration: 1500
                            easing.type: Easing.InOutQuad
                        }
                        NumberAnimation {
                            from: 25; to: 20
                            duration: 1500
                            easing.type: Easing.InOutQuad
                        }
                    }
                    
                    Model {
                        id: droneModel
                        source: "Assets/meshes/mk4_v2_10_mesh.mesh"
                        scale: Qt.vector3d(0.5, 0.5, 0.5)
                        materials: [
                            PrincipledMaterial {
                                id: droneMaterial
                                baseColor: "#dddddd"
                                roughness: 0.3
                                metalness: 0.6
                                cullMode: PrincipledMaterial.NoCulling
                                alphaMode: PrincipledMaterial.Opaque
                            }
                        ]
                        
                        // Eigenschaften für die Rotation
                        property real rollDeg: 0
                        property real pitchDeg: 0
                        property real yawDeg: 0
                        
                        // Rotation anwenden
                        eulerRotation: Qt.vector3d(pitchDeg, yawDeg, rollDeg)
                    }
                }
                
                camera: camera
                
                // Kamerasteuerung
                WasdController {
                    id: wasdController
                    speed: 2.0
                    shiftSpeed: 5.0
                    controlledObject: camera
                    focus: true
                    Keys.forwardTo: wasdController
                }
                
                // Maussteuerung
                MouseArea {
                    anchors.fill: parent
                    property point lastPos
                    property real sensitivity: 0.5
                    propagateComposedEvents: true
                    
                    onPositionChanged: function(mouse) {
                        if (mouse.buttons === Qt.RightButton) {
                            var deltaX = (mouse.x - lastPos.x) * sensitivity
                            var deltaY = (mouse.y - lastPos.y) * sensitivity
                            
                            camera.eulerRotation.y += deltaX
                            camera.eulerRotation.x = Math.max(-90, Math.min(0, camera.eulerRotation.x - deltaY))
                        }
                        lastPos = Qt.point(mouse.x, mouse.y)
                    }
                    
                    onPressed: function(mouse) {
                        lastPos = Qt.point(mouse.x, mouse.y)
                    }
                    
                    onWheel: function(wheel) {
                        var zoomFactor = wheel.angleDelta.y > 0 ? 0.9 : 1.1
                        var dir = camera.forward
                        camera.position = Qt.vector3d(
                            camera.position.x + dir.x * 10 * (zoomFactor - 1),
                            camera.position.y + dir.y * 10 * (zoomFactor - 1),
                            camera.position.z + dir.z * 10 * (zoomFactor - 1)
                        )
                    }
                }
            }
            
            // Rotation values and control aids
            Column {
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottomMargin: 10
                spacing: 5
                
                Text {
                    color: "white"
                    text: `Roll: ${droneModel.rollDeg.toFixed(1)}°, Pitch: ${droneModel.pitchDeg.toFixed(1)}°, Yaw: ${droneModel.yawDeg.toFixed(1)}°`
                    font.pixelSize: 14
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                
                Text {
                    color: "#aaaaaa"
                    text: "Zoom: Mouse wheel | Camera rotation: Right mouse button | Movement: WASD"
                    font.pixelSize: 12
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
            
            // Zoom-Steuerung
            Row {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 10
                spacing: 5
                
                Button {
                    width: 40
                    height: 40
                    text: "+"
                    font.pixelSize: 20
                    background: Rectangle {
                        color: "#333333"
                        opacity: 0.7
                        radius: 5
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        var dir = camera.forward
                        camera.position = Qt.vector3d(
                            camera.position.x + dir.x * 30,
                            camera.position.y + dir.y * 30,
                            camera.position.z + dir.z * 30
                        )
                    }
                }
                
                Button {
                    width: 40
                    height: 40
                    text: "-"
                    font.pixelSize: 20
                    background: Rectangle {
                        color: "#333333"
                        opacity: 0.7
                        radius: 5
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        var dir = camera.forward
                        camera.position = Qt.vector3d(
                            camera.position.x - dir.x * 30,
                            camera.position.y - dir.y * 30,
                            camera.position.z - dir.z * 30
                        )
                    }
                }
                
                Button {
                    width: 40
                    height: 40
                    text: "R"
                    font.pixelSize: 16
                    background: Rectangle {
                        color: "#333333"
                        opacity: 0.7
                        radius: 5
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        camera.position = Qt.vector3d(0, 150, 350)
                        camera.eulerRotation = Qt.vector3d(-15, 0, 0)
                    }
                }
            }
        }
        
        // Compact log view (10% of height)
        Rectangle {
            id: logArea
            anchors.top: modelView.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.topMargin: 10
            color: "#121212"
            border.color: "#3c3c3c"
            border.width: 1
            
            // Überschrift und Clear-Button
            Row {
                id: logHeader
                height: 25
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 5
                spacing: 10
                
                Text {
                    text: "Important FC Messages"
                    color: "white"
                    font.pixelSize: 12
                    font.bold: true
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Button {
                    width: 80
                    height: 20
                    text: "Clear"
                    font.pixelSize: 10
                    
                    background: Rectangle {
                        color: "#333333"
                        radius: 3
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        if (logger) {
                            logger.clear()
                        }
                    }
                }
            }
            
            // Kompakte Logs (nur wichtige Meldungen)
            LogsList {
                id: logslist
                anchors.top: logHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: 5
            }
        }
    }
    
    // Timer for sensor updates (3D model, GPS and battery)
    Timer {
        id: sensorUpdateTimer
        interval: 50
        running: true
        repeat: true
        
        onTriggered: {
            if (sensorModel) {
                try {
                    var sensors = sensorModel.get_all_sensors()
                    var rollValue = 0
                    var pitchValue = 0
                    var yawValue = 0
                    var gpsLat = 0
                    var gpsLon = 0
                    var batteryPercent = 0
                    var batteryVoltage = 0
                    
                    // Sensoren auslesen
                    for (var i = 0; i < sensors.length; i++) {
                        var sensor = sensors[i]
                        
                        // Attitude für 3D-Modell
                        if (sensor.id === "roll") {
                            rollValue = sensor.value
                        } else if (sensor.id === "pitch") {
                            pitchValue = sensor.value
                        } else if (sensor.id === "yaw") {
                            yawValue = sensor.value
                        }
                        
                        // GPS-Daten
                        else if (sensor.id === "gps_lat") {
                            gpsLat = sensor.value
                        } else if (sensor.id === "gps_lon") {
                            gpsLon = sensor.value
                        }
                        
                        // Batterie-Daten
                        else if (sensor.id === "battery_remaining") {
                            batteryPercent = sensor.value
                        } else if (sensor.id === "battery_voltage") {
                            batteryVoltage = sensor.value
                        }
                    }
                    
                    // 3D-Modell aktualisieren
                    droneModel.rollDeg = rollValue
                    droneModel.pitchDeg = pitchValue
                    droneModel.yawDeg = yawValue
                    
                    // GPS-Status aktualisieren, wenn Daten vorhanden
                    if (gpsLat !== 0 || gpsLon !== 0) {
                        gpsStatus.text = `GPS: ${gpsLat.toFixed(6)}, ${gpsLon.toFixed(6)}`
                        gpsStatus.color = "#00ff00"
                    }
                    
                    // Batterie-Status aktualisieren, wenn Daten vorhanden
                    if (batteryPercent > 0) {
                        batteryStatus.text = `Battery: ${batteryPercent.toFixed(0)}% (${batteryVoltage.toFixed(1)}V)`
                        batteryStatus.color = batteryPercent > 20 ? "#00ff00" : "#ff0000"
                    }
                } catch (e) {
                    // Fehler ignorieren
                }
            }
        }
    }
    
    // Connections für Attitude-Updates
    Connections {
        target: serialConnector
        
        // Hauptverbindung für Attitude-Werte
        function onAttitudeChanged(roll, pitch, yaw) {
            var rollDeg = (typeof roll === 'number' && Math.abs(roll) < Math.PI) ? (roll * 180 / Math.PI) : roll
            var pitchDeg = (typeof pitch === 'number' && Math.abs(pitch) < Math.PI) ? (pitch * 180 / Math.PI) : pitch
            var yawDeg = (typeof yaw === 'number' && Math.abs(yaw) < Math.PI) ? (yaw * 180 / Math.PI) : yaw
            
            droneModel.rollDeg = rollDeg
            droneModel.pitchDeg = pitchDeg
            droneModel.yawDeg = yawDeg
        }
        
        // Fallback für älteres Format
        function onAttitude_msg(roll, pitch, yaw) {
            var rollDeg = (typeof roll === 'number' && Math.abs(roll) < Math.PI) ? (roll * 180 / Math.PI) : roll
            var pitchDeg = (typeof pitch === 'number' && Math.abs(pitch) < Math.PI) ? (pitch * 180 / Math.PI) : pitch
            var yawDeg = (typeof yaw === 'number' && Math.abs(yaw) < Math.PI) ? (yaw * 180 / Math.PI) : yaw
            
            droneModel.rollDeg = rollDeg
            droneModel.pitchDeg = pitchDeg
            droneModel.yawDeg = yawDeg
        }
        
        // Connection status
        function onConnectedChanged(connected) {
            connectionStatus.text = connected ? "Connected" : "Disconnected"
            connectionStatus.color = connected ? "#00ff00" : "#ff0000"
            connectButton.text = connected ? "Disconnect" : "Connect"
            
            hoverAnimation.running = connected
        }
    }
    
    // Initialisierung
    Component.onCompleted: {
        if (serialConnector) {
            if (serialConnector.connected) {
                connectionStatus.text = "Connected"
                connectionStatus.color = "#00ff00"
                connectButton.text = "Disconnect"
            }
            
            // Ports aktualisieren
            portSelector.model = serialConnector.availablePorts
        }
    }
}