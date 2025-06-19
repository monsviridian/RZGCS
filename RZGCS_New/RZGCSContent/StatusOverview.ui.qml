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
    id: statusOverview
    width: parent.width
    height: parent.height

    // Dunkler Hintergrund
    Rectangle {
        anchors.fill: parent
        color: "#121212"
    }

    // Status-Übersicht mit Grid-Layout
    GridLayout {
        id: statusGrid
        anchors.fill: parent
        anchors.margins: 8
        columns: 5
        rows: 2
        rowSpacing: 8
        columnSpacing: 8

        // 1. Fahrzeuginformationen
        Rectangle {
            Layout.column: 0
            Layout.row: 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#1e1e1e"
            border.color: "#3eb243" // Grün für OK-Status
            border.width: 2
            radius: 5

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 5

                Text {
                    text: "Fahrzeuginformationen"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }

                Rectangle {
                    height: 1
                    Layout.fillWidth: true
                    color: "#444444"
                }

                // Fahrzeuginformationen Grid
                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: 2
                    
                    Text { text: "Rahmen Klasse:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Quad"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Rahmentyp:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "X"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Firmware Version:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "4.7.0dev"; color: "white"; font.pixelSize: 12 }
                }
            }

            // Status-Indikator
            Rectangle {
                width: 16
                height: 16
                radius: 8
                color: "#3eb243" // Grün für OK
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 8
            }
        }

        // 2. Radio
        Rectangle {
            Layout.column: 1
            Layout.row: 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#1e1e1e"
            border.color: "#e63946" // Rot für Fehler
            border.width: 2
            radius: 5

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 5

                Text {
                    text: "Radio"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }

                Rectangle {
                    height: 1
                    Layout.fillWidth: true
                    color: "#444444"
                }

                // Radio Informationen
                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: 2
                    
                    Text { text: "Roll:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Channel 1"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Pitch:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Channel 2"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Yaw:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Channel 4"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Throttle:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Channel 3"; color: "white"; font.pixelSize: 12 }
                }
            }

            // Status-Indikator
            Rectangle {
                width: 16
                height: 16
                radius: 8
                color: "#e63946" // Rot für Fehler
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 8
            }
        }

        // 3. Flugmodi
        Rectangle {
            Layout.column: 2
            Layout.row: 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#1e1e1e"
            border.color: "#3eb243" // Grün für OK
            border.width: 2
            radius: 5

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 5

                Text {
                    text: "Flugmodi"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }

                Rectangle {
                    height: 1
                    Layout.fillWidth: true
                    color: "#444444"
                }

                // Flugmodi Informationen
                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: 2
                    
                    Text { text: "Flugmodus 1:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Stabilize"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Flugmodus 2:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Stabilize"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Flugmodus 3:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Stabilize"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Flugmodus 4:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Stabilize"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Flugmodus 5:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Stabilize"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Flugmodus 6:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Stabilize"; color: "white"; font.pixelSize: 12 }
                }
            }

            // Status-Indikator
            Rectangle {
                width: 16
                height: 16
                radius: 8
                color: "#3eb243" // Grün für OK
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 8
            }
        }

        // 4. Sensoren
        Rectangle {
            Layout.column: 3
            Layout.row: 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#1e1e1e"
            border.color: "#e63946" // Rot für Fehler
            border.width: 2
            radius: 5

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 5

                Text {
                    text: "Sensoren"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }

                Rectangle {
                    height: 1
                    Layout.fillWidth: true
                    color: "#444444"
                }

                // Sensoren Informationen
                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: 2
                    
                    Text { text: "Kompass:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Setup required"; color: "#e63946"; font.pixelSize: 12 }
                    
                    Text { text: "Setup required:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Not inverted"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Accelerometer:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Setup required"; color: "#e63946"; font.pixelSize: 12 }
                    
                    Text { text: "INS_BMI088 (IMU):"; color: "white"; font.pixelSize: 12 }
                    Text { text: "EKF2"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Barometer:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "DPS310 (I2C)"; color: "white"; font.pixelSize: 12 }
                }
            }

            // Status-Indikator
            Rectangle {
                width: 16
                height: 16
                radius: 8
                color: "#e63946" // Rot für Fehler
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 8
            }
        }

        // 5. Power
        Rectangle {
            Layout.column: 4
            Layout.row: 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#1e1e1e"
            border.color: "#808080" // Grau für neutralen Status
            border.width: 2
            radius: 5

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 5

                Text {
                    text: "Power"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }

                Rectangle {
                    height: 1
                    Layout.fillWidth: true
                    color: "#444444"
                }

                // Power Informationen
                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: 2
                    
                    Text { text: "Batt1 monitor:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Analog Voltage and Current"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Batt1 capacity:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "5000 mAh"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Batt2 monitor:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Disabled"; color: "white"; font.pixelSize: 12 }
                }
            }
        }

        // 6. Safety-Einstellungen
        Rectangle {
            Layout.column: 0
            Layout.row: 1
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#1e1e1e"
            border.color: "#808080" // Grau für neutralen Status
            border.width: 2
            radius: 5

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 5

                Text {
                    text: "Safety"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }

                Rectangle {
                    height: 1
                    Layout.fillWidth: true
                    color: "#444444"
                }

                // Safety Informationen
                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: 2
                    rowSpacing: 2
                    
                    Text { text: "Arming Checks:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Enabled"; color: "#3eb243"; font.pixelSize: 12 }
                    
                    Text { text: "Manual Arming:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Enabled (except AHRS)"; color: "#3eb243"; font.pixelSize: 12 }
                    
                    Text { text: "Batt1 low failsafe:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "None"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "Batt1 critical failsafe:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "None"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "GeoFence:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "Disabled"; color: "white"; font.pixelSize: 12 }
                    
                    Text { text: "RTL max alt:"; color: "white"; font.pixelSize: 12 }
                    Text { text: "1500 cm"; color: "white"; font.pixelSize: 12 }
                }
            }
        }
    }

    // Verbindungsleiste am unteren Rand
    Rectangle {
        id: connectionBar
        height: 30
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        color: "#1e1e1e"

        RowLayout {
            anchors.fill: parent
            anchors.margins: 5
            spacing: 10

            // Verbindungsstatus
            Text {
                text: "Status: "
                color: "white"
                font.pixelSize: 12
            }

            Text {
                id: statusText
                text: "Disconnected"
                color: "#e63946" // Rot für nicht verbunden
                font.pixelSize: 12
                font.bold: true
            }

            Item { Layout.fillWidth: true } // Spacer

            // Firmware-Version
            Text {
                text: "Firmware: 4.7.0dev"
                color: "white"
                font.pixelSize: 12
            }
        }
    }

    // Wird aufgerufen wenn Verbindungsstatus sich ändert
    function updateConnectionStatus(connected) {
        if (connected) {
            statusText.text = "Connected"
            statusText.color = "#3eb243" // Grün für verbunden
        } else {
            statusText.text = "Disconnected"
            statusText.color = "#e63946" // Rot für nicht verbunden
        }
    }

    // Anstatt Connections für jeden Signal: Ein Timer, der die Werte regelmäßig aktualisiert
    Timer {
        interval: 1000 // Aktualisiere jede Sekunde
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            console.log("Aktualisiere Status-Übersicht...")
            // Verbindungsstatus aktualisieren
            if (typeof serialConnector !== "undefined") {
                updateConnectionStatus(serialConnector.connected)
            }
            
            // Controller-Werte in UI aktualisieren, wenn verfügbar
            if (typeof statusController !== "undefined") {
                // Hier können wir auf die Properties des Controllers zugreifen
                console.log("Status Controller gefunden!")
            } else {
                console.log("Status Controller nicht verfügbar")
            }
        }
    }

    // Komponente initialisieren
    Component.onCompleted: {
        // Verbindung mit dem SerialConnector herstellen
        if (typeof serialConnector !== "undefined") {
            updateConnectionStatus(serialConnector.connected)
        }
        
        // Statusu00fcbersicht mit initialem Status aktualisieren
        if (typeof statusController !== "undefined") {
            console.log("StatusController gefunden, initialisiere Statusu00fcbersicht...")
        } else {
            console.log("Warnung: StatusController nicht gefunden!")
        }
    }
}
