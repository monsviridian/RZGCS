import QtQuick
import QtQuick3D
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 300
    height: 300
    
    // Eigenschaften zur Steuerung der Rotation
    property real angleX: 0
    property real angleY: 0
    property real angleZ: 0
    
    // Eigenschaften zur Visualisierung des Kalibrierungsfortschritts
    property real calibrationProgress: 0.0
    property var collectedPoints: []
    
    // Funktion zum Hinzufügen neuer Kalibrierungspunkte
    function addCalibrationPoint(x, y, z) {
        // Normalisieren der Werte
        var mag = Math.sqrt(x*x + y*y + z*z);
        if (mag > 0) {
            var normalized_x = x / mag;
            var normalized_y = y / mag;
            var normalized_z = z / mag;
            
            // Punkt zur Liste hinzufügen (maximal 100 Punkte)
            if (collectedPoints.length > 100) {
                collectedPoints.shift(); // Ältesten Punkt entfernen
            }
            collectedPoints.push({x: normalized_x, y: normalized_y, z: normalized_z});
        }
    }
    
    // Animation starten/stoppen
    function startRotationAnimation() {
        rotationAnimation.start();
    }
    
    function stopRotationAnimation() {
        rotationAnimation.stop();
    }
    
    // View3D für die 3D-Darstellung
    View3D {
        id: view3D
        anchors.fill: parent
        
        environment: SceneEnvironment {
            backgroundMode: SceneEnvironment.Color
            clearColor: "#2c2c2c"
            antialiasingMode: SceneEnvironment.MSAA
            antialiasingQuality: SceneEnvironment.High
        }
        
        // Kamera mit besserer Position
        PerspectiveCamera {
            id: camera
            position: Qt.vector3d(0, 100, 350)
            eulerRotation: Qt.vector3d(-15, 0, 0)  // Statt lookAt, da nicht alle Qt-Versionen lookAt unterstützen
            clipFar: 2000
            clipNear: 1
        }
        
        // Bessere Beleuchtung
        DirectionalLight {
            eulerRotation: Qt.vector3d(-30, -30, 0)
            brightness: 1.0
            ambientColor: Qt.rgba(0.1, 0.1, 0.1, 1.0)
        }
        
        DirectionalLight {
            eulerRotation: Qt.vector3d(45, 45, 0)
            brightness: 0.5
        }
        
        // Drohnenmodell
        Model {
            id: droneModel
            source: "Assets/meshes/mk4_v2_10_mesh.mesh"
            scale: Qt.vector3d(0.5, 0.5, 0.5)
            eulerRotation: Qt.vector3d(root.angleX, root.angleY, root.angleZ)
            materials: [
                PrincipledMaterial {
                    baseColor: "#e0e0e0"
                    roughness: 0.3
                    metalness: 0.6
                }
            ]
        }
        
        // Koordinatenachsen (klein und subtil)
        Model {
            id: xAxis
            source: "#Cylinder"
            position: Qt.vector3d(25, 0, 0)
            eulerRotation: Qt.vector3d(0, 0, 90)
            scale: Qt.vector3d(0.2, 50, 0.2)
            materials: [PrincipledMaterial { baseColor: "#ff6666"; opacity: 0.7 }]
        }
        
        Model {
            id: yAxis
            source: "#Cylinder"
            position: Qt.vector3d(0, 25, 0)
            scale: Qt.vector3d(0.2, 50, 0.2)
            materials: [PrincipledMaterial { baseColor: "#66ff66"; opacity: 0.7 }]
        }
        
        Model {
            id: zAxis
            source: "#Cylinder"
            position: Qt.vector3d(0, 0, 25)
            eulerRotation: Qt.vector3d(90, 0, 0)
            scale: Qt.vector3d(0.2, 50, 0.2)
            materials: [PrincipledMaterial { baseColor: "#6666ff"; opacity: 0.7 }]
        }
        
        // Kompass-Sphäre für Visualisierung (transparenter)
        Model {
            id: compassSphere
            source: "#Sphere"
            scale: Qt.vector3d(100, 100, 100)
            materials: [
                PrincipledMaterial {
                    baseColor: "#333333"
                    roughness: 0.8
                    metalness: 0.0
                    opacity: 0.15
                    alphaMode: PrincipledMaterial.Blend
                }
            ]
        }
        
        // Hilfsebene für bessere Orientierung
        Model {
            source: "#Rectangle"
            scale: Qt.vector3d(150, 150, 1)
            position: Qt.vector3d(0, -25, 0)
            eulerRotation: Qt.vector3d(-90, 0, 0)
            materials: [PrincipledMaterial { baseColor: "#303030"; opacity: 0.5 }]
        }
    }
    
    // Animation für Figur-8-Bewegung (für Demo)
    SequentialAnimation {
        id: rotationAnimation
        running: false
        loops: Animation.Infinite
        
        // Erste Hälfte der Figur-8
        ParallelAnimation {
            NumberAnimation { target: root; property: "angleY"; from: 0; to: 180; duration: 2000; easing.type: Easing.InOutQuad }
            SequentialAnimation {
                NumberAnimation { target: root; property: "angleZ"; from: 0; to: 45; duration: 1000; easing.type: Easing.InOutQuad }
                NumberAnimation { target: root; property: "angleZ"; from: 45; to: -45; duration: 1000; easing.type: Easing.InOutQuad }
            }
        }
        
        // Zweite Hälfte der Figur-8
        ParallelAnimation {
            NumberAnimation { target: root; property: "angleY"; from: 180; to: 360; duration: 2000; easing.type: Easing.InOutQuad }
            SequentialAnimation {
                NumberAnimation { target: root; property: "angleZ"; from: -45; to: 45; duration: 1000; easing.type: Easing.InOutQuad }
                NumberAnimation { target: root; property: "angleZ"; from: 45; to: 0; duration: 1000; easing.type: Easing.InOutQuad }
            }
        }
    }
    
    // Anweisungs-Overlay
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 60
        color: Qt.rgba(0, 0, 0, 0.6)
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 5
            spacing: 2
            
            Text {
                text: "Drehen Sie die Drohne langsam in einer Figur-8-Bewegung"
                color: "white"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 12
            }
            
            ProgressBar {
                Layout.fillWidth: true
                value: calibrationProgress
            }
            
            Text {
                text: "Fortschritt: " + Math.round(calibrationProgress * 100) + "%"
                color: "white"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 12
            }
        }
    }
}
