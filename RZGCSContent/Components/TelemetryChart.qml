import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    
    // Properties für die Chart-Daten
    property var sensorViewModel: null
    property string chartTitle: "Telemetry Chart"
    property string dataType: "altitude" // altitude, speed, battery, etc.
    property int maxDataPoints: 100
    property bool useOpenGL: true // GPU-Beschleunigung aktivieren
    property bool showDemoData: true // Zeige Demo-Daten, wenn kein sensorViewModel
    
    Component.onCompleted: {
        console.log("D: TelemetryChart.qml - Component.onCompleted")
        console.log("D: TelemetryChart - chartTitle:", chartTitle)
        console.log("D: TelemetryChart - dataType:", dataType)
        console.log("D: TelemetryChart - showDemoData:", showDemoData)
        console.log("D: TelemetryChart - width:", width)
        console.log("D: TelemetryChart - height:", height)
    }
    
    // Chart-Komponente mit GPU-Beschleunigung
    ChartView {
        id: chartView
        anchors.fill: parent
        antialiasing: true
        legend.visible: true
        legend.alignment: Qt.AlignBottom
        legend.labelColor: "#ffffff"
        
        // GPU-Beschleunigung aktivieren
        antialiasing: true
        
        Component.onCompleted: {
            console.log("D: ChartView Component.onCompleted")
            console.log("D: ChartView - anchors.fill:", anchors.fill)
            console.log("D: ChartView - antialiasing:", antialiasing)
        }
        
        // Demo-Daten für Tests
        ValueAxis {
            id: axisX
            min: 0
            max: 100
            tickCount: 11
            labelFormat: "%.0f"
            titleText: "Time (s)"
            titleVisible: true
            labelsColor: "#ffffff"
            titleColor: "#ffffff"
            gridLineColor: "#444444"
            lineColor: "#666666"
        }
        
        ValueAxis {
            id: axisY
            min: -50
            max: 150
            tickCount: 11
            labelFormat: "%.0f"
            titleText: dataType === "altitude" ? "Altitude (m)" : 
                      dataType === "speed" ? "Speed (m/s)" : 
                      dataType === "battery" ? "Voltage (V)" : "Value"
            titleVisible: true
            labelsColor: "#ffffff"
            titleColor: "#ffffff"
            gridLineColor: "#444444"
            lineColor: "#666666"
        }
        
        // Demo-LineSeries
        LineSeries {
            id: demoSeries
            name: chartTitle
            axisX: axisX
            axisY: axisY
            useOpenGL: root.useOpenGL
            color: "#4CAF50"
            width: 2
            
            Component.onCompleted: {
                console.log("D: LineSeries Component.onCompleted")
                console.log("D: LineSeries - useOpenGL:", useOpenGL)
                console.log("D: LineSeries - color:", color)
                
                // Demo-Daten generieren
                if (showDemoData) {
                    console.log("D: Generating demo data...")
                    for (let i = 0; i <= 100; i++) {
                        let value
                        if (dataType === "altitude") {
                            value = 50 + 50 * Math.sin(i * 0.1) + 20 * Math.cos(i * 0.05)
                        } else if (dataType === "speed") {
                            value = 10 + 5 * Math.sin(i * 0.2) + 3 * Math.cos(i * 0.1)
                        } else if (dataType === "battery") {
                            value = 12.6 - (i * 0.01) + 0.2 * Math.sin(i * 0.3)
                        } else {
                            value = 50 + 30 * Math.sin(i * 0.15)
                        }
                        demoSeries.append(i, value)
                    }
                    console.log("D: Demo data generated with", demoSeries.count, "points")
                }
            }
        }
    }
    
    // Timer für Demo-Animation
    Timer {
        id: demoTimer
        interval: 100 // 10 FPS
        running: showDemoData
        repeat: true
        
        onTriggered: {
            if (showDemoData && demoSeries.count > 0) {
                // Entferne den ersten Punkt und füge einen neuen hinzu
                demoSeries.remove(0)
                let lastX = demoSeries.at(demoSeries.count - 1).x
                let newX = lastX + 1
                let newValue
                
                if (dataType === "altitude") {
                    newValue = 50 + 50 * Math.sin(newX * 0.1) + 20 * Math.cos(newX * 0.05)
                } else if (dataType === "speed") {
                    newValue = 10 + 5 * Math.sin(newX * 0.2) + 3 * Math.cos(newX * 0.1)
                } else if (dataType === "battery") {
                    newValue = 12.6 - (newX * 0.01) + 0.2 * Math.sin(newX * 0.3)
                } else {
                    newValue = 50 + 30 * Math.sin(newX * 0.15)
                }
                
                demoSeries.append(newX, newValue)
                
                // Aktualisiere X-Achse
                axisX.min = Math.max(0, newX - 100)
                axisX.max = newX
            }
        }
    }
} 