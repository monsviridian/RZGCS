/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 800
    height: 600
    
    // Schwarzer Hintergrund für den gesamten Tab
    Rectangle {
        anchors.fill: parent
        color: "#000000" // Schwarz
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: "#000000"
            radius: 5
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 10
                
                Text {
                    text: qsTr("Sensor Data")
                    color: "white"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.fillWidth: true
                }
                
                Text {
                    id: updateTime
                    text: "Last Update: " + new Date().toLocaleTimeString()
                    color: "white"
                    font.pixelSize: 12
                }
                
                Timer {
                    interval: 500  // Schnellere Aktualisierung: 0.5s statt 1s
                    running: true
                    repeat: true
                    onTriggered: {
                        updateTime.text = "Letzte Aktualisierung: " + new Date().toLocaleTimeString()
                        // Workaround, um das SensorModel zu "triggern"
                        sensorgrid.model = null
                        sensorgrid.model = sensorModel
                    }
                }
            }
        }
        
        // Sensor Grid
        GridView {
            id: sensorgrid
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            cellWidth: 200
            cellHeight: 100

            model: sensorModel

            delegate: Rectangle {
                width: sensorgrid.cellWidth - 10
                height: sensorgrid.cellHeight - 10
                color: "#1d1d1d"
                radius: 5
                border.color: "#0d52a4"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 5
                    spacing: 2

                    Text {
                        text: model.name
                        color: "#ffffff"
                        font.pixelSize: 14
                        font.bold: true
                        Layout.fillWidth: true
                    }

                    Text {
                        text: model.value + " " + model.unit
                        color: "#00ff00"
                        font.pixelSize: 20
                        font.bold: true
                        Layout.fillWidth: true
                    }
                    
                    // Fortschrittsbalken für Werte, die Prozent darstellen
                    Rectangle {
                        visible: model.unit === "%"
                        Layout.fillWidth: true
                        height: 5
                        color: "#333333"
                        radius: 2
                        
                        Rectangle {
                            width: parent.width * (model.value / 100)
                            height: parent.height
                            color: model.value > 20 ? "#00ff00" : "#ff0000"
                            radius: 2
                        }
                    }
                }
            }

            ScrollBar.vertical: ScrollBar {
                active: true
                policy: ScrollBar.AsNeeded
            }

            ScrollBar.horizontal: ScrollBar {
                active: true
                policy: ScrollBar.AsNeeded
            }
        }
    }
}
