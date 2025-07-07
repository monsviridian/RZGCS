import QtQuick
import QtQuick3D
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 400
    height: 400
    
    // Controller-Referenz, die von außen gesetzt wird
    property var controller: null
    
    // Eigenschaften zur Steuerung der Rotation
    property real angleX: 0
    property real angleY: 0
    property real angleZ: 0
    
    // Eigenschaft für den Kalibrierungsfortschritt
    property real calibrationProgress: 0.0
    property int currentStep: 0
    
    // Kalibrierungspunkte für Visualisierung
    property var collectedPoints: []
    property int totalPointsNeeded: 50
    property int currentPoints: 0
    
    // Funktion zum Hinzufügen eines Kalibrierungspunkts
    function addCalibrationPoint(x, y, z) {
        if (collectedPoints.length < totalPointsNeeded) {
            collectedPoints.push({x: x, y: y, z: z});
            currentPoints = collectedPoints.length;
            calibrationProgress = Math.min(currentPoints / totalPointsNeeded, 1.0);
            
            // Erstelle visuellen Punkt in der 3D-Szene
            var point = calibrationPointComponent.createObject(calibrationPointsNode, {
                "position": Qt.vector3d(x * 50, y * 50, z * 50)
            });
        }
    }
    
    // Funktion zum Zurücksetzen der Kalibrierung
    function resetCalibration() {
        collectedPoints = [];
        currentPoints = 0;
        calibrationProgress = 0.0;
        
        // Entferne alle Kalibrierungspunkte aus der 3D-Szene
        for (var i = calibrationPointsNode.children.length - 1; i >= 0; i--) {
            calibrationPointsNode.children[i].destroy();
        }
    }
    
    // View3D für die 3D-Darstellung
    View3D {
        id: view3D
        anchors.fill: parent
        
        environment: SceneEnvironment {
            backgroundMode: SceneEnvironment.Color
            clearColor: "#1a1a1a"
            antialiasingMode: SceneEnvironment.MSAA
            antialiasingQuality: SceneEnvironment.High
        }
        
        // Kamera mit besserer Position für Kompass-Ansicht
        PerspectiveCamera {
            id: camera
            position: Qt.vector3d(0, 0, 400)
            eulerRotation: Qt.vector3d(0, 0, 0)
            clipFar: 2000
            clipNear: 1
        }
        
        // Beleuchtung
        DirectionalLight {
            eulerRotation: Qt.vector3d(-30, -30, 0)
            brightness: 1.0
            ambientColor: Qt.rgba(0.2, 0.2, 0.2, 1.0)
        }
        
        DirectionalLight {
            eulerRotation: Qt.vector3d(45, 45, 0)
            brightness: 0.5
        }
        
        // Kalibrierungssphäre (transparent)
        Model {
            source: "#Sphere"
            scale: Qt.vector3d(100, 100, 100)
            materials: [
                PrincipledMaterial {
                    baseColor: Qt.rgba(0.1, 0.3, 0.8, 0.1)
                    opacity: 0.3
                    alphaMode: PrincipledMaterial.Blend
                    roughness: 0.8
                }
            ]
        }
        
        // Koordinatenachsen
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(120, 0, 0)
            eulerRotation: Qt.vector3d(0, 0, 90)
            scale: Qt.vector3d(0.5, 120, 0.5)
            materials: [PrincipledMaterial { baseColor: "#ff6666" }]
        }
        
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(0, 120, 0)
            scale: Qt.vector3d(0.5, 120, 0.5)
            materials: [PrincipledMaterial { baseColor: "#66ff66" }]
        }
        
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(0, 0, 120)
            eulerRotation: Qt.vector3d(90, 0, 0)
            scale: Qt.vector3d(0.5, 120, 0.5)
            materials: [PrincipledMaterial { baseColor: "#6666ff" }]
        }
        
        // Drohnenmodell in der Mitte
        Model {
            id: droneModel
            source: "Assets/meshes/mk4_v2_10_mesh.mesh"
            scale: Qt.vector3d(0.3, 0.3, 0.3)
            eulerRotation: Qt.vector3d(root.angleX, root.angleY, root.angleZ)
            materials: [
                PrincipledMaterial {
                    baseColor: "#50c0ff"
                    roughness: 0.3
                    metalness: 0.7
                }
            ]
        }
        
        // Node für Kalibrierungspunkte
        Node {
            id: calibrationPointsNode
        }
        
        // Hilfsebene für Orientierung
        Model {
            source: "#Rectangle"
            scale: Qt.vector3d(200, 200, 1)
            position: Qt.vector3d(0, -50, 0)
            eulerRotation: Qt.vector3d(-90, 0, 0)
            materials: [
                PrincipledMaterial {
                    baseColor: "#333333"
                    opacity: 0.3
                    alphaMode: PrincipledMaterial.Blend
                }
            ]
        }
    }
    
    // Komponente für Kalibrierungspunkte
    Component {
        id: calibrationPointComponent
        
        Model {
            source: "#Sphere"
            scale: Qt.vector3d(2, 2, 2)
            materials: [
                PrincipledMaterial {
                    baseColor: "#ffff00"
                    emissiveFactor: Qt.rgba(0.5, 0.5, 0, 1.0)
                    roughness: 0.2
                }
            ]
        }
    }
    
    // Status-Overlay
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 100
        color: Qt.rgba(0, 0, 0, 0.7)
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 5
            
            Text {
                text: "Kompass-Kalibrierung"
                color: "white"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 14
                font.bold: true
            }
            
            ProgressBar {
                Layout.fillWidth: true
                value: calibrationProgress
                background: Rectangle {
                    color: "#333333"
                    radius: 2
                }
                contentItem: Rectangle {
                    color: calibrationProgress > 0.8 ? "#66ff66" : "#ffff66"
                    radius: 2
                }
            }
            
            Text {
                text: currentPoints + " / " + totalPointsNeeded + " Punkte gesammelt (" + Math.round(calibrationProgress * 100) + "%)"
                color: "white"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 12
            }
            
            Text {
                text: "Drehen Sie die Drohne in alle Richtungen"
                color: "#cccccc"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 11
            }
        }
    }
    
    // Automatische Rotation der Kamera für bessere Übersicht
    NumberAnimation {
        target: camera
        property: "eulerRotation.y"
        from: 0
        to: 360
        duration: 30000
        loops: Animation.Infinite
        running: true
    }
}
