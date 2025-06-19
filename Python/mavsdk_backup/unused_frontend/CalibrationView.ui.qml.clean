import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var controller: null  // Controller-Referenz, die von außen gesetzt wird
    
    Rectangle {
        anchors.fill: parent
        color: "#2c2c2c"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15
            
            Text {
                Layout.fillWidth: true
                text: "Kompass und Accelerometer Kalibrierung"
                font.pixelSize: 24
                font.bold: true
                color: "white"
            }
            
            Text {
                Layout.fillWidth: true
                text: "Kalibrieren Sie die Sensoren und Systeme Ihrer Drohne."
                font.pixelSize: 16
                color: "#cccccc"
                wrapMode: Text.WordWrap
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#555555"
                Layout.topMargin: 10
                Layout.bottomMargin: 10
            }
            
            TabBar {
                id: calibrationTabBar
                Layout.fillWidth: true
                
                TabButton {
                    text: "Kompass"
                    width: implicitWidth
                }
                
                TabButton {
                    text: "Beschleunigungssensor"
                    width: implicitWidth
                }
            }
            
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
                        
                        // Hauptbereich mit 3D-Visualisierung und Steuerungselementen
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 300
                            color: "#222222"
                            radius: 8
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 15
                                spacing: 20
                                
                                // 3D-Visualisierung für den Kompass
                                Compass3DView {
                                    id: compass3DView
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: parent.width * 0.6
                                    
                                    // Verbindung zum Controller für Kompass-Daten
                                    Connections {
                                        target: root.controller
                                        
                                        function onCompassValueChanged(x, y, z) {
                                            // Aktualisiere die Drohnenrotation basierend auf den Kompasswerten
                                            compass3DView.angleX = x * 0.1;
                                            compass3DView.angleY = y * 0.1;
                                            compass3DView.angleZ = z * 0.1;
                                            
                                            // Füge Punkt zur Visualisierung hinzu
                                            compass3DView.addCalibrationPoint(x, y, z);
                                            
                                            // Aktualisiere den Fortschritt basierend auf der Anzahl der gesammelten Punkte
                                            var progress = Math.min(compass3DView.collectedPoints.length / 50, 1.0);
                                            compass3DView.calibrationProgress = progress;
                                        }
                                    }
                                }
                                
                                // Anweisungen und Status
                                ColumnLayout {
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: parent.width * 0.4
                                    spacing: 15
                                    
                                    Rectangle {
                                        Layout.fillWidth: true
                                        color: "#333333"
                                        radius: 5
                                        height: compassInstructionsColumn.height + 20
                                        
                                        ColumnLayout {
                                            id: compassInstructionsColumn
                                            anchors.left: parent.left
                                            anchors.right: parent.right
                                            anchors.top: parent.top
                                            anchors.margins: 10
                                            spacing: 10
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "Anweisungen"
                                                font.pixelSize: 16
                                                font.bold: true
                                                color: "#66ccff"
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "1. Starten Sie die Kalibrierung mit dem 'Starten' Button"
                                                wrapMode: Text.WordWrap
                                                color: "white"
                                                font.pixelSize: 12
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "2. Drehen Sie die Drohne langsam in einer Figur-8-Bewegung"
                                                wrapMode: Text.WordWrap
                                                color: "white"
                                                font.pixelSize: 12
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "3. Decken Sie alle Orientierungen ab, bis der Fortschritt 100% erreicht"
                                                wrapMode: Text.WordWrap
                                                color: "white"
                                                font.pixelSize: 12
                                            }
                                        }
                                    }
                                    
                                    // Fortschrittsanzeige
                                    Rectangle {
                                        Layout.fillWidth: true
                                        color: "#333333"
                                        radius: 5
                                        height: compassProgressColumn.height + 20
                                        
                                        ColumnLayout {
                                            id: compassProgressColumn
                                            anchors.left: parent.left
                                            anchors.right: parent.right
                                            anchors.top: parent.top
                                            anchors.margins: 10
                                            spacing: 10
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "Kalibrierungsfortschritt"
                                                font.pixelSize: 16
                                                font.bold: true
                                                color: "#66ccff"
                                            }
                                            
                                            ProgressBar {
                                                id: compassProgressBar
                                                Layout.fillWidth: true
                                                value: compass3DView.calibrationProgress
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: Math.round(compass3DView.calibrationProgress * 100) + "% abgeschlossen"
                                                horizontalAlignment: Text.AlignHCenter
                                                color: "white"
                                                font.pixelSize: 14
                                            }
                                            
                                            // Status-Text (wird durch Signals aktualisiert)
                                            Text {
                                                id: compassStatusText
                                                Layout.fillWidth: true
                                                text: "Bereit"
                                                wrapMode: Text.WordWrap
                                                horizontalAlignment: Text.AlignHCenter
                                                color: "#aaffaa"
                                                font.pixelSize: 12
                                            }
                                        }
                                    }
                                    
                                    // Spacer
                                    Item { Layout.fillHeight: true }
                                }
                            }
                        }
                        
                        // Steuerungsschaltflächen
                        Rectangle {
                            Layout.fillWidth: true
                            height: 60
                            color: "#333333"
                            radius: 5
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 15
                                
                                Button {
                                    text: "Starten"
                                    Layout.fillWidth: true
                                    implicitHeight: 40
                                    background: Rectangle {
                                        color: parent.pressed ? "#2980b9" : (parent.hovered ? "#3498db" : "#2c3e50")
                                        radius: 4
                                    }
                                    contentItem: Text {
                                        text: parent.text
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: "white"
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    onClicked: {
                                        if (root.controller) {
                                            root.controller.startCompassCalibration();
                                            compassStatusText.text = "Kalibrierung läuft..."
                                            compassStatusText.color = "#ffff99"
                                        }
                                    }
                                }
                                
                                Button {
                                    text: "Abbrechen"
                                    Layout.fillWidth: true
                                    implicitHeight: 40
                                    background: Rectangle {
                                        color: parent.pressed ? "#c0392b" : (parent.hovered ? "#e74c3c" : "#7f8c8d")
                                        radius: 4
                                    }
                                    contentItem: Text {
                                        text: parent.text
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: "white"
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    onClicked: {
                                        if (root.controller) {
                                            root.controller.cancelCalibration();
                                            compassStatusText.text = "Kalibrierung abgebrochen"
                                            compassStatusText.color = "#ff9999"
                                            
                                            // Animation optional neu starten für Demo
                                            compass3DView.stopRotationAnimation();
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Verbindung für Kalibrierungssignale
                        Connections {
                            target: root.controller
                            
                            function onCalibrationProgressChanged(progress, message) {
                                if (calibrationTabBar.currentIndex === 0) { // Kompass-Tab
                                    compass3DView.calibrationProgress = progress;
                                    compassStatusText.text = message;
                                    compassStatusText.color = "#ffff99"; // Gelb während der Kalibrierung
                                }
                            }
                            
                            function onCalibrationFinished(success, message) {
                                if (calibrationTabBar.currentIndex === 0) { // Kompass-Tab
                                    compassStatusText.text = message;
                                    compassStatusText.color = success ? "#aaffaa" : "#ff9999"; // Grün bei Erfolg, Rot bei Fehler
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
                        
                        // Hauptbereich mit 3D-Visualisierung und Steuerungselementen
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 300
                            color: "#222222"
                            radius: 8
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 15
                                spacing: 20
                                
                                // 3D-Visualisierung für den Accelerometer
                                Accel3DView {
                                    id: accel3DView
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: parent.width * 0.6
                                }
                                
                                // Anweisungen und Status
                                ColumnLayout {
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: parent.width * 0.4
                                    spacing: 15
                                    
                                    Rectangle {
                                        Layout.fillWidth: true
                                        color: "#333333"
                                        radius: 5
                                        height: accelInstructionsColumn.height + 20
                                        
                                        ColumnLayout {
                                            id: accelInstructionsColumn
                                            anchors.left: parent.left
                                            anchors.right: parent.right
                                            anchors.top: parent.top
                                            anchors.margins: 10
                                            spacing: 10
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "Anweisungen"
                                                font.pixelSize: 16
                                                font.bold: true
                                                color: "#66ccff"
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "1. Starten Sie die Kalibrierung mit dem 'Starten' Button"
                                                wrapMode: Text.WordWrap
                                                color: "white"
                                                font.pixelSize: 12
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "2. Halten Sie die Drohne in jeder der gezeigten Positionen"
                                                wrapMode: Text.WordWrap
                                                color: "white"
                                                font.pixelSize: 12
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "3. Bestätigen Sie jede Position mit dem entsprechenden Button"
                                                wrapMode: Text.WordWrap
                                                color: "white"
                                                font.pixelSize: 12
                                            }
                                        }
                                    }
                                    
                                    // Fortschrittsanzeige
                                    Rectangle {
                                        Layout.fillWidth: true
                                        color: "#333333"
                                        radius: 5
                                        height: accelProgressColumn.height + 20
                                        
                                        ColumnLayout {
                                            id: accelProgressColumn
                                            anchors.left: parent.left
                                            anchors.right: parent.right
                                            anchors.top: parent.top
                                            anchors.margins: 10
                                            spacing: 10
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "Kalibrierungsfortschritt"
                                                font.pixelSize: 16
                                                font.bold: true
                                                color: "#66ccff"
                                            }
                                            
                                            ProgressBar {
                                                id: accelProgressBar
                                                Layout.fillWidth: true
                                                value: accel3DView.calibrationProgress
                                            }
                                            
                                            Text {
                                                id: accelProgressText
                                                Layout.fillWidth: true
                                                text: "Position " + (Math.floor(accel3DView.calibrationProgress * 6) + 1) + " von 6"
                                                horizontalAlignment: Text.AlignHCenter
                                                color: "white"
                                                font.pixelSize: 14
                                            }
                                            
                                            // Status-Text (wird durch Signals aktualisiert)
                                            Text {
                                                id: accelStatusText
                                                Layout.fillWidth: true
                                                text: "Bereit"
                                                wrapMode: Text.WordWrap
                                                horizontalAlignment: Text.AlignHCenter
                                                color: "#aaffaa"
                                                font.pixelSize: 12
                                            }
                                        }
                                    }
                                    
                                    // Positionssteuerung
                                    Rectangle {
                                        Layout.fillWidth: true
                                        color: "#333333"
                                        radius: 5
                                        height: positionButtonsColumn.height + 20
                                        visible: accel3DView.calibrationProgress > 0
                                        
                                        ColumnLayout {
                                            id: positionButtonsColumn
                                            anchors.left: parent.left
                                            anchors.right: parent.right
                                            anchors.top: parent.top
                                            anchors.margins: 10
                                            spacing: 10
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: "Aktuelle Position bestätigen"
                                                font.pixelSize: 14
                                                font.bold: true
                                                color: "#66ccff"
                                            }
                                            
                                            Button {
                                                Layout.fillWidth: true
                                                text: "Bestätigen und Fortfahren"
                                                implicitHeight: 36
                                                background: Rectangle {
                                                    color: parent.pressed ? "#27ae60" : (parent.hovered ? "#2ecc71" : "#16a085")
                                                    radius: 4
                                                }
                                                contentItem: Text {
                                                    text: parent.text
                                                    font.pixelSize: 13
                                                    font.bold: true
                                                    color: "white"
                                                    horizontalAlignment: Text.AlignHCenter
                                                    verticalAlignment: Text.AlignVCenter
                                                }
                                                onClicked: {
                                                    if (root.controller) {
                                                        root.controller.nextCalibrationStep();
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Verbindung zum Controller
                        Connections {
                            target: root.controller
                            
                            function onAccelValueChanged(x, y, z) {
                                // Verwende die Accelerometer-Daten für eine realistische Darstellung
                                // der Drohne basierend auf den tatsächlichen Sensordaten
                                if (calibrationTabBar.currentIndex === 1) {
                                    // Rotationswerte berechnen und anwenden
                                    // Vereinfachte Berechnung - kann für realistischere Darstellung verbessert werden
                                    var tiltX = Math.atan2(y, Math.sqrt(x*x + z*z)) * (180/Math.PI);
                                    var tiltY = Math.atan2(-x, Math.sqrt(y*y + z*z)) * (180/Math.PI);
                                    
                                    accel3DView.angleX = tiltX;
                                    accel3DView.angleY = tiltY;
                                }
                            }
                            
                            function onCalibrationProgressChanged(progress, message) {
                                // Fortschritt der Kalibrierung aktualisieren
                                if (calibrationTabBar.currentIndex === 1) { // Accelerometer-Tab
                                    accel3DView.calibrationProgress = progress;
                                    accelStatusText.text = message;
                                    accelStatusText.color = "#ffff99";
                                    
                                    // Schritt-Index berechnen (6 Schritte insgesamt)
                                    var step = Math.floor(progress * 6);
                                    if (step < 6) {
                                        accel3DView.setCalibrationStep(step);
                                    }
                                }
                            }
                            
                            function onCalibrationFinished(success, message) {
                                if (calibrationTabBar.currentIndex === 1) { // Accelerometer-Tab
                                    accelStatusText.text = message;
                                    accelStatusText.color = success ? "#aaffaa" : "#ff9999";
                                }
                            }
                        }
                        
                        // Steuerungsschaltflächen
                        Rectangle {
                            Layout.fillWidth: true
                            height: 60
                            color: "#333333"
                            radius: 5
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 15
                                
                                Button {
                                    text: "Starten"
                                    Layout.fillWidth: true
                                    implicitHeight: 40
                                    background: Rectangle {
                                        color: parent.pressed ? "#2980b9" : (parent.hovered ? "#3498db" : "#2c3e50")
                                        radius: 4
                                    }
                                    contentItem: Text {
                                        text: parent.text
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: "white"
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    onClicked: {
                                        if (root.controller) {
                                            root.controller.startAccelCalibration();
                                            accelStatusText.text = "Kalibrierung läuft..."
                                            accelStatusText.color = "#ffff99"
                                        }
                                    }
                                }
                                
                                Button {
                                    text: "Abbrechen"
                                    Layout.fillWidth: true
                                    implicitHeight: 40
                                    background: Rectangle {
                                        color: parent.pressed ? "#c0392b" : (parent.hovered ? "#e74c3c" : "#7f8c8d")
                                        radius: 4
                                    }
                                    contentItem: Text {
                                        text: parent.text
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: "white"
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    onClicked: {
                                        if (root.controller) {
                                            root.controller.cancelCalibration();
                                            accelStatusText.text = "Kalibrierung abgebrochen"
                                            accelStatusText.color = "#ff9999"
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
}
