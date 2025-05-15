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

Item {
    id: preflightview
    width: 1483
    height: 1080

    Rectangle {
        x: 0
        width: 1483

        anchors.leftMargin: 8
        anchors.rightMargin: 431
        color: "black"
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        z: -1 // sorgt dafür, dass es hinter allen anderen Komponenten liegt
    }

    Text {
        id: titel
        x: 154
        y: 25
        width: 86
        text: qsTr("Logs")
        color: "white"

        anchors.bottom: logslist.top
        anchors.topMargin: -25
        anchors.bottomMargin: 9
    }

    // Clear-Button für Logs
    Button {
        id: clearLogsButton
        text: qsTr("Clear Logs")
        x: 250
        y: 25
        width: 100
        height: 30
        
        onClicked: {
            if (logger) {
                logger.clear()
            }
        }
    }

    // Test-Button für Logs
    Button {
        id: testLogButton
        text: qsTr("Test Log")
        x: 360
        y: 25
        width: 100
        height: 30
        
        onClicked: {
            if (logger) {
                logger.info("Test log message " + new Date().toLocaleTimeString())
            }
        }
    }

    LogsList {
        id: logslist
        width: 373

        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: 33
        anchors.topMargin: 55
        anchors.bottomMargin: 110
        anchors.top: parent.top
    }

    Frame {
        id: connectframe
        x: 753
        y: 84

        width: 247
        height: 169

        ComboBox {
            id: portSelector
            x: 0
            y: 0
            width: 82
            height: 32
            model: []

            Connections {
                target: serialConnector
                function onAvailable_ports_changed(ports) {
                    portSelector.model = ports
                }

                Component.onCompleted: {
                    console.log("Lade Ports ...")
                    serialConnector.load_ports()
                }
            }
        }

        ComboBox {
            id: connectorType
            x: 88
            y: 0
            width: 82
            height: 32
            model: ["MAVLink", "MAVSDK"]
        }

        ComboBox {
            id: baurate
            x: 0
            y: 57
            width: 82
            height: 32

            model: ["115200", "57600", "38400"]
        }
        ComboBox {
            id: autopilot
            x: 0
            y: 107
            width: 82
            height: 32

            model: ["ArduPilot", "Betaflight"]
        }

        Button {
            id: button
            x: 143
            y: 48
            width: 92
            height: 32
            text: qsTr("Connect")

            Connections {
                target: button
                function onClicked() {
                    console.log("🟢 Button geklickt") // ← Debug
                    serialConnector.connect_to_serial(
                                portSelector.currentText,
                                parseInt(baurate.currentText),
                                autopilot.currentText,
                                connectorType.currentText)
                }
            }
        }

        Button {
            id: disconnect
            x: 143
            y: 98
            text: qsTr("Disconnect")

            Connections {
                target: disconnect
                function onClicked() {
                    serialConnector.disconnect()
                }
            }
        }
    }

    View3D {
        id: view3D
        anchors.left: parent.left
        anchors.right: parent.horizontalCenter
        anchors.top: parent.top
        anchors.bottom: parent.verticalCenter
        anchors.leftMargin: 948
        anchors.rightMargin: -491
        anchors.topMargin: 289
        anchors.bottomMargin: 44
        environment: sceneEnvironment
        camera: camera

        SceneEnvironment {
            id: sceneEnvironment
            backgroundMode: SceneEnvironment.Color
            clearColor: "#100b0b"
            antialiasingQuality: SceneEnvironment.High
            antialiasingMode: SceneEnvironment.MSAA
        }

        PerspectiveCamera {
            id: camera
            position: Qt.vector3d(300, 200, 300)
            eulerRotation: Qt.vector3d(-30, 45, 0)
        }

        DirectionalLight {
            id: light
            eulerRotation: Qt.vector3d(-45, 0, 0)
            brightness: 10
        }

        Node {
            id: node

            Node {
                id: view3d
                objectName: "ROOT"

                Model {
                    id: cube
                    objectName: "Cube"
                    source: "Assets/meshes/cube_mesh.mesh"
                    materials: [material_material]
                }

                Model {
                    id: mk4_v2_10
                    objectName: "mk4_v2_10"
                    source: "Assets/meshes/mk4_v2_10_mesh.mesh"
                    scale: Qt.vector3d(0.5, 0.5, 0.5)
                    materials: [default_MTL_material]

                    // ✨ Eigene Properties für Drehwinkel
                    property real rollDeg: 0
                    property real pitchDeg: 0
                    property real yawDeg: 0

                    // ✨ Drohnenrotation über Roll, Pitch, Yaw
                    eulerRotation: Qt.vector3d(rollDeg, yawDeg, pitchDeg)
                }
            }

            Node {
                id: __materialLibrary__

                PrincipledMaterial {
                    id: material_material
                    objectName: "Material"
                    baseColor: "#ffcccccc"
                    roughness: 0.5
                    cullMode: PrincipledMaterial.NoCulling
                    alphaMode: PrincipledMaterial.Opaque
                }

                PrincipledMaterial {
                    id: default_MTL_material
                    objectName: "DEFAULT_MTL"
                    baseColor: "#ffcccccc"
                    roughness: 1
                    cullMode: PrincipledMaterial.NoCulling
                    alphaMode: PrincipledMaterial.Opaque
                }
            }
        }

        // ✨ Verbindung zum Python-Signal, das Attitude-Werte liefert
        Connections {
            target: serialConnector
            onAttitude_msg: (roll, pitch, yaw) => {
                                mk4_v2_10.rollDeg = roll * 180 / Math.PI
                                mk4_v2_10.pitchDeg = pitch * 180 / Math.PI
                                mk4_v2_10.yawDeg = yaw * 180 / Math.PI
                            }
        }

        // Optional: Anzeigen der Werte für Debugging
    }

    View3D {
        id: view3D1
        x: 1032
        y: 70
        anchors.left: parent.left
        anchors.right: parent.horizontalCenter
        anchors.top: parent.top
        anchors.bottom: parent.verticalCenter

        anchors.leftMargin: 433
        anchors.rightMargin: 40
        anchors.topMargin: 295
        anchors.bottomMargin: 50
        environment: sceneEnvironment1
        SceneEnvironment {
            id: sceneEnvironment1
            clearColor: "#100b0b"
            backgroundMode: SceneEnvironment.Color
            antialiasingQuality: SceneEnvironment.High
            antialiasingMode: SceneEnvironment.MSAA
        }

        PerspectiveCamera {
            id: camera1
            position: Qt.vector3d(
                          0, 0,
                          500) // Kamera steht vor dem Modell auf der Z-Achse
            eulerRotation: Qt.vector3d(0, 0, 0)
        }

        DirectionalLight {
            id: light1
            eulerRotation: Qt.vector3d(0, 0, 0)
            brightness: 10
        }

        Node {
            id: node1
            Node {
                id: view3d1
                objectName: "ROOT"
                Model {
                    id: cube1
                    source: "Assets/meshes/cube_mesh.mesh"
                    objectName: "Cube"
                    materials: [material_material1]
                }

                Model {
                    id: mk4_v2_11
                    source: "Assets/meshes/mk4_v2_10_mesh.mesh"
                    scale: Qt.vector3d(0.5, 0.5, 0.5)
                    rotation: Qt.quaternion(0.99984, -0.017862, 0, 0)
                    objectName: "mk4_v2_10"
                    materials: [default_MTL_material1]
                    // ✨ Eigene Properties für Drehwinkel
                    property real rollDeg: 0
                    property real pitchDeg: 0
                    property real yawDeg: 0

                    // ✨ Drohnenrotation über Roll, Pitch, Yaw
                    eulerRotation: Qt.vector3d(rollDeg, yawDeg, pitchDeg)
                }
            }

            Node {
                id: __materialLibrary__1
                PrincipledMaterial {
                    id: material_material1
                    roughness: 0.5
                    objectName: "Material"
                    cullMode: PrincipledMaterial.NoCulling
                    baseColor: "#cccccc"
                    alphaMode: PrincipledMaterial.Opaque
                }

                PrincipledMaterial {
                    id: default_MTL_material1
                    roughness: 1
                    objectName: "DEFAULT_MTL"
                    cullMode: PrincipledMaterial.NoCulling
                    baseColor: "#cccccc"
                    alphaMode: PrincipledMaterial.Opaque
                }
            }
        }
        Connections {
            target: serialConnector
            onAttitude_msg: (roll, pitch, yaw) => {
                                mk4_v2_11.rollDeg = roll * 180 / Math.PI
                                mk4_v2_11.pitchDeg = pitch * 180 / Math.PI
                                mk4_v2_11.yawDeg = yaw * 180 / Math.PI
                            }
        }

        Text {
            y: 168

            anchors.leftMargin: 296
            anchors.topMargin: 188
            anchors.left: parent.left
            color: "white"
            text: `Roll: ${mk4_v2_10.rollDeg.toFixed(
                      2)}°, Pitch: ${mk4_v2_10.pitchDeg.toFixed(
                      2)}°, Yaw: ${mk4_v2_10.yawDeg.toFixed(2)}°`
            font.pixelSize: 14
        }

        camera: camera1
    }

    SensorView {
        id: sensorView
        x: 493
        y: 578
        width: 767
        height: 263
    }

    Button {
        id: loadsensor
        x: 861
        y: 524
        text: qsTr("Load Sensor")

        Connections {
            target: loadsensor
            function onClicked() {
                sensorModel.update_sensor("GPS", Math.random() * 100)
            }
        }
    }

    Connections {
        target: preflightview
        function onActiveFocusChanged() {
            console.log("clicked")
        }
    }
}

/*##^##
Designer {
    D{i:0;matPrevEnvDoc:"SkyBox";matPrevEnvValueDoc:"preview_studio";matPrevModelDoc:"#Sphere"}
D{i:13;cameraSpeed3d:25;cameraSpeed3dMultiplier:1}D{i:25;cameraSpeed3d:25;cameraSpeed3dMultiplier:1}
}
##^##*/

