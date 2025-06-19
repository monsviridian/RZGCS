import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * EnvironmentPanel - Displays environmental conditions for SITL simulation
 * Shows wind speed/direction, turbulence, and temperature
 */
Rectangle {
    id: root
    color: "#333333"
    radius: 4
    
    // Properties
    property real windSpeed: 0.0
    property real windDirection: 0.0
    property real turbulence: 0.0
    property real temperature: 25.0
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8
        
        // Title
        Label {
            text: "Environmental Conditions"
            font.pixelSize: 14
            font.bold: true
            color: "#FFFFFF"
            Layout.fillWidth: true
        }
        
        // Wind speed and direction
        GridLayout {
            columns: 2
            Layout.fillWidth: true
            
            Label {
                text: "Wind Speed:"
                color: "#CCCCCC"
                font.pixelSize: 12
            }
            
            Label {
                text: windSpeed.toFixed(1) + " m/s"
                color: getWindColor(windSpeed)
                font.pixelSize: 12
                font.bold: true
            }
            
            Label {
                text: "Wind Direction:"
                color: "#CCCCCC"
                font.pixelSize: 12
            }
            
            Label {
                text: windDirection.toFixed(0) + "°"
                color: "#FFFFFF"
                font.pixelSize: 12
                font.bold: true
            }
            
            Label {
                text: "Turbulence:"
                color: "#CCCCCC"
                font.pixelSize: 12
            }
            
            Label {
                text: turbulence.toFixed(0) + "%"
                color: getTurbulenceColor(turbulence)
                font.pixelSize: 12
                font.bold: true
            }
            
            Label {
                text: "Temperature:"
                color: "#CCCCCC"
                font.pixelSize: 12
            }
            
            Label {
                text: temperature.toFixed(1) + "°C"
                color: getTemperatureColor(temperature)
                font.pixelSize: 12
                font.bold: true
            }
        }
        
        // Wind direction indicator
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            
            Rectangle {
                anchors.centerIn: parent
                width: Math.min(parent.width, parent.height) * 0.8
                height: width
                radius: width / 2
                color: "#222222"
                border.color: "#444444"
                border.width: 1
                
                // North marker
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: 2
                    text: "N"
                    color: "#FFFFFF"
                    font.pixelSize: 10
                }
                
                // Wind direction arrow
                Canvas {
                    id: windDirectionCanvas
                    anchors.fill: parent
                    
                    onPaint: {
                        var ctx = getContext("2d");
                        var centerX = width / 2;
                        var centerY = height / 2;
                        var radius = Math.min(width, height) / 2 - 10;
                        
                        // Clear canvas
                        ctx.reset();
                        
                        // Convert wind direction to radians (0° is North, increases clockwise)
                        // Need to adjust because canvas uses 0° as East, increasing counterclockwise
                        var windRad = (90 - windDirection) * Math.PI / 180;
                        
                        // Start point (center)
                        var startX = centerX;
                        var startY = centerY;
                        
                        // End point
                        var endX = centerX + Math.cos(windRad) * radius;
                        var endY = centerY - Math.sin(windRad) * radius;
                        
                        // Draw arrow line
                        ctx.beginPath();
                        ctx.moveTo(startX, startY);
                        ctx.lineTo(endX, endY);
                        ctx.lineWidth = 2;
                        ctx.strokeStyle = getWindColor(windSpeed);
                        ctx.stroke();
                        
                        // Draw arrowhead
                        var headLength = 10;
                        var angle = Math.atan2(startY - endY, startX - endX);
                        
                        ctx.beginPath();
                        ctx.moveTo(endX, endY);
                        ctx.lineTo(
                            endX - headLength * Math.cos(angle - Math.PI/6),
                            endY - headLength * Math.sin(angle - Math.PI/6)
                        );
                        ctx.lineTo(
                            endX - headLength * Math.cos(angle + Math.PI/6),
                            endY - headLength * Math.sin(angle + Math.PI/6)
                        );
                        ctx.closePath();
                        ctx.fillStyle = getWindColor(windSpeed);
                        ctx.fill();
                    }
                }
            }
        }
    }
    
    // Update wind direction indicator when values change
    onWindDirectionChanged: windDirectionCanvas.requestPaint()
    onWindSpeedChanged: windDirectionCanvas.requestPaint()
    
    // Helper functions for colors
    function getWindColor(speed) {
        if (speed < 5.0) return "#00FF00";      // Light green for calm
        else if (speed < 10.0) return "#FFFF00"; // Yellow for moderate
        else if (speed < 15.0) return "#FFA500"; // Orange for strong
        else return "#FF0000";                   // Red for very strong
    }
    
    function getTurbulenceColor(turbulence) {
        if (turbulence < 20.0) return "#00FF00";      // Light green for calm
        else if (turbulence < 50.0) return "#FFFF00"; // Yellow for moderate
        else if (turbulence < 70.0) return "#FFA500"; // Orange for strong
        else return "#FF0000";                        // Red for severe
    }
    
    function getTemperatureColor(temp) {
        if (temp < 0.0) return "#00FFFF";       // Cyan for below freezing
        else if (temp < 15.0) return "#0088FF"; // Light blue for cold
        else if (temp < 25.0) return "#00FF00"; // Green for moderate
        else if (temp < 35.0) return "#FFFF00"; // Yellow for warm
        else return "#FF0000";                  // Red for hot
    }
}
