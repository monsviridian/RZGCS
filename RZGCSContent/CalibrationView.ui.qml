import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var controller: null
    
    Rectangle {
        anchors.fill: parent
        color: "#2c2c2c"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15
            
            // Heading
            Text {
                Layout.fillWidth: true
                text: "Calibration"
                font.pixelSize: 24
                font.bold: true
                color: "white"
            }
            
            // Description
            Text {
                Layout.fillWidth: true
                text: "Calibrate the sensors and systems of your drone."
                font.pixelSize: 16
                color: "#cccccc"
                wrapMode: Text.WordWrap
            }
            
            // Separator line
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#555555"
                Layout.topMargin: 10
                Layout.bottomMargin: 10
            }
            
            // Main content with tabs
            TabBar {
                id: calibrationTabBar
                Layout.fillWidth: true
                
                TabButton {
                    text: "Compass"
                    width: implicitWidth
                }
                
                TabButton {
                    text: "Accelerometer"
                    width: implicitWidth
                }
                
                TabButton {
                    text: "Gyroscope"
                    width: implicitWidth
                }
                
                TabButton {
                    text: "RC Remote Control"
                    width: implicitWidth
                }
            }
            
            // Stack view for tabs
            StackLayout {
                id: calibrationStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: calibrationTabBar.currentIndex
                
                // Kompass-Kalibrierung
                Item {
                    id: compassCalibration
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 15
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Kompass-Kalibrierung"
                            font.pixelSize: 18
                            font.bold: true
                            color: "white"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Drehen Sie die Drohne langsam in alle Richtungen, um den Kompass zu kalibrieren."
                            wrapMode: Text.WordWrap
                            color: "#cccccc"
                        }
                        
                        // Visuelle Darstellung der Kalibrierung
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 200
                            color: "#3c3c3c"
                            border.color: "#555555"
                            border.width: 1
                            
                            // Hier kann später eine visuelle Darstellung eingefügt werden
                            Text {
                                anchors.centerIn: parent
                                text: "Visuelle Darstellung der Kompass-Kalibrierung"
                                color: "#aaaaaa"
                            }
                        }
                        
                        // Fortschrittsanzeige
                        ProgressBar {
                            id: compassProgress
                            Layout.fillWidth: true
                            value: 0.0
                        }
                        
                        // Aktionsschaltflächen
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10
                            
                            Button {
                                text: "Starten"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.startCompassCalibration();
                                    }
                                }
                            }
                            
                            Button {
                                text: "Abbrechen"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.cancelCalibration();
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Beschleunigungssensor-Kalibrierung
                Item {
                    id: accelCalibration
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 15
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Beschleunigungssensor-Kalibrierung"
                            font.pixelSize: 18
                            font.bold: true
                            color: "white"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Platzieren Sie die Drohne in den angegebenen Positionen, um den Beschleunigungssensor zu kalibrieren."
                            wrapMode: Text.WordWrap
                            color: "#cccccc"
                        }
                        
                        // Visuelle Anleitung
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 200
                            color: "#3c3c3c"
                            border.color: "#555555"
                            border.width: 1
                            
                            Text {
                                anchors.centerIn: parent
                                text: "Visuelle Anleitung zur Positionierung der Drohne"
                                color: "#aaaaaa"
                            }
                        }
                        
                        // Fortschrittsanzeige mit Schritten
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 5
                            
                            Text {
                                text: "Fortschritt: 0/6 Positionen"
                                color: "white"
                            }
                            
                            ProgressBar {
                                id: accelProgress
                                Layout.fillWidth: true
                                value: 0.0
                            }
                        }
                        
                        // Aktionsschaltflächen
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10
                            
                            Button {
                                text: "Starten"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.startAccelCalibration();
                                    }
                                }
                            }
                            
                            Button {
                                text: "Weiter"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.nextCalibrationStep();
                                    }
                                }
                            }
                            
                            Button {
                                text: "Abbrechen"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.cancelCalibration();
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Gyroskop-Kalibrierung 
                Item {
                    id: gyroCalibration
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 15
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Gyroskop-Kalibrierung"
                            font.pixelSize: 18
                            font.bold: true
                            color: "white"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Stellen Sie sicher, dass die Drohne vollkommen still und auf einer ebenen Fläche steht."
                            wrapMode: Text.WordWrap
                            color: "#cccccc"
                        }
                        
                        // Visuelle Anzeige der Gyroskop-Werte
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 200
                            color: "#3c3c3c"
                            border.color: "#555555"
                            border.width: 1
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 10
                                
                                Text {
                                    text: "Gyroskop-Werte:"
                                    color: "white"
                                    font.bold: true
                                }
                                
                                Text {
                                    text: "X: 0.00 °/s"
                                    color: "#aaaaaa"
                                }
                                
                                Text {
                                    text: "Y: 0.00 °/s"
                                    color: "#aaaaaa"
                                }
                                
                                Text {
                                    text: "Z: 0.00 °/s"
                                    color: "#aaaaaa"
                                }
                            }
                        }
                        
                        // Fortschrittsanzeige
                        ProgressBar {
                            id: gyroProgress
                            Layout.fillWidth: true
                            value: 0.0
                        }
                        
                        // Aktionsschaltflächen
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10
                            
                            Button {
                                text: "Starten"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.startGyroCalibration();
                                    }
                                }
                            }
                            
                            Button {
                                text: "Abbrechen"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.cancelCalibration();
                                    }
                                }
                            }
                        }
                    }
                }
                
                // RC Fernbedienung-Kalibrierung
                Item {
                    id: rcCalibration
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 15
                        
                        Text {
                            Layout.fillWidth: true
                            text: "RC Fernbedienung-Kalibrierung"
                            font.pixelSize: 18
                            font.bold: true
                            color: "white"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Bewegen Sie alle Steuerknüppel und Schalter der Fernbedienung durch ihren vollen Bewegungsbereich."
                            wrapMode: Text.WordWrap
                            color: "#cccccc"
                        }
                        
                        // Visuelle Darstellung der RC-Eingaben
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 250
                            color: "#3c3c3c"
                            border.color: "#555555"
                            border.width: 1
                            
                            GridLayout {
                                anchors.fill: parent
                                anchors.margins: 15
                                columns: 4
                                rowSpacing: 15
                                columnSpacing: 15
                                
                                // Steuerknüppel-Anzeigen
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: "#2a2a2a"
                                    border.color: "#666666"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "Steuerknüppel 1"
                                        color: "white"
                                    }
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: "#2a2a2a"
                                    border.color: "#666666"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "Steuerknüppel 2"
                                        color: "white"
                                    }
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: "#2a2a2a"
                                    border.color: "#666666"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "Schalter 1"
                                        color: "white"
                                    }
                                }
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: "#2a2a2a"
                                    border.color: "#666666"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "Schalter 2"
                                        color: "white"
                                    }
                                }
                            }
                        }
                        
                        // Kanalliste
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 150
                            color: "#3c3c3c"
                            border.color: "#555555"
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 5
                                
                                Text {
                                    text: "RC Kanal-Werte:"
                                    color: "white"
                                    font.bold: true
                                }
                                
                                ListView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    model: 8 // 8 RC Kanäle
                                    delegate: RowLayout {
                                        width: parent.width
                                        height: 25
                                        
                                        Text {
                                            text: "Kanal " + (index + 1) + ":"
                                            color: "#cccccc"
                                            Layout.preferredWidth: 70
                                        }
                                        
                                        ProgressBar {
                                            Layout.fillWidth: true
                                            value: 0.5 // Standardwert
                                        }
                                        
                                        Text {
                                            text: "1500" // PWM-Wert
                                            color: "#cccccc"
                                            Layout.preferredWidth: 50
                                            horizontalAlignment: Text.AlignRight
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Aktionsschaltflächen
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10
                            
                            Button {
                                text: "Starten"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.startRCCalibration();
                                    }
                                }
                            }
                            
                            Button {
                                text: "Speichern"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.saveRCCalibration();
                                    }
                                }
                            }
                            
                            Button {
                                text: "Abbrechen"
                                Layout.fillWidth: true
                                onClicked: {
                                    if (root.controller) {
                                        root.controller.cancelCalibration();
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
