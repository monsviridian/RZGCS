import QtQuick
import QtQuick.Controls
import QtQuick.Window

Window {
    id: testWindow
    width: 800
    height: 600
    visible: true
    title: "System Info Logs Test"
    
    Rectangle {
        id: logArea
        anchors.fill: parent
        color: "#121212"
        
        Column {
            id: header
            width: parent.width
            height: 50
            
            Text {
                text: "System Info Logs Test"
                color: "white"
                font.pixelSize: 20
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }
        
        ListView {
            id: logsList
            anchors.top: header.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 10
            clip: true
            spacing: 5
            
            // Hier verwenden wir logger.system_info_logs direkt
            model: logger ? logger.system_info_logs : []
            
            delegate: Rectangle {
                width: logsList.width
                height: logText.height + 10
                color: index % 2 === 0 ? "#2d2d2d" : "#252525"
                
                Text {
                    id: logText
                    text: modelData
                    color: "white"
                    font.family: "Consolas, 'Courier New', monospace"
                    font.pixelSize: 16
                    wrapMode: Text.WordWrap
                    width: parent.width - 20
                    anchors {
                        left: parent.left
                        leftMargin: 10
                        verticalCenter: parent.verticalCenter
                    }
                }
            }
            
            ScrollBar.vertical: ScrollBar {
                active: true
                policy: ScrollBar.AsNeeded
            }
        }
        
        // Debug-Bereich
        Rectangle {
            id: debugArea
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 100
            color: "#333333"
            
            Column {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5
                
                Text {
                    text: "Debug-Informationen:"
                    color: "white"
                    font.bold: true
                }
                
                Text {
                    text: logger ? "Logger ist verfügbar" : "Logger ist NICHT verfügbar"
                    color: logger ? "green" : "red"
                }
                
                Text {
                    text: logger && logger.system_info_logs ? 
                          "System-Info-Logs: " + logger.system_info_logs.length : 
                          "Keine System-Info-Logs verfügbar"
                    color: "white"
                }
                
                Button {
                    text: "Test-Log hinzufügen"
                    onClicked: {
                        if (logger) {
                            logger.addSystemInfoLog("Test: " + new Date().toLocaleTimeString())
                        }
                    }
                }
            }
        }
    }
    
    // Zum Testen
    Component.onCompleted: {
        if (logger) {
            console.log("Logger ist verfügbar")
            console.log("Anzahl der System-Info-Logs: " + logger.system_info_logs.length)
        } else {
            console.log("Logger ist NICHT verfügbar")
        }
    }
}
