import QtQuick
import QtQuick3D
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 800
    height: 600
    
    View3D {
        id: view3D
        anchors.fill: parent
        
        environment: SceneEnvironment {
            clearColor: "#1a1a1a"
            backgroundMode: SceneEnvironment.Color
            antialiasingMode: SceneEnvironment.MSAA
            antialiasingQuality: SceneEnvironment.High
        }
        
        // Kamera mit besserer Position für Drohnenansicht
        PerspectiveCamera {
            id: camera
            position: Qt.vector3d(0, 120, 600)  // Deutlich weiter hinten für bessere Übersicht
            eulerRotation: Qt.vector3d(-10, 0, 0)  // Flacherer Winkel
            clipFar: 2000
            clipNear: 1
            
            // Animation der Kamera nach der Partikelanimation
            SequentialAnimation {
                id: cameraAnimation
                running: false
                
                PauseAnimation { duration: 4000 } // Warten bis Drohne erscheint
                ParallelAnimation {
                    NumberAnimation {
                        target: camera
                        property: "position.y"
                        to: 100  // Nicht so weit nach unten
                        duration: 2000
                        easing.type: Easing.InOutQuad
                    }
                    NumberAnimation {
                        target: camera
                        property: "position.z"
                        to: 500  // Weiter weg bleiben
                        duration: 2000
                        easing.type: Easing.InOutQuad
                    }
                }
            }
        }
        
        // Beleuchtung
        DirectionalLight {
            eulerRotation: Qt.vector3d(-30, -30, 0)
            brightness: 1.0
            ambientColor: Qt.rgba(0.1, 0.1, 0.1, 1.0)
        }
        
        DirectionalLight {
            eulerRotation: Qt.vector3d(45, 45, 0)
            brightness: 0.5
        }
        
        // Hintergrund mit topografischen Linien
        Model {
            source: "#Rectangle"
            scale: Qt.vector3d(500, 500, 1)
            position: Qt.vector3d(0, 0, -100)
            materials: [
                PrincipledMaterial {
                    baseColorMap: Texture {
                        source: "Assets/overlay.png"
                    }
                    opacity: 0.15
                    alphaMode: PrincipledMaterial.Blend
                }
            ]
        }
        
        // Hilfsebene für Orientierung
        Model {
            source: "#Rectangle"
            scale: Qt.vector3d(150, 150, 1)
            position: Qt.vector3d(0, -25, 0)
            eulerRotation: Qt.vector3d(-90, 0, 0)
            materials: [PrincipledMaterial { 
                baseColor: "#303030"
                opacity: 0.3
                alphaMode: PrincipledMaterial.Blend
            }]
        }
        
        // Die Drohne selbst (wird erst später eingeblendet)
        Model {
            id: droneModel
            source: "Assets/meshes/mk4_v2_10_mesh.mesh"
            scale: Qt.vector3d(2.0, 2.0, 2.0)  // Kleinere Skalierung für bessere Proportionen
            opacity: 0.0
            position: Qt.vector3d(0, 0, 0)  // Zentriert im Sichtfeld
            
            materials: [
                PrincipledMaterial {
                    baseColor: "#50c0ff"  // Helleres, kräftigeres Blau für bessere Sichtbarkeit
                    roughness: 0.1
                    metalness: 0.9
                    emissiveFactor: Qt.rgba(0.2, 0.4, 0.8, 1.0)  // Stärkeres Glühen
                }
            ]
            
            // Animation für das Einblenden der Drohne
            SequentialAnimation {
                id: droneAppearAnimation
                running: false
                
                // Kurz warten, bis sich die Partikel positioniert haben
                PauseAnimation { duration: 3000 }
                
                // Parallele Animationen für verschiedene Eigenschaften
                ParallelAnimation {
                    // Einblenden
                    NumberAnimation { 
                        target: droneModel
                        property: "opacity"
                        from: 0.0
                        to: 1.0
                        duration: 1500
                        easing.type: Easing.InOutQuad
                    }
                    
                    // Leichte Skalierungsanimation für mehr Aufmerksamkeit
                    NumberAnimation {
                        target: droneModel
                        property: "scale.x"
                        from: 1.5
                        to: 2.0
                        duration: 2000
                        easing.type: Easing.OutElastic
                    }
                    NumberAnimation {
                        target: droneModel
                        property: "scale.y"
                        from: 1.5
                        to: 2.0
                        duration: 2000
                        easing.type: Easing.OutElastic
                    }
                    NumberAnimation {
                        target: droneModel
                        property: "scale.z"
                        from: 1.5
                        to: 2.0
                        duration: 2000
                        easing.type: Easing.OutElastic
                    }
                    
                    // Leichte Rotation für visuellen Effekt
                    NumberAnimation {
                        target: droneModel
                        property: "eulerRotation.y"
                        from: -30
                        to: 0
                        duration: 2000
                        easing.type: Easing.OutBack
                    }
                }
                
                // Langsame Rotationsanimation nach dem Erscheinen für bessere Sichtbarkeit
                SequentialAnimation {
                    PauseAnimation { duration: 2000 }
                    NumberAnimation {
                        target: droneModel
                        property: "eulerRotation.y"
                        from: 0
                        to: 360
                        duration: 20000
                        loops: Animation.Infinite
                    }
                }
            }
        }
        
        // Container für Partikel
        Node {
            id: particlesNode
            property bool animationActive: false
            
            // Einfacher Ansatz mit vordefinierten Partikeln
            Component.onCompleted: {
                // Wir generieren die Partikel sofort und starten die Animation automatisch
                createParticles();
                // Automatisch Animation starten
                startAnimation();
            }
            
            // Button-Handler zum Start der Animation
            function startAnimation() {
                if (!animationActive) {
                    // Animation der Drohne starten
                    droneAppearAnimation.running = true;
                    
                    // Kameraanimation starten
                    cameraAnimation.running = true;
                    
                    // Alle Kinder (Partikel) animieren
                    for (var i = 0; i < particlesNode.children.length; i++) {
                        var particle = particlesNode.children[i];
                        // Nur Partikel mit startParticleAnimation-Methode animieren
                        if (typeof particle.startParticleAnimation === "function") {
                            particle.startParticleAnimation();
                        }
                    }
                    
                    animationActive = true;
                }
            }
            
            function createParticles() {
                // Anzahl der Partikel
                var particleCount = 150;
                
                // Erzeugen der Partikel
                for (var i = 0; i < particleCount; i++) {
                    var particle = particleComponent.createObject(particlesNode);
                    
                    // Zufällige Startposition im Raum
                    var startX = (Math.random() * 400) - 200;
                    var startY = (Math.random() * 400) - 200;
                    var startZ = (Math.random() * 400) - 200;
                    
                    // Endposition (zur Drohne hin)
                    var endX = (Math.random() * 40) - 20;
                    var endY = (Math.random() * 40) - 20;
                    var endZ = (Math.random() * 40) - 20;
                    
                    // Zufällige Verzögerung für die Animation
                    var delay = Math.random() * 1000;
                    
                    // Zufällige Farbe (Blau-/Türkistöne)
                    var r = 0.1 + Math.random() * 0.2;
                    var g = 0.5 + Math.random() * 0.4;
                    var b = 0.7 + Math.random() * 0.3;
                    
                    // Zufällige Größe
                    var scale = 0.1 + Math.random() * 0.2;
                    
                    // Partikel konfigurieren
                    particle.position = Qt.vector3d(startX, startY, startZ);
                    particle.endPosition = Qt.vector3d(endX, endY, endZ);
                    particle.customDelay = delay;
                    
                    // Material und Größe anpassen
                    if (particle.customMaterial) {
                        particle.customMaterial.baseColor = Qt.rgba(r, g, b, 1.0);
                        particle.customMaterial.emissiveFactor = Qt.rgba(r*0.5, g*0.5, b*0.5, 1.0);
                    }
                    
                    particle.scale = Qt.vector3d(scale, scale*10, scale);
                }
            }
        }
        
        // Vereinfachtes Partikel-Modell
        Component {
            id: particleComponent
            
            Model {
                // Eigenschaften für Animation
                property vector3d endPosition: Qt.vector3d(0, 0, 0)
                property int customDelay: 0
                property PrincipledMaterial customMaterial: PrincipledMaterial {
                    baseColor: "#66ccff"
                    emissiveFactor: Qt.rgba(0.2, 0.5, 0.8, 1.0)
                    emissiveMap: Texture { source: "Assets/overlay.png" }
                    alphaMode: PrincipledMaterial.Blend
                    opacity: 0.7
                }
                
                source: "#Cube"
                materials: [ customMaterial ]
                
                // Funktion zum Starten der Animation
                function startParticleAnimation() {
                    // Position direkter animieren
                    animX.to = endPosition.x;
                    animX.duration = 2000 + Math.random() * 1000;
                    
                    animY.to = endPosition.y;
                    animY.duration = 2000 + Math.random() * 1000;
                    
                    animZ.to = endPosition.z;
                    animZ.duration = 2000 + Math.random() * 1000;
                    
                    // Animationen starten
                    xAnim.running = true;
                    yAnim.running = true;
                    zAnim.running = true;
                    
                    // Rotation starten
                    rotX.running = true;
                    rotY.running = true;
                    
                    // Ausblenden nach Animation
                    fadeOutTimer.start();
                }
                
                // Separate Animationen für X, Y, Z - einfacher zu debuggen
                SequentialAnimation {
                    id: xAnim
                    running: false
                    
                    PauseAnimation { duration: customDelay }
                    NumberAnimation {
                        id: animX
                        target: parent
                        property: "position.x"
                        to: 0 // wird in startParticleAnimation gesetzt
                        duration: 2000
                        easing.type: Easing.InOutQuad
                    }
                }
                
                SequentialAnimation {
                    id: yAnim
                    running: false
                    
                    PauseAnimation { duration: customDelay }
                    NumberAnimation {
                        id: animY
                        target: parent
                        property: "position.y"
                        to: 0 // wird in startParticleAnimation gesetzt
                        duration: 2000
                        easing.type: Easing.InOutQuad
                    }
                }
                
                SequentialAnimation {
                    id: zAnim
                    running: false
                    
                    PauseAnimation { duration: customDelay }
                    NumberAnimation {
                        id: animZ
                        target: parent
                        property: "position.z"
                        to: 0 // wird in startParticleAnimation gesetzt
                        duration: 2000
                        easing.type: Easing.InOutQuad
                    }
                }
                
                // Rotationen
                NumberAnimation {
                    id: rotX
                    running: false
                    target: parent
                    property: "eulerRotation.x"
                    from: Math.random() * 360
                    to: Math.random() * 360
                    duration: 3000
                    easing.type: Easing.InOutQuad
                }
                
                NumberAnimation {
                    id: rotY
                    running: false
                    target: parent
                    property: "eulerRotation.y"
                    from: Math.random() * 360
                    to: Math.random() * 360
                    duration: 3000
                    easing.type: Easing.InOutQuad
                }
                
                // Timer zum Ausblenden der Partikel
                Timer {
                    id: fadeOutTimer
                    interval: 3500  // Nach 3,5 Sekunden ausblenden (nach Positionierung)
                    running: false
                    onTriggered: {
                        // Partikel langsam ausblenden
                        opacityAnim.running = true;
                    }
                }
                
                // Animation zum Ausblenden
                NumberAnimation {
                    id: opacityAnim
                    target: parent
                    property: "opacity"
                    from: parent.opacity
                    to: 0.0
                    duration: 1000
                    easing.type: Easing.InOutQuad
                }
            }
        }
    }
    
    // Start-Button versteckt, da Animation automatisch startet
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 20
        width: 180
        height: 50
        color: "#2c3e50"
        radius: 5
        visible: false  // Button verstecken
        
        Text {
            anchors.centerIn: parent
            text: "Animation starten"
            color: "white"
            font.pixelSize: 16
            font.bold: true
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: {
                particlesNode.startAnimation();
            }
        }
    }
}
