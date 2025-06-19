import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var firmwareViewModel: null  // Referenz zum ViewModel, wird von außen gesetzt
    property bool isConnected: false

    Rectangle {
        anchors.fill: parent
        color: "#2c2c2c"
        
        ScrollView {
            id: scrollView
            anchors.fill: parent
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AlwaysOn
            ScrollBar.horizontal.policy: ScrollBar.AsNeeded
            
            ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15
            
            Text {
                Layout.fillWidth: true
                text: "Firmware Installation"
                font.pixelSize: 24
                font.bold: true
                color: "white"
            }
            
            Text {
                Layout.fillWidth: true
                text: "Installieren oder aktualisieren Sie die Firmware Ihres Flugcontrollers."
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
            
            // Hauptbereich mit zwei Spalten
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 20
                
                // Linke Spalte - Geräteauswahl und Firmware-Typ
                ColumnLayout {
                    Layout.fillHeight: true
                    Layout.preferredWidth: parent.width * 0.4
                    spacing: 15
                    
                    // Geräteauswahl
                    Rectangle {
                        Layout.fillWidth: true
                        color: "#333333"
                        radius: 5
                        height: deviceColumn.height + 20
                        
                        ColumnLayout {
                            id: deviceColumn
                            anchors.top: parent.top
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.margins: 10
                            spacing: 10
                            
                            Text {
                                text: "Verbundenes Gerät"
                                font.pixelSize: 16
                                font.bold: true
                                color: "white"
                            }
                            
                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: "#555555"
                            }
                            
                            Text {
                                text: root.isConnected ? "Flugcontroller erkannt" : "Kein Gerät verbunden"
                                color: root.isConnected ? "#00ff00" : "#ff9900"
                                font.pixelSize: 14
                            }
                            
                            Text {
                                visible: root.isConnected && firmwareViewModel && firmwareViewModel.deviceInfo
                                text: firmwareViewModel && firmwareViewModel.deviceInfo ? 
                                    "Typ: " + firmwareViewModel.deviceInfo.boardType + "\nBootloader: " + 
                                    firmwareViewModel.deviceInfo.bootloaderVersion : ""
                                color: "#cccccc"
                                font.pixelSize: 12
                            }
                            
                            Button {
                                Layout.fillWidth: true
                                text: "Gerät verbinden"
                                enabled: !root.isConnected
                                
                                onClicked: {
                                    if (firmwareViewModel) {
                                        firmwareViewModel.connectDevice()
                                    }
                                }
                            }
                        }
                    }
                    
                    // Firmware-Typ-Auswahl
                    Rectangle {
                        Layout.fillWidth: true
                        color: "#333333"
                        radius: 5
                        height: firmwareTypeColumn.height + 20
                        enabled: root.isConnected
                        opacity: enabled ? 1.0 : 0.6
                        
                        ColumnLayout {
                            id: firmwareTypeColumn
                            anchors.top: parent.top
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.margins: 10
                            spacing: 10
                            
                            Text {
                                text: "Firmware-Typ"
                                font.pixelSize: 16
                                font.bold: true
                                color: "white"
                            }
                            
                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: "#555555"
                            }
                            
                            RadioButton {
                                id: ardupilotRadio
                                text: "ArduPilot"
                                checked: firmwareViewModel ? firmwareViewModel.firmwareType === "ardupilot" : true
                                onCheckedChanged: {
                                    if (checked && firmwareViewModel) {
                                        firmwareViewModel.firmwareType = "ardupilot"
                                    }
                                }
                                
                                contentItem: Text {
                                    text: ardupilotRadio.text
                                    font.pixelSize: 14
                                    color: "white"
                                    leftPadding: ardupilotRadio.indicator.width + ardupilotRadio.spacing
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                            
                            RadioButton {
                                id: px4Radio
                                text: "PX4"
                                checked: firmwareViewModel ? firmwareViewModel.firmwareType === "px4" : false
                                onCheckedChanged: {
                                    if (checked && firmwareViewModel) {
                                        firmwareViewModel.firmwareType = "px4"
                                    }
                                }
                                
                                contentItem: Text {
                                    text: px4Radio.text
                                    font.pixelSize: 14
                                    color: "white"
                                    leftPadding: px4Radio.indicator.width + px4Radio.spacing
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                        }
                    }
                    
                    // Erweiterte Optionen
                    Rectangle {
                        Layout.fillWidth: true
                        color: "#333333"
                        radius: 5
                        height: advancedColumn.height + 20
                        enabled: root.isConnected
                        opacity: enabled ? 1.0 : 0.6
                        
                        ColumnLayout {
                            id: advancedColumn
                            anchors.top: parent.top
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.margins: 10
                            spacing: 10
                            
                            Text {
                                text: "Erweiterte Optionen"
                                font.pixelSize: 16
                                font.bold: true
                                color: "white"
                            }
                            
                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: "#555555"
                            }
                            
                            CheckBox {
                                id: wipeSettingsCheck
                                text: "Einstellungen löschen"
                                checked: firmwareViewModel ? firmwareViewModel.wipeSettings : false
                                onCheckedChanged: {
                                    if (firmwareViewModel) {
                                        firmwareViewModel.wipeSettings = checked
                                    }
                                }
                                
                                contentItem: Text {
                                    text: wipeSettingsCheck.text
                                    font.pixelSize: 14
                                    color: "white"
                                    leftPadding: wipeSettingsCheck.indicator.width + wipeSettingsCheck.spacing
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                            
                            CheckBox {
                                id: developerVersionsCheck
                                text: "Entwicklerversionen anzeigen"
                                checked: firmwareViewModel ? firmwareViewModel.showDeveloperVersions : false
                                onCheckedChanged: {
                                    if (firmwareViewModel) {
                                        firmwareViewModel.showDeveloperVersions = checked
                                    }
                                }
                                
                                contentItem: Text {
                                    text: developerVersionsCheck.text
                                    font.pixelSize: 14
                                    color: "white"
                                    leftPadding: developerVersionsCheck.indicator.width + developerVersionsCheck.spacing
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                        }
                    }
                    
                    // Platzhalter
                    Item {
                        Layout.fillHeight: true
                    }
                }
                
                // Rechte Spalte - Firmware-Auswahl und Installation
                ColumnLayout {
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    spacing: 15
                    
                    // Firmware-Varianten
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: 200
                        color: "#333333"
                        radius: 5
                        enabled: root.isConnected
                        opacity: enabled ? 1.0 : 0.6
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 10
                            
                            Text {
                                text: ardupilotRadio.checked ? "ArduPilot Firmware Varianten" : "PX4 Firmware Versionen"
                                font.pixelSize: 16
                                font.bold: true
                                color: "white"
                            }
                            
                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: "#555555"
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                
                                ListView {
                                    id: firmwareList
                                    anchors.fill: parent
                                    model: firmwareViewModel ? firmwareViewModel.firmwareList : null
                                    spacing: 5
                                    
                                    delegate: Rectangle {
                                        width: ListView.view.width
                                        height: delegateLayout.height + 20
                                        color: firmwareList.currentIndex === index ? "#4a6fb5" : "#444444"
                                        radius: 3
                                        
                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: {
                                                firmwareList.currentIndex = index
                                                if (firmwareViewModel) {
                                                    firmwareViewModel.selectedFirmwareIndex = index
                                                }
                                            }
                                        }
                                        
                                        ColumnLayout {
                                            id: delegateLayout
                                            anchors.left: parent.left
                                            anchors.right: parent.right
                                            anchors.top: parent.top
                                            anchors.margins: 10
                                            spacing: 5
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: modelData.name
                                                font.bold: true
                                                font.pixelSize: 14
                                                color: "white"
                                                elide: Text.ElideRight
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: modelData.version
                                                font.pixelSize: 12
                                                color: "#cccccc"
                                                elide: Text.ElideRight
                                            }
                                            
                                            Text {
                                                Layout.fillWidth: true
                                                text: modelData.description || ""
                                                font.pixelSize: 12
                                                color: "#aaaaaa"
                                                wrapMode: Text.WordWrap
                                                visible: modelData.description && modelData.description.length > 0
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Status und Fortschritt
                    Rectangle {
                        Layout.fillWidth: true
                        color: "#333333"
                        radius: 5
                        height: statusColumn.height + 20
                        
                        ColumnLayout {
                            id: statusColumn
                            anchors.top: parent.top
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.margins: 10
                            spacing: 10
                            
                            Text {
                                text: "Status"
                                font.pixelSize: 16
                                font.bold: true
                                color: "white"
                            }
                            
                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: "#555555"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                text: firmwareViewModel ? firmwareViewModel.statusMessage : "Bereit"
                                font.pixelSize: 14
                                color: "#cccccc"
                                wrapMode: Text.WordWrap
                            }
                            
                            ProgressBar {
                                Layout.fillWidth: true
                                height: 6
                                from: 0
                                to: 100
                                value: firmwareViewModel ? firmwareViewModel.progress : 0
                                visible: firmwareViewModel && firmwareViewModel.inProgress
                                
                                background: Rectangle {
                                    implicitWidth: 200
                                    implicitHeight: 6
                                    color: "#222222"
                                    radius: 3
                                }
                                
                                contentItem: Rectangle {
                                    width: parent.visualPosition * parent.width
                                    height: parent.height
                                    radius: 2
                                    color: "#00aa00"
                                }
                            }
                        }
                    }
                    
                    // Aktionsschaltflächen
                    Rectangle {
                        Layout.fillWidth: true
                        color: "#333333"
                        radius: 5
                        height: actionColumn.height + 20
                        
                        ColumnLayout {
                            id: actionColumn
                            anchors.top: parent.top
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.margins: 10
                            spacing: 10
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10
                                
                                Button {
                                    Layout.fillWidth: true
                                    text: "Firmware herunterladen"
                                    enabled: root.isConnected && firmwareList.count > 0 && 
                                             firmwareViewModel && !firmwareViewModel.inProgress
                                    
                                    onClicked: {
                                        if (firmwareViewModel) {
                                            firmwareViewModel.downloadFirmware()
                                        }
                                    }
                                }
                                
                                Button {
                                    Layout.fillWidth: true
                                    text: "Firmware installieren"
                                    enabled: root.isConnected && firmwareViewModel && 
                                             firmwareViewModel.firmwareDownloaded && !firmwareViewModel.inProgress
                                    
                                    onClicked: {
                                        if (firmwareViewModel) {
                                            firmwareViewModel.flashFirmware()
                                        }
                                    }
                                }
                            }
                            
                            Button {
                                Layout.fillWidth: true
                                text: "Abbrechen"
                                enabled: firmwareViewModel && firmwareViewModel.inProgress
                                
                                onClicked: {
                                    if (firmwareViewModel) {
                                        firmwareViewModel.cancelOperation()
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
