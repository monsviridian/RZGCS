import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var controller: calibrationController  // Use the calibrationController from main app
    
    // Ensure all calibration messages go to the message panel
    Connections {
        target: calibrationController
        
        function onLogMessageReceived(type, message) {
            if (messageManager) {
                var messageType = 1; // Default to info
                if (type === "error") messageType = 3;
                else if (type === "warning") messageType = 2;
                else if (type === "success") messageType = 4;
                
                messageManager.addMessage(`[CALIBRATION] ${message}`, messageType);
            }
        }
        
        function onCalibrationProgressChanged(progress, message) {
            if (messageManager) {
                messageManager.addMessage(`[CALIBRATION] ${message} (${Math.round(progress*100)}%)`, 1);
            }
        }
        
        function onCalibrationFinished(success, message) {
            if (messageManager) {
                var messageType = success ? 4 : 3; // Success or Error
                messageManager.addMessage(`[CALIBRATION] ${message}`, messageType);
            }
        }
    }
    
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
                
                TabButton { text: "Kompass"; width: implicitWidth }
                TabButton { text: "Beschleunigungssensor"; width: implicitWidth }
                TabButton { text: "Gyroskop"; width: implicitWidth }
                TabButton { text: "Level"; width: implicitWidth }
                TabButton { text: "RC"; width: implicitWidth }
                TabButton { text: "ESC"; width: implicitWidth }
                TabButton { text: "Joystick"; width: implicitWidth }
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
                                            if (messageManager) {
                                                messageManager.addMessage("[CALIBRATION] Starting compass calibration...", 1);
                                            }
                                            root.controller.start_calibration("compass");
                                            compassStatusText.text = "Kalibrierung läuft..."
                                            compassStatusText.color = "#ffff99"
                                        } else {
                                            if (messageManager) {
                                                messageManager.addMessage("[CALIBRATION] Error: No calibration controller available", 3);
                                            }
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
                                            if (messageManager) {
                                                messageManager.addMessage("[CALIBRATION] Cancelling compass calibration...", 2);
                                            }
                                            root.controller.cancel_calibration();
                                            compassStatusText.text = "Kalibrierung abgebrochen"
                                            compassStatusText.color = "#ff9999"
                                            
                                            // Animation optional neu starten für Demo
                                            compass3DView.stopRotationAnimation();
                                        } else {
                                            if (messageManager) {
                                                messageManager.addMessage("[CALIBRATION] Error: No calibration controller available", 3);
                                            }
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
                        
                        // Logger-Anzeige für Kalibrierungsstatus
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 250  // Vergrößert von 150 auf 250
                            color: "#333333"
                            radius: 5
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 5
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10
                                    
                                    Text {
                                        Layout.fillWidth: true
                                        text: "Kalibrierungsstatus"
                                        font.pixelSize: 16
                                        font.bold: true
                                        color: "#66ccff"
                                    }
                                    
                                    // Neustart-Button
                                    Button {
                                        text: "FC Neustarten"
                                        implicitHeight: 30
                                        implicitWidth: 120
                                        background: Rectangle {
                                            color: parent.pressed ? "#d35400" : (parent.hovered ? "#e67e22" : "#f39c12")
                                            radius: 4
                                        }
                                        contentItem: Text {
                                            text: parent.text
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: "white"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        onClicked: {
                                            if (root.controller) {
                                                if (messageManager) {
                                                    messageManager.addMessage("[CALIBRATION] Sending reboot command to flight controller...", 2);
                                                }
                                                root.controller.reboot_flight_controller();
                                            } else {
                                                if (messageManager) {
                                                    messageManager.addMessage("[CALIBRATION] Error: No calibration controller available", 3);
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    
                                    background: Rectangle {
                                        color: "#222222"
                                        radius: 3
                                    }
                                    
                                    ListView {
                                        id: logListView
                                        anchors.fill: parent
                                        anchors.margins: 5
                                        model: ListModel { id: logModel }
                                        delegate: Text {
                                            width: ListView.view.width
                                            text: message
                                            color: {
                                                if (type === "error") return "#ff6666";
                                                if (type === "warning") return "#ffcc66";
                                                return "#cccccc";
                                            }
                                            font.pixelSize: 13  // Vergrößert von 12 auf 13
                                            wrapMode: Text.WordWrap
                                        }
                                    }
                                }
                                
                                // Verbindung zum Controller für Log-Nachrichten
                                Connections {
                                    target: root.controller
                                    
                                    function onLogMessageReceived(type, message) {
                                        // Neue Nachrichten am Anfang einfügen
                                        logModel.insert(0, {"type": type, "message": message});
                                        
                                        // Begrenze die Anzahl der Nachrichten (optional)
                                        if (logModel.count > 50) {
                                            logModel.remove(logModel.count - 1);
                                        }
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
                                            root.controller.start_calibration("accel");
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
                        
                        // Logger-Anzeige für Kalibrierungsstatus (Accelerometer)
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 250  // Vergrößert von 150 auf 250
                            color: "#333333"
                            radius: 5
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 5
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10
                                    
                                    Text {
                                        Layout.fillWidth: true
                                        text: "Kalibrierungsstatus"
                                        font.pixelSize: 16
                                        font.bold: true
                                        color: "#66ccff"
                                    }
                                    
                                    // Neustart-Button
                                    Button {
                                        text: "FC Neustarten"
                                        implicitHeight: 30
                                        implicitWidth: 120
                                        background: Rectangle {
                                            color: parent.pressed ? "#d35400" : (parent.hovered ? "#e67e22" : "#f39c12")
                                            radius: 4
                                        }
                                        contentItem: Text {
                                            text: parent.text
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: "white"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        onClicked: {
                                            if (root.controller) {
                                                if (messageManager) {
                                                    messageManager.addMessage("[CALIBRATION] Sending reboot command to flight controller...", 2);
                                                }
                                                root.controller.reboot_flight_controller();
                                            } else {
                                                if (messageManager) {
                                                    messageManager.addMessage("[CALIBRATION] Error: No calibration controller available", 3);
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    
                                    background: Rectangle {
                                        color: "#222222"
                                        radius: 3
                                    }
                                    
                                    ListView {
                                        id: accelLogListView
                                        anchors.fill: parent
                                        anchors.margins: 5
                                        model: logModel  // Verwende das gleiche Model wie in der Kompass-Ansicht
                                        delegate: Text {
                                            width: ListView.view.width
                                            text: message
                                            color: {
                                                if (type === "error") return "#ff6666";
                                                if (type === "warning") return "#ffcc66";
                                                return "#cccccc";
                                            }
                                            font.pixelSize: 13  // Vergrößert von 12 auf 13
                                            wrapMode: Text.WordWrap
                                        }
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
                            text: "Halten Sie die Drohne ruhig und bewegen Sie sie nicht während der Gyroskop-Kalibrierung."
                            wrapMode: Text.WordWrap
                            color: "#cccccc"
                        }
                        
                        // Hauptbereich mit Status und Steuerung
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 300
                            color: "#222222"
                            radius: 8
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 20
                                spacing: 20
                                
                                // Status-Anzeige
                                Rectangle {
                                    Layout.fillWidth: true
                                    color: "#333333"
                                    radius: 5
                                    height: 100
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 15
                                        spacing: 10
                                        
                                        Text {
                                            Layout.fillWidth: true
                                            text: "Gyroskop-Status"
                                            font.pixelSize: 16
                                            font.bold: true
                                            color: "#66ccff"
                                        }
                                        
                                        ProgressBar {
                                            id: gyroProgressBar
                                            Layout.fillWidth: true
                                            value: 0.0
                                        }
                                        
                                        Text {
                                            id: gyroStatusText
                                            Layout.fillWidth: true
                                            text: "Bereit für Kalibrierung"
                                            horizontalAlignment: Text.AlignHCenter
                                            color: "#aaffaa"
                                            font.pixelSize: 14
                                        }
                                    }
                                }
                                
                                // Anweisungen
                                Rectangle {
                                    Layout.fillWidth: true
                                    color: "#333333"
                                    radius: 5
                                    height: 120
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 15
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
                                            text: "1. Stellen Sie sicher, dass die Drohne auf einer ebenen Fläche steht"
                                            wrapMode: Text.WordWrap
                                            color: "white"
                                            font.pixelSize: 12
                                        }
                                        
                                        Text {
                                            Layout.fillWidth: true
                                            text: "2. Starten Sie die Kalibrierung und bewegen Sie die Drohne NICHT"
                                            wrapMode: Text.WordWrap
                                            color: "white"
                                            font.pixelSize: 12
                                        }
                                        
                                        Text {
                                            Layout.fillWidth: true
                                            text: "3. Warten Sie bis die Kalibrierung abgeschlossen ist"
                                            wrapMode: Text.WordWrap
                                            color: "white"
                                            font.pixelSize: 12
                                        }
                                    }
                                }
                                
                                // Steuerungsschaltflächen
                                RowLayout {
                                    Layout.fillWidth: true
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
                                            if (calibrationController) {
                                                calibrationController.start_calibration("gyro");
                                                gyroStatusText.text = "Kalibrierung läuft..."
                                                gyroStatusText.color = "#ffff99"
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
                                            if (calibrationController) {
                                                calibrationController.cancel_calibration();
                                                gyroStatusText.text = "Kalibrierung abgebrochen"
                                                gyroStatusText.color = "#ff9999"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Verbindung zum Controller
                        Connections {
                            target: calibrationController
                            
                            function onCalibrationProgressChanged(progress, message) {
                                if (calibrationTabBar.currentIndex === 2) { // Gyroskop-Tab
                                    gyroProgressBar.value = progress;
                                    gyroStatusText.text = message;
                                    gyroStatusText.color = "#ffff99";
                                }
                            }
                            
                            function onCalibrationFinished(success, message) {
                                if (calibrationTabBar.currentIndex === 2) { // Gyroskop-Tab
                                    gyroStatusText.text = message;
                                    gyroStatusText.color = success ? "#aaffaa" : "#ff9999";
                                }
                            }
                        }
                    }
                }
                
                // Level-Kalibrierung
                Item {
                    id: levelCalibration
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 15
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Level-Kalibrierung"
                            font.pixelSize: 18
                            font.bold: true
                            color: "white"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: "Kalibrieren Sie die Level-Sensoren für eine präzise horizontale Ausrichtung."
                            wrapMode: Text.WordWrap
                            color: "#cccccc"
                        }
                        
                        // Hauptbereich mit Status und Steuerung
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 300
                            color: "#222222"
                            radius: 8
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 20
                                spacing: 20
                                
                                // Status-Anzeige
                                Rectangle {
                                    Layout.fillWidth: true
                                    color: "#333333"
                                    radius: 5
                                    height: 100
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 15
                                        spacing: 10
                                        
                                        Text {
                                            Layout.fillWidth: true
                                            text: "Level-Status"
                                            font.pixelSize: 16
                                            font.bold: true
                                            color: "#66ccff"
                                        }
                                        
                                        ProgressBar {
                                            id: levelProgressBar
                                            Layout.fillWidth: true
                                            value: 0.0
                                        }
                                        
                                        Text {
                                            id: levelStatusText
                                            Layout.fillWidth: true
                                            text: "Bereit für Kalibrierung"
                                            horizontalAlignment: Text.AlignHCenter
                                            color: "#aaffaa"
                                            font.pixelSize: 14
                                        }
                                    }
                                }
                                
                                // Anweisungen
                                Rectangle {
                                    Layout.fillWidth: true
                                    color: "#333333"
                                    radius: 5
                                    height: 120
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 15
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
                                            text: "1. Stellen Sie die Drohne auf eine perfekt ebene Fläche"
                                            wrapMode: Text.WordWrap
                                            color: "white"
                                            font.pixelSize: 12
                                        }
                                        
                                        Text {
                                            Layout.fillWidth: true
                                            text: "2. Stellen Sie sicher, dass die Drohne waagerecht steht"
                                            wrapMode: Text.WordWrap
                                            color: "white"
                                            font.pixelSize: 12
                                        }
                                        
                                        Text {
                                            Layout.fillWidth: true
                                            text: "3. Starten Sie die Level-Kalibrierung"
                                            wrapMode: Text.WordWrap
                                            color: "white"
                                            font.pixelSize: 12
                                        }
                                    }
                                }
                                
                                // Steuerungsschaltflächen
                                RowLayout {
                                    Layout.fillWidth: true
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
                                            if (calibrationController) {
                                                calibrationController.start_calibration("level");
                                                levelStatusText.text = "Kalibrierung läuft..."
                                                levelStatusText.color = "#ffff99"
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
                                            if (calibrationController) {
                                                calibrationController.cancel_calibration();
                                                levelStatusText.text = "Kalibrierung abgebrochen"
                                                levelStatusText.color = "#ff9999"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Verbindung zum Controller
                        Connections {
                            target: calibrationController
                            
                            function onCalibrationProgressChanged(progress, message) {
                                if (calibrationTabBar.currentIndex === 3) { // Level-Tab
                                    levelProgressBar.value = progress;
                                    levelStatusText.text = message;
                                    levelStatusText.color = "#ffff99";
                                }
                            }
                            
                            function onCalibrationFinished(success, message) {
                                if (calibrationTabBar.currentIndex === 3) { // Level-Tab
                                    levelStatusText.text = message;
                                    levelStatusText.color = success ? "#aaffaa" : "#ff9999";
                                }
                            }
                        }
                    }
                }
                
                Loader { source: "RCControl3DView.qml"; visible: calibrationTabBar.currentIndex === 4; property var controller: root.controller }
                Loader { source: "ESCCalibrationView.qml"; visible: calibrationTabBar.currentIndex === 5; property var controller: root.controller }
                Loader { source: "JoystickCalibrationView.qml"; visible: calibrationTabBar.currentIndex === 6; property var controller: root.controller }
            }
        }
    }
}
