/*
Store View mit 3D-Modell-Vorschau und Model-Wechsel-Funktion.
*/
import QtQuick
import QtQuick.Controls
import QtQuick3D 6.8
import QtQuick3D.Helpers 6.8
import QtQuick3D.AssetUtils
import QtQuick.Layouts

Item {
    id: storeview
    width: parent.width
    height: parent.height

    // Schwarzer Hintergrund
    Rectangle {
        anchors.fill: parent
        color: "black"
        z: -1
    }

    // Hauptbereich
    Item {
        id: mainContent
        anchors.fill: parent
        anchors.margins: 10

        // Header-Bereich mit Logo und Titel
        Rectangle {
            id: headerArea
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 80
            color: "#1a1a1a"
            radius: 5

            // Logo-Bereich links
            Rectangle {
                id: logoArea
                width: 200
                height: parent.height - 20
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 20
                color: "#262626"
                radius: 5

                Image {
                    id: logoImage
                    anchors.centerIn: parent
                    source: "Assets/logo_base.png"
                    width: parent.width * 0.8
                    height: parent.height * 0.8
                    fillMode: Image.PreserveAspectFit
                }
            }

            // Titel-Bereich mit Bild
            Image {
                anchors.left: logoArea.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 20
                source: "Assets/Ebene_1-2.png"
                height: parent.height * 0.6
                fillMode: Image.PreserveAspectFit
            }
        }

        // Hauptbereich mit 3D-Ansicht und Seitenleiste
        Row {
            anchors.top: headerArea.bottom
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: 10
            spacing: 10

            // 3D-Modell-Ansicht (70% der Breite)
            Rectangle {
                id: modelView
                width: parent.width * 0.7
                height: parent.height
                color: "#0a0a0a"
                border.color: "#3c3c3c"
                border.width: 1

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
                            property real yawDeg: 30  // Start mit leichter Drehung
                            
                            // Rotation anwenden
                            eulerRotation: Qt.vector3d(pitchDeg, yawDeg, rollDeg)
                        }
                    }
                    
                    camera: camera
                    
                    // Automatische Rotation
                    NumberAnimation {
                        target: droneModel
                        property: "yawDeg"
                        from: 0
                        to: 360
                        duration: 10000
                        loops: Animation.Infinite
                        running: true
                    }
                    
                    // Kamerasteuerung
                    WasdController {
                        id: wasdController
                        speed: 2.0
                        shiftSpeed: 5.0
                        controlledObject: camera
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
                
                // Steuerungshilfe
                Text {
                    anchors.bottom: parent.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottomMargin: 10
                    color: "#aaaaaa"
                    text: "Zoom: Mouse wheel | Camera rotation: Right mouse button | Movement: WASD"
                    font.pixelSize: 12
                }
            }
            
            // Seitenleiste (30% der Breite)
            Rectangle {
                id: sidebar
                width: parent.width * 0.3 - parent.spacing
                height: parent.height
                color: "#121212"
                border.color: "#3c3c3c"
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 20
                    
                    // Modell-Auswahl-Bereich
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 120
                        color: "#1a1a1a"
                        radius: 5
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            spacing: 15
                            
                            Text {
                                text: "Select Model"
                                font.pixelSize: 18
                                font.bold: true
                                color: "white"
                            }
                            
                            ComboBox {
                                id: modelSelector
                                Layout.fillWidth: true
                                model: ["RZ MK4 Drone", "RZ MK3 Pro", "RZ Phoenix", "RZ Talon"]
                                
                                background: Rectangle {
                                    color: "#262626"
                                    border.color: "#3c3c3c"
                                    border.width: 1
                                    radius: 3
                                }
                                
                                contentItem: Text {
                                    text: modelSelector.displayText
                                    color: "white"
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: 10
                                }
                                
                                popup.background: Rectangle {
                                    color: "#262626"
                                    border.color: "#3c3c3c"
                                }
                                
                                delegate: ItemDelegate {
                                    width: modelSelector.width
                                    contentItem: Text {
                                        text: modelData
                                        color: "white"
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    background: Rectangle {
                                        color: highlighted ? "#3c3c3c" : "#262626"
                                    }
                                    highlighted: modelSelector.highlightedIndex === index
                                }
                            }
                            
                            Button {
                                id: changeModelButton
                                Layout.fillWidth: true
                                text: "Change Model"
                                
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
                                    // In a real system, this would change the 3D model
                                    console.log("Changing model to: " + modelSelector.currentText)
                                }
                            }
                        }
                    }
                    
                    // Modell-Informationen
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#1a1a1a"
                        radius: 5
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            spacing: 15
                            
                            Text {
                                text: "About this Model"
                                font.pixelSize: 18
                                font.bold: true
                                color: "white"
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                
                                TextArea {
                                    id: aboutText
                                    readOnly: true
                                    wrapMode: TextEdit.Wrap
                                    textFormat: TextEdit.RichText
                                    color: "white"
                                    background: Item {}
                                    text: "<h3>RZ MK4 Drone</h3>
                                    <p>The RZ MK4 Drone is our latest high-performance UAV for professional applications.</p>
                                    <p><b>Technical Specifications:</b></p>
                                    <ul>
                                        <li>Flight time: up to 45 minutes</li>
                                        <li>Maximum speed: 72 km/h</li>
                                        <li>Range: 8 km</li>
                                        <li>Camera: 4K@60fps</li>
                                        <li>Weight: 1.2 kg</li>
                                    </ul>
                                    <p>Ideal for aerial photography, inspection, and mapping. Equipped with state-of-the-art collision avoidance technology and precise GPS.</p>
                                    <p><b>Benefits:</b></p>
                                    <ul>
                                        <li>Enhanced wind resistance</li>
                                        <li>Foldable design for easy transport</li>
                                        <li>Advanced autonomous functions</li>
                                        <li>Compatible with all RZ sensors</li>
                                    </ul>"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
