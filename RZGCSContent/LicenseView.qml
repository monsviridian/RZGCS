import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import com.rzgcs.licensing 1.0

Item {
    id: root
    width: 800
    height: 600
    
    LicenseController {
        id: licenseController
    }
    
    Rectangle {
        anchors.fill: parent
        color: "#1e1e1e"
        
        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width * 0.8
            spacing: 20
            
            Text {
                text: "RZGCS Lizenzmanagement"
                font.pixelSize: 28
                font.bold: true
                color: "white"
                Layout.alignment: Qt.AlignHCenter
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#555555"
            }
            
            // Aktueller Lizenzstatus
            Rectangle {
                Layout.fillWidth: true
                height: licenseStatusLayout.height + 40
                color: "#2a2a2a"
                radius: 5
                
                ColumnLayout {
                    id: licenseStatusLayout
                    anchors.centerIn: parent
                    width: parent.width - 40
                    spacing: 15
                    
                    Text {
                        text: "Aktueller Lizenzstatus"
                        font.pixelSize: 18
                        font.bold: true
                        color: "white"
                    }
                    
                    GridLayout {
                        columns: 2
                        Layout.fillWidth: true
                        rowSpacing: 10
                        columnSpacing: 20
                        
                        Text { 
                            text: "Status:" 
                            font.pixelSize: 16
                            color: "#aaaaaa"
                        }
                        Text { 
                            text: licenseController.isLicensed ? "Lizenziert" : "Nicht lizenziert (Basic)"
                            font.pixelSize: 16
                            color: licenseController.isLicensed ? "#00ff00" : "#ffff00"
                            font.bold: true
                        }
                        
                        Text { 
                            text: "Lizenztyp:" 
                            font.pixelSize: 16
                            color: "#aaaaaa"
                        }
                        Text { 
                            text: licenseController.licenseType
                            font.pixelSize: 16
                            color: "white"
                        }
                        
                        Text { 
                            text: "Gültig bis:" 
                            font.pixelSize: 16
                            color: "#aaaaaa"
                        }
                        Text { 
                            text: licenseController.licenseExpiry
                            font.pixelSize: 16
                            color: "white"
                        }
                    }
                }
            }
            
            // Lizenz aktivieren
            Rectangle {
                Layout.fillWidth: true
                height: activationLayout.height + 40
                color: "#2a2a2a"
                radius: 5
                
                ColumnLayout {
                    id: activationLayout
                    anchors.centerIn: parent
                    width: parent.width - 40
                    spacing: 15
                    
                    Text {
                        text: "Lizenz aktivieren"
                        font.pixelSize: 18
                        font.bold: true
                        color: "white"
                    }
                    
                    TextField {
                        id: licenseKeyInput
                        Layout.fillWidth: true
                        placeholderText: "Lizenzschlüssel eingeben (z.B. RZGCS-PRO-1234-5678-9ABC-DEF0)"
                        font.pixelSize: 16
                        color: "white"
                        background: Rectangle {
                            color: "#333333"
                            radius: 3
                        }
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        
                        Button {
                            text: "Aktivieren"
                            font.pixelSize: 16
                            padding: 10
                            
                            background: Rectangle {
                                color: "#0066cc"
                                radius: 3
                            }
                            
                            onClicked: {
                                var success = licenseController.activateLicense(licenseKeyInput.text)
                                if (success) {
                                    activationMessage.text = "Lizenz erfolgreich aktiviert!"
                                    activationMessage.color = "#00ff00"
                                } else {
                                    activationMessage.text = "Lizenzaktivierung fehlgeschlagen. Ungültiger Schlüssel."
                                    activationMessage.color = "#ff0000"
                                }
                                activationMessage.visible = true
                            }
                        }
                        
                        Button {
                            text: "Deaktivieren"
                            font.pixelSize: 16
                            padding: 10
                            visible: licenseController.isLicensed
                            
                            background: Rectangle {
                                color: "#cc3300"
                                radius: 3
                            }
                            
                            onClicked: {
                                var success = licenseController.deactivateLicense()
                                if (success) {
                                    activationMessage.text = "Lizenz erfolgreich deaktiviert"
                                    activationMessage.color = "#ffff00"
                                } else {
                                    activationMessage.text = "Deaktivierung fehlgeschlagen"
                                    activationMessage.color = "#ff0000"
                                }
                                activationMessage.visible = true
                            }
                        }
                    }
                    
                    Text {
                        id: activationMessage
                        visible: false
                        font.pixelSize: 16
                        font.italic: true
                    }
                }
            }
            
            // Verfügbare Lizenzen
            Rectangle {
                Layout.fillWidth: true
                height: licensesLayout.height + 40
                color: "#2a2a2a"
                radius: 5
                
                ColumnLayout {
                    id: licensesLayout
                    anchors.centerIn: parent
                    width: parent.width - 40
                    spacing: 15
                    
                    Text {
                        text: "Verfügbare Lizenzen"
                        font.pixelSize: 18
                        font.bold: true
                        color: "white"
                    }
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        
                        // Basic-Lizenz
                        Rectangle {
                            Layout.fillWidth: true
                            height: 80
                            color: "#252525"
                            border.color: licenseController.licenseType === "Basic" ? "#ffff00" : "transparent"
                            border.width: 2
                            radius: 3
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 20
                                
                                Rectangle {
                                    width: 60
                                    height: 60
                                    radius: 30
                                    color: "#555555"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "B"
                                        font.pixelSize: 24
                                        font.bold: true
                                        color: "white"
                                    }
                                }
                                
                                ColumnLayout {
                                    spacing: 5
                                    Layout.fillWidth: true
                                    
                                    Text {
                                        text: "Basic"
                                        font.pixelSize: 18
                                        font.bold: true
                                        color: "white"
                                    }
                                    
                                    Text {
                                        text: "Grundlegende Steuerung, begrenzte Sensoren"
                                        font.pixelSize: 14
                                        color: "#aaaaaa"
                                    }
                                }
                                
                                Text {
                                    text: "Kostenlos"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: "#ffff00"
                                }
                            }
                        }
                        
                        // Professional-Lizenz
                        Rectangle {
                            Layout.fillWidth: true
                            height: 80
                            color: "#252525"
                            border.color: licenseController.licenseType === "Professional" ? "#00ff00" : "transparent"
                            border.width: 2
                            radius: 3
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 20
                                
                                Rectangle {
                                    width: 60
                                    height: 60
                                    radius: 30
                                    color: "#0066cc"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "P"
                                        font.pixelSize: 24
                                        font.bold: true
                                        color: "white"
                                    }
                                }
                                
                                ColumnLayout {
                                    spacing: 5
                                    Layout.fillWidth: true
                                    
                                    Text {
                                        text: "Professional"
                                        font.pixelSize: 18
                                        font.bold: true
                                        color: "white"
                                    }
                                    
                                    Text {
                                        text: "Alle Sensorfunktionen, Partikelanimation, erweiterte Protokollierung"
                                        font.pixelSize: 14
                                        color: "#aaaaaa"
                                    }
                                }
                                
                                Text {
                                    text: "€99/Jahr"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: "#00ff00"
                                }
                            }
                        }
                        
                        // Enterprise-Lizenz
                        Rectangle {
                            Layout.fillWidth: true
                            height: 80
                            color: "#252525"
                            border.color: licenseController.licenseType === "Enterprise" ? "#00ffff" : "transparent"
                            border.width: 2
                            radius: 3
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 20
                                
                                Rectangle {
                                    width: 60
                                    height: 60
                                    radius: 30
                                    color: "#9900cc"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "E"
                                        font.pixelSize: 24
                                        font.bold: true
                                        color: "white"
                                    }
                                }
                                
                                ColumnLayout {
                                    spacing: 5
                                    Layout.fillWidth: true
                                    
                                    Text {
                                        text: "Enterprise"
                                        font.pixelSize: 18
                                        font.bold: true
                                        color: "white"
                                    }
                                    
                                    Text {
                                        text: "Angel Mode, benutzerdefinierte Flugpfade, unbegrenzter Support"
                                        font.pixelSize: 14
                                        color: "#aaaaaa"
                                    }
                                }
                                
                                Text {
                                    text: "€299/Jahr"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: "#00ffff"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
