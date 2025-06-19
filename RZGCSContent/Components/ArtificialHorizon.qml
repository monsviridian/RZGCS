import QtQuick 2.15
import QtQuick.Controls 2.15

/**
 * ArtificialHorizon - Vereinfachte Version des künstlichen Horizonts
 * Zeigt Pitch und Roll als visuelle Fluginstrumentenanzeige an
 */
Item {
    id: artificialHorizon
    width: 300
    height: 300
    
    // Eingabe-Eigenschaften für Roll und Pitch
    property real roll: 0.0
    property real pitch: 0.0
    property bool disarmed: true
    
    // Skalierungseigenschaften
    property real pitchScale: 2.0 // 2.0 bedeutet 10 Grad Pitch entsprechen 20 Pixeln
    
    // Farben
    property color skyColor: "#3399ff"
    property color groundColor: "#996600"
    property color lineColor: "white"
    
    // Hintergrundkreis (Bezel)
    Rectangle {
        id: bezel
        anchors.fill: parent
        radius: width/2
        color: "#222222"
        border.color: "#444444"
        border.width: 2
        
        // Äußerer Rand für bessere Sichtbarkeit
        Rectangle {
            id: outerRing
            anchors.centerIn: parent
            width: parent.width - 10
            height: width
            radius: width/2
            color: "transparent"
            border.color: "#666666"
            border.width: 1
        }
        
        // Runde Clipping-Maske für den Horizont
        Rectangle {
            id: clipItem
            anchors.centerIn: parent
            width: parent.width - 20
            height: width
            radius: width/2
            clip: true
            color: "transparent"
            
            // Horizont-Element
            Item {
                id: horizonItem
                width: parent.width * 4
                height: parent.height * 4
                anchors.centerIn: parent
                
                // Rotation und Translation für Roll/Pitch
                transform: [
                    Rotation {
                        angle: -roll
                        origin.x: horizonItem.width / 2
                        origin.y: horizonItem.height / 2
                    },
                    Translate {
                        y: pitch * pitchScale
                    }
                ]
                
                // Himmel (obere Hälfte)
                Rectangle {
                    id: skyRect
                    width: parent.width
                    height: parent.height / 2
                    color: skyColor
                    anchors {
                        top: parent.top
                        left: parent.left
                        right: parent.right
                    }
                }
                
                // Boden (untere Hälfte)
                Rectangle {
                    id: groundRect
                    width: parent.width
                    height: parent.height / 2
                    color: groundColor
                    anchors {
                        bottom: parent.bottom
                        left: parent.left
                        right: parent.right
                    }
                }
                
                // Horizont-Linie (Trennlinie zwischen Himmel und Boden)
                Rectangle {
                    id: horizonLine
                    width: parent.width
                    height: 2
                    color: "white"
                    anchors.centerIn: parent
                    opacity: 0.7
                }
                
                // Pitch-Markierungen
                Repeater {
                    model: 18 // 9 Linien nach oben und 9 nach unten, in 10-Grad-Intervallen
                    Rectangle {
                        id: pitchLine
                        property int pitchDegrees: (index - 9) * 10
                        width: pitchDegrees % 30 == 0 ? 60 : 40 // Längere Linie alle 30 Grad
                        height: 2
                        color: lineColor
                        x: (horizonItem.width - width) / 2
                        y: horizonItem.height / 2 - pitchDegrees * pitchScale - height / 2
                        visible: pitchDegrees != 0 // 0-Grad-Linie nicht anzeigen, da wir die Horizont-Linie haben
                        
                        // Pitch-Werte-Text
                        Text {
                            visible: pitchDegrees % 20 == 0 && pitchDegrees != 0 // Nur Zahlen in 20-Grad-Intervallen anzeigen
                            text: Math.abs(pitchDegrees)
                            color: lineColor
                            font.pixelSize: 12
                            font.bold: true
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: pitchDegrees > 0 ? parent.right : undefined
                            anchors.right: pitchDegrees < 0 ? parent.left : undefined
                            anchors.margins: 4
                        }
                    }
                }
            }
        }
        
        // Flugzeugsymbol (statisch)
        Canvas {
            id: aircraftSymbol
            anchors.fill: parent
            
            onPaint: {
                var ctx = getContext("2d");
                var centerX = width / 2;
                var centerY = height / 2;
                var size = width / 10;
                
                ctx.reset();
                ctx.strokeStyle = "yellow";
                ctx.lineWidth = 3;
                
                // Flugzeugsymbol zeichnen (vereinfacht)
                ctx.beginPath();
                // Flügel
                ctx.moveTo(centerX - size * 3, centerY);
                ctx.lineTo(centerX + size * 3, centerY);
                // Rumpf
                ctx.moveTo(centerX, centerY - size * 2);
                ctx.lineTo(centerX, centerY + size);
                ctx.stroke();
            }
        }
        
        // Roll-Markierungen am Rand
        Canvas {
            id: rollIndicators
            anchors.fill: parent
            
            onPaint: {
                var ctx = getContext("2d");
                var centerX = width / 2;
                var centerY = height / 2;
                var radius = width / 2 - 15;
                
                ctx.reset();
                ctx.strokeStyle = "white";
                ctx.lineWidth = 2;
                
                // Skalenstriche für Roll-Referenz zeichnen
                for (var i = -6; i <= 6; i++) {
                    var angle = i * 15 * Math.PI / 180; // 15-Grad-Schritte
                    var startRadius = i % 2 === 0 ? radius - 10 : radius - 5;
                    
                    ctx.beginPath();
                    ctx.moveTo(
                        centerX + startRadius * Math.sin(angle),
                        centerY - startRadius * Math.cos(angle)
                    );
                    ctx.lineTo(
                        centerX + radius * Math.sin(angle),
                        centerY - radius * Math.cos(angle)
                    );
                    ctx.stroke();
                }
            }
        }
        
        // Roll-Pfeilanzeige
        Canvas {
            id: rollArrow
            anchors.fill: parent
            
            onPaint: {
                var ctx = getContext("2d");
                var centerX = width / 2;
                var centerY = height / 2;
                var radius = width / 2 - 25;
                var angle = -roll * Math.PI / 180;
                
                ctx.reset();
                ctx.fillStyle = "yellow";
                
                // Pfeil zeichnen
                ctx.beginPath();
                ctx.moveTo(
                    centerX + radius * Math.sin(angle),
                    centerY - radius * Math.cos(angle)
                );
                ctx.lineTo(
                    centerX + (radius - 10) * Math.sin(angle - 0.1),
                    centerY - (radius - 10) * Math.cos(angle - 0.1)
                );
                ctx.lineTo(
                    centerX + (radius - 10) * Math.sin(angle + 0.1),
                    centerY - (radius - 10) * Math.cos(angle + 0.1)
                );
                ctx.closePath();
                ctx.fill();
            }
        }
        
        // DISARMED-Text bei Bedarf
        Text {
            anchors.centerIn: parent
            text: "DISARMED"
            visible: disarmed
            color: "red"
            font.pixelSize: 32
            font.bold: true
            style: Text.Outline
            styleColor: "white"
        }
    }
    
    // Aktualisieren der Canvas bei Änderungen von Roll oder Pitch
    onRollChanged: {
        aircraftSymbol.requestPaint();
        rollIndicators.requestPaint();
        rollArrow.requestPaint();
    }
    
    onPitchChanged: {
        aircraftSymbol.requestPaint();
    }
}
