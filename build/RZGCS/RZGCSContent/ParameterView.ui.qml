/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQml.Models 2.2

Item {
    id: root
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "black"
        z: -1
    }
    
    // Debug-Funktion
    function logMessage(message) {
        console.log("[ParameterView] " + message)
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        RowLayout {
            spacing: 10
            Layout.fillWidth: true

            TextField {
                id: searchField
                placeholderText: "Search..."
                Layout.preferredWidth: 200
                color: "white"
                background: Rectangle {
                    color: "#333333"
                    border.color: "#777777"
                    radius: 2
                }
                onTextChanged: {
                    logMessage("Such-Text geändert: " + text)
                    if (text.length > 0) {
                        // Beim Tippen filtern
                        root.filterParameters(text)
                    } else {
                        // Wenn leer, alle anzeigen
                        paramTable.model = parameterModel
                    }
                }
            }

            Button {
                id: clearButton
                text: "Clear"
                Layout.preferredWidth: 80
                background: Rectangle {
                    color: "black"
                    border.color: "gray"
                    border.width: 1
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: searchField.text = ""
            }

            Item { Layout.fillWidth: true } // Spacer

            Button {
                id: toolsButton
                text: "Tools"
                Layout.preferredWidth: 80
                background: Rectangle {
                    color: "black"
                    border.color: "gray"
                    border.width: 1
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }

        // Funktion zum Filtern der Parameter
        function filterParameters(searchString) {
            logMessage("Filtere nach: " + searchString)
            if (parameterModel) {
                try {
                    var filtered = parameterModel.filter_parameters(searchString)
                    if (filtered && filtered.length !== undefined) {
                        logMessage("Gefiltert: " + filtered.length + " Ergebnisse")
                        // Modell direkt aktualisieren
                        paramTable.model = filtered
                    } else {
                        logMessage("Filter-Ergebnis ungültig")
                    }
                } catch (e) {
                    logMessage("Fehler beim Filtern: " + e)
                }
            } else {
                logMessage("Parameter-Modell nicht verfügbar")
            }
        }
        
        ListView {
            id: paramTable
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: parameterModel
            
            // Header für die Tabelle
            header: Rectangle {
                width: paramTable.width
                height: 30
                color: "#444444"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 10
                    anchors.rightMargin: 10
                    spacing: 10

                    Text {
                        text: "Parameter"
                        color: "white"
                        font.bold: true
                        Layout.preferredWidth: 120
                    }
                    
                    Text {
                        text: "Option"
                        color: "white"
                        font.bold: true
                        Layout.preferredWidth: 120
                    }
                    
                    Text {
                        text: "Wert"
                        color: "white"
                        font.bold: true
                        Layout.preferredWidth: 120
                    }
                    
                    Text {
                        text: "Beschreibung"
                        color: "white"
                        font.bold: true
                        Layout.fillWidth: true
                    }
                }
            }
            
            // Modell aktualisieren, wenn neue Parameter geladen wurden
            function resetModel() {
                logMessage("Parameter-Liste zurücksetzen")
                // Aktuelles Model festlegen
                if (searchField.text === "") {
                    // Alle Parameter anzeigen wenn kein Suchtext
                    paramTable.model = parameterModel
                } else {
                    // Suche erneut ausführen
                    root.filterParameters(searchField.text)  
                }
            }
            
            // Element Template
            delegate: Rectangle {
                width: paramTable.width
                height: 40
                color: index === paramTable.currentIndex ? "#ffd700" : (model.name === "RC" ? "#ffd700" : (index % 2 === 0 ? "#333333" : "#444444")) 

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 10
                    anchors.rightMargin: 10
                    spacing: 10

                    Text {
                        text: model.name
                        color: index === paramTable.currentIndex ? "black" : "white"
                        Layout.preferredWidth: 120
                    }
                    
                    Text {
                        text: model.option || ""
                        color: index === paramTable.currentIndex ? "black" : "white"
                        Layout.preferredWidth: 120
                    }
                    
                    // Parameter-Wert (klickbar zum Bearbeiten)
                    Item {
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: parent.height
                        
                        Text {
                            id: valueText
                            anchors.fill: parent
                            anchors.leftMargin: 5
                            text: model.value || "Do Nothing"
                            color: index === paramTable.currentIndex ? "black" : "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        // Hintergrund zum Anklicken
                        Rectangle {
                            anchors.fill: parent
                            color: "transparent"
                            border.width: 1
                            border.color: "#555555"
                            opacity: paramMouseArea.containsMouse ? 0.3 : 0
                        }
                        
                        MouseArea {
                            id: paramMouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            
                            // Zum Bearbeiten klicken
                            onClicked: {
                                logMessage("Parameter bearbeiten: " + model.name + " = " + model.value)
                                editDialog.paramName = model.name
                                editDialog.currentValue = model.value
                                editDialog.open()
                            }
                        }
                    }
                    
                    Text {
                        text: model.desc || "RC input option"
                        color: index === paramTable.currentIndex ? "black" : "white"
                        Layout.fillWidth: true
                    }
                }
                
                // Für Auswahl eines Parameters
                MouseArea {
                    anchors.fill: parent
                    onClicked: paramTable.currentIndex = index
                }
            }
            
            ScrollBar.vertical: ScrollBar {}
        }

        // Automatisches Laden der Parameter nach Verbindung
        Connections {
            target: serialConnector
            function onConnectedChanged(connected) {
                if (connected) {
                    console.log("Verbindung hergestellt, lade Parameter...")
                    serialConnector.load_parameters()
                }
            }
        }

        // Feedback beim Laden der Parameter
        Connections {
            target: parameterModel
            function onParametersLoaded() {
                console.log("Parameter wurden geladen, Anzahl:", parameterModel.rowCount())
                paramTable.resetModel()
            }
        }
        
        // Dialog zum Bearbeiten von Parametern
        Dialog {
            id: editDialog
            title: "Parameter bearbeiten"
            width: 300
            height: 200
            anchors.centerIn: parent
            modal: true
            
            // Parameter-Eigenschaften
            property string paramName: ""
            property string currentValue: ""
            
            // Hintergrund
            background: Rectangle {
                color: "#333333"
                border.color: "gray"
                border.width: 1
            }
            
            // Dialog-Inhalt
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 15
                
                // Parameter-Name
                Text {
                    text: "Parameter: " + editDialog.paramName
                    color: "white"
                    font.bold: true
                }
                
                // Aktueller Wert
                Text {
                    text: "Aktueller Wert: " + editDialog.currentValue
                    color: "white"
                }
                
                // Neuer Wert
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    
                    Text {
                        text: "Neuer Wert:"
                        color: "white"
                    }
                    
                    TextField {
                        id: newValueField
                        Layout.fillWidth: true
                        text: editDialog.currentValue
                        color: "white"
                        background: Rectangle {
                            color: "#222222"
                            border.color: "gray"
                            border.width: 1
                        }
                    }
                }
                
                // Buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Layout.alignment: Qt.AlignRight
                    
                    Button {
                        text: "Abbrechen"
                        onClicked: editDialog.close()
                        background: Rectangle {
                            color: "#444444"
                            border.color: "gray"
                            border.width: 1
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    Button {
                        text: "Speichern"
                        onClicked: {
                            logMessage("Speichere Parameter: " + editDialog.paramName + " = " + newValueField.text)
                            // Parameter-Wert aktualisieren
                            if (parameterModel.set_parameter_value(editDialog.paramName, newValueField.text)) {
                                logMessage("Parameter im Modell aktualisiert")
                                // Senden an FC, falls verbunden
                                if (serialConnector && serialConnector.connected) {
                                    serialConnector.set_parameter(editDialog.paramName, newValueField.text)
                                    logMessage("Parameter an FC gesendet")
                                }
                                editDialog.close()
                            } else {
                                logMessage("Fehler beim Aktualisieren des Parameters")
                            }
                        }
                        background: Rectangle {
                            color: "#444444"
                            border.color: "gray"
                            border.width: 1
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }
    }
}
