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
    
    // Anleitung zur Position basierend auf Schritt
    readonly property var positionDescriptions: [
        "Position 1: Drohne flach auf den Boden stellen (Z+)",
        "Position 2: Drohne auf den Rücken stellen (Z-)", 
        "Position 3: Drohne auf die linke Seite stellen (X-)",
        "Position 4: Drohne auf die rechte Seite stellen (X+)",
        "Position 5: Drohne auf die Nase stellen (Y+)",
        "Position 6: Drohne mit Nase nach unten stellen (Y-)"
    ]
    
    readonly property var positionDetails: [
        "Halten Sie die Drohne flach und waagerecht. Die Propeller sollten nach oben zeigen.",
        "Drehen Sie die Drohne um 180° so dass die Propeller nach unten zeigen.",
        "Drehen Sie die Drohne um 90° nach links. Die linke Seite sollte nach unten zeigen.",
        "Drehen Sie die Drohne um 90° nach rechts. Die rechte Seite sollte nach unten zeigen.",
        "Heben Sie die Nase der Drohne an. Die Vorderseite sollte nach oben zeigen.",
        "Senken Sie die Nase der Drohne ab. Die Vorderseite sollte nach unten zeigen."
    ]
    
    // Funktion zum Setzen des Kalibrierungsschritts
    function setCalibrationStep(step) {
        if (step >= 0 && step < 6) {
            currentStep = step
            updateDroneOrientation()
            stepAnimation.start()
        }
    }
    
    // Funktion zum Aktualisieren der Drohnenausrichtung basierend auf dem aktuellen Schritt
    function updateDroneOrientation() {
        var targetX = 0
        var targetY = 0
        var targetZ = 0
        
        switch (currentStep) {
        case 0: // Z+ (flach)
            targetX = 0
            targetY = 0
            targetZ = 0
            break
        case 1: // Z- (auf dem Rücken)
            targetX = 180
            targetY = 0
            targetZ = 0
            break
        case 2: // X- (linke Seite)
            targetX = 0
            targetY = 0
            targetZ = -90
            break
        case 3: // X+ (rechte Seite)
            targetX = 0
            targetY = 0
            targetZ = 90
            break
        case 4: // Y+ (Nase nach oben)
            targetX = -90
            targetY = 0
            targetZ = 0
            break
        case 5: // Y- (Nase nach unten)
            targetX = 90
            targetY = 0
            targetZ = 0
            break
        }
        
        // Animation zu den Zielwerten
        angleXAnimation.to = targetX
        angleYAnimation.to = targetY
        angleZAnimation.to = targetZ
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
        
        // Kamera mit besserer Position
        PerspectiveCamera {
            id: camera
            position: Qt.vector3d(0, 150, 400)
            eulerRotation: Qt.vector3d(-20, 0, 0)
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
        
        // Drohnenmodell
        Model {
            id: droneModel
            source: "Assets/meshes/mk4_v2_10_mesh.mesh"
            scale: Qt.vector3d(0.4, 0.4, 0.4)
            eulerRotation: Qt.vector3d(root.angleX, root.angleY, root.angleZ)
            materials: [
                PrincipledMaterial {
                    baseColor: currentStep < 6 ? "#50c0ff" : "#66ff66"
                    roughness: 0.3
                    metalness: 0.7
                    emissiveFactor: currentStep < 6 ? Qt.rgba(0.1, 0.3, 0.8, 1.0) : Qt.rgba(0.2, 0.8, 0.2, 1.0)
                }
            ]
        }
        
        // Koordinatenachsen
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(30, 0, 0)
            eulerRotation: Qt.vector3d(0, 0, 90)
            scale: Qt.vector3d(0.3, 30, 0.3)
            materials: [PrincipledMaterial { baseColor: "#ff6666" }]
        }
        
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(0, 30, 0)
            scale: Qt.vector3d(0.3, 30, 0.3)
            materials: [PrincipledMaterial { baseColor: "#66ff66" }]
        }
        
        Model {
            source: "#Cylinder"
            position: Qt.vector3d(0, 0, 30)
            eulerRotation: Qt.vector3d(90, 0, 0)
            scale: Qt.vector3d(0.3, 30, 0.3)
            materials: [PrincipledMaterial { baseColor: "#6666ff" }]
        }
        
        // Hilfsebene für Orientierung
        Model {
            source: "#Rectangle"
            scale: Qt.vector3d(100, 100, 1)
            position: Qt.vector3d(0, -20, 0)
            eulerRotation: Qt.vector3d(-90, 0, 0)
            materials: [
                PrincipledMaterial {
                    baseColor: "#333333"
                    opacity: 0.4
                    alphaMode: PrincipledMaterial.Blend
                }
            ]
        }
        
        // Pfeile für die gewünschte Ausrichtung
        Model {
            visible: currentStep < 6
            source: "#Cone"
            position: Qt.vector3d(0, 40, 0)
            scale: Qt.vector3d(0.5, 1, 0.5)
            eulerRotation: Qt.vector3d(0, 0, 0)
            materials: [
                PrincipledMaterial {
                    baseColor: "#ffff00"
                    emissiveFactor: Qt.rgba(0.5, 0.5, 0, 1.0)
                }
            ]
        }
    }
    
    // Animationen für Übergänge
    ParallelAnimation {
        id: stepAnimation
        running: false
        
        NumberAnimation {
            id: angleXAnimation
            target: root
            property: "angleX"
            duration: 800
            easing.type: Easing.InOutQuad
        }
        
        NumberAnimation {
            id: angleYAnimation
            target: root
            property: "angleY"
            duration: 800
            easing.type: Easing.InOutQuad
        }
        
        NumberAnimation {
            id: angleZAnimation
            target: root
            property: "angleZ"
            duration: 800
            easing.type: Easing.InOutQuad
        }
    }
    
    // Anweisungs-Overlay
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 120
        color: Qt.rgba(0, 0, 0, 0.8)
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 5
            
            Text {
                text: "Schritt " + (currentStep + 1) + " von 6"
                color: "#66ccff"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 14
                font.bold: true
            }
            
            Text {
                text: currentStep < positionDescriptions.length
                      ? positionDescriptions[currentStep]
                      : "Kalibrierung abgeschlossen"
                color: "white"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 12
                wrapMode: Text.WordWrap
            }
            
            Text {
                text: currentStep < positionDetails.length ? positionDetails[currentStep] : ""
                color: "#cccccc"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 10
                wrapMode: Text.WordWrap
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
                text: Math.round(calibrationProgress * 100) + "% abgeschlossen"
                color: "white"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 11
            }
        }
    }
    
    // Schritt-Indikatoren
    RowLayout {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 10
        spacing: 5
        
        Repeater {
            model: 6
            
            Rectangle {
                Layout.fillWidth: true
                height: 4
                radius: 2
                color: {
                    if (index < currentStep) return "#66ff66"  // Abgeschlossen
                    if (index === currentStep) return "#ffff66"  // Aktuell
                    return "#666666"  // Noch nicht erreicht
                }
            }
        }
    }
}

/*##^##
Designer {
    D{i:0}D{i:1;cameraSpeed3d:25;cameraSpeed3dMultiplier:1}
}
##^##*/
