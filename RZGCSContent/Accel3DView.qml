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
    
    // Eigenschaft für den Kalibrierungsfortschritt
    property real calibrationProgress: 0.0
    property int currentStep: 0
    
    // Anleitung zur Position basierend auf Schritt
    readonly property var positionDescriptions: [
        "Position 1: Drohne flach auf den Boden stellen (Z+)",
        "Position 2: Drohne auf den Rücken stellen (Z-)",
        "Position 3: Drohne auf die linke Seite stellen (X-)",
        "Position 4: Drohne auf die rechte Seite stellen (X+)",
        "Position 5: Drohne auf die Nase stellen (Y+)",
        "Position 6: Drohne mit Nase nach unten stellen (Y-)"
    ]
    
    // Funktion zum Setzen des Kalibrierungsschritts
    function setCalibrationStep(step) {
        if (step >= 0 && step < 6) {
            currentStep = step
            updateDroneOrientation()
        }
    }
    
    // Funktion zum Aktualisieren der Drohnenausrichtung basierend auf dem aktuellen Schritt
    function updateDroneOrientation() {
        switch (currentStep) {
            case 0: // Z+ (flach)
                angleX = 0
                angleY = 0
                angleZ = 0
                break
            case 1: // Z- (auf dem Rücken)
                angleX = 180
                angleY = 0
                angleZ = 0
                break
            case 2: // X- (linke Seite)
                angleX = 0
                angleY = 0
                angleZ = -90
                break
            case 3: // X+ (rechte Seite)
                angleX = 0
                angleY = 0
                angleZ = 90
                break
            case 4: // Y+ (Nase nach oben)
                angleX = -90
                angleY = 0
                angleZ = 0
                break
            case 5: // Y- (Nase nach unten)
                angleX = 90
                angleY = 0
                angleZ = 0
                break
        }
    }
    
    // Animation für Übergänge zwischen Positionen
    function startAnimation() {
        rotationAnimation.start()
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
        
        // Hilfsebene für bessere Orientierung
        Model {
            source: "#Rectangle"
            scale: Qt.vector3d(150, 150, 1)
            position: Qt.vector3d(0, -25, 0)
            eulerRotation: Qt.vector3d(-90, 0, 0)
            materials: [PrincipledMaterial { baseColor: "#303030"; opacity: 0.5 }]
        }
    }
    
    // Animation für Übergang zwischen Positionen
    SequentialAnimation {
        id: rotationAnimation
        running: false
        
        ParallelAnimation {
            NumberAnimation { target: root; property: "angleX"; duration: 500; easing.type: Easing.InOutQuad }
            NumberAnimation { target: root; property: "angleY"; duration: 500; easing.type: Easing.InOutQuad }
            NumberAnimation { target: root; property: "angleZ"; duration: 500; easing.type: Easing.InOutQuad }
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
                text: currentStep < positionDescriptions.length 
                      ? positionDescriptions[currentStep] 
                      : "Kalibrierung abgeschlossen"
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
                text: "Schritt " + (currentStep + 1) + " von 6 - " + Math.round(calibrationProgress * 100) + "%"
                color: "white"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 12
            }
        }
    }
}
