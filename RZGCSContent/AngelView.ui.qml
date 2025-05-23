import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var controller: null  // Controller-Referenz, die von außen gesetzt werden kann
    
    Rectangle {
        anchors.fill: parent
        color: "#2c2c2c"
        
        // Fullscreen Terrain Visualization
        Image {
            id: terrainImage
            anchors.fill: parent
            source: "file:///C:/Users/fuckheinerkleinehack/Documents/RZGS2/RZGCS/Assets/render.png"
            fillMode: Image.PreserveAspectFit
            
            // Schwarzer Punkt für Drohnenposition
            Rectangle {
                id: droneMarker
                width: 12
                height: 12
                radius: 6
                color: "black"
                border.color: "white"
                border.width: 2
                x: parent.width * 0.6 - width/2  // Position auf dem Terrain
                y: parent.height * 0.4 - height/2
            }
            
            // Kreisförmige Flugpfade
            Canvas {
                id: pathCanvas
                anchors.fill: parent
                
                // Relative Positionen auf der Karte 
                // (basierend auf dem render.png Bild und relativen Bildschirmkoordinaten)
                property var ukrainePos: {"x": 0.75, "y": 0.35}  // Position in der Ukraine
                property var europePos: {"x": 0.45, "y": 0.28}  // Position in Europa (z.B. Deutschland)
                property var turkeyPos: {"x": 0.65, "y": 0.48}  // Position in der Türkei
                property var africaPos: {"x": 0.35, "y": 0.55}  // Position in Nordafrika
                property var russiaPos: {"x": 0.85, "y": 0.2}   // Position in Russland
                property var balticPos: {"x": 0.62, "y": 0.25}  // Position im Baltikum
                property var ukPos: {"x": 0.40, "y": 0.19}     // Position in Großbritannien
                property var mideastPos: {"x": 0.75, "y": 0.58} // Position im Nahen Osten
                property real ukraineRadius: 60
                property real europeRadius: 80
                property real turkeyRadius: 50
                property real africaRadius: 70
                property real russiaRadius: 90
                property real balticRadius: 45
                property real ukRadius: 35
                property real mideastRadius: 65
                
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.clearRect(0, 0, width, height);
                    
                    // Position 1: Ukraine
                    var ukraineCenterX = width * ukrainePos.x;
                    var ukraineCenterY = height * ukrainePos.y;
                    
                    // Punkt für Ukraine
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(ukraineCenterX, ukraineCenterY, 5, 0, Math.PI * 2, false);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    // Flugpfad für Ukraine
                    ctx.strokeStyle = "#ff6666";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(ukraineCenterX, ukraineCenterY, ukraineRadius, 0, Math.PI * 2, false);
                    ctx.stroke();
                    
                    // Position 2: Europa
                    var europeCenterX = width * europePos.x;
                    var europeCenterY = height * europePos.y;
                    
                    // Punkt für Europa
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(europeCenterX, europeCenterY, 5, 0, Math.PI * 2, false);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    // Flugpfad für Europa
                    ctx.strokeStyle = "#66ccff";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(europeCenterX, europeCenterY, europeRadius, 0, Math.PI * 2, false);
                    ctx.stroke();
                    
                    // Position 3: Türkei
                    var turkeyCenterX = width * turkeyPos.x;
                    var turkeyCenterY = height * turkeyPos.y;
                    
                    // Punkt für Türkei
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(turkeyCenterX, turkeyCenterY, 5, 0, Math.PI * 2, false);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    // Flugpfad für Türkei
                    ctx.strokeStyle = "#ffcc66";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(turkeyCenterX, turkeyCenterY, turkeyRadius, 0, Math.PI * 2, false);
                    ctx.stroke();
                    
                    // Position 4: Afrika
                    var africaCenterX = width * africaPos.x;
                    var africaCenterY = height * africaPos.y;
                    
                    // Punkt für Afrika
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(africaCenterX, africaCenterY, 5, 0, Math.PI * 2, false);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    // Flugpfad für Afrika
                    ctx.strokeStyle = "#66ff99";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(africaCenterX, africaCenterY, africaRadius, 0, Math.PI * 2, false);
                    ctx.stroke();
                    
                    // Position 5: Russland
                    var russiaCenterX = width * russiaPos.x;
                    var russiaCenterY = height * russiaPos.y;
                    
                    // Punkt für Russland
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(russiaCenterX, russiaCenterY, 5, 0, Math.PI * 2, false);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    // Flugpfad für Russland
                    ctx.strokeStyle = "#cc66cc";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(russiaCenterX, russiaCenterY, russiaRadius, 0, Math.PI * 2, false);
                    ctx.stroke();
                    
                    // Position 6: Baltikum
                    var balticCenterX = width * balticPos.x;
                    var balticCenterY = height * balticPos.y;
                    
                    // Punkt für Baltikum
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(balticCenterX, balticCenterY, 5, 0, Math.PI * 2, false);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    // Flugpfad für Baltikum
                    ctx.strokeStyle = "#ff9933";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(balticCenterX, balticCenterY, balticRadius, 0, Math.PI * 2, false);
                    ctx.stroke();
                    
                    // Position 7: Großbritannien
                    var ukCenterX = width * ukPos.x;
                    var ukCenterY = height * ukPos.y;
                    
                    // Punkt für Großbritannien
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(ukCenterX, ukCenterY, 5, 0, Math.PI * 2, false);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    // Flugpfad für Großbritannien
                    ctx.strokeStyle = "#33cccc";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(ukCenterX, ukCenterY, ukRadius, 0, Math.PI * 2, false);
                    ctx.stroke();
                    
                    // Position 8: Naher Osten
                    var mideastCenterX = width * mideastPos.x;
                    var mideastCenterY = height * mideastPos.y;
                    
                    // Punkt für Nahen Osten
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(mideastCenterX, mideastCenterY, 5, 0, Math.PI * 2, false);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    
                    // Flugpfad für Nahen Osten
                    ctx.strokeStyle = "#cc3300";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(mideastCenterX, mideastCenterY, mideastRadius, 0, Math.PI * 2, false);
                    ctx.stroke();
                }
                
                Component.onCompleted: {
                    requestPaint();
                }
            }
        }
    }
}
