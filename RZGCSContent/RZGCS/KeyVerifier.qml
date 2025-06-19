import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Dialogs

Item {
    id: root
    
    // Properties
    property bool isConnected: false
    property string selectedUavId: ""
    property var verificationData: ({})
    
    // Signals
    signal verifyKeysClicked()
    signal signKeysClicked()
    
    // Layout
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        
        // Header
        Rectangle {
            Layout.fillWidth: true
            height: 50
            color: "#2c3e50"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                Label {
                    text: "Key Verifier"
                    font.pixelSize: 20
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Verify Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: verifyKeysClicked()
                }
                
                Button {
                    text: "Sign Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: signKeysClicked()
                }
            }
        }
        
        // Content
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#34495e"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                // Verification Settings
                GroupBox {
                    title: "Verification Settings"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        // Verification Type
                        ComboBox {
                            id: verificationTypeSelector
                            Layout.fillWidth: true
                            model: ["Digital Signature", "Certificate", "Hash", "MAC"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Verification Algorithm
                        ComboBox {
                            id: verificationAlgorithmSelector
                            Layout.fillWidth: true
                            model: {
                                switch(verificationTypeSelector.currentText) {
                                    case "Digital Signature": return ["RSA", "ECDSA", "EdDSA"]
                                    case "Certificate": return ["X.509", "PGP"]
                                    case "Hash": return ["SHA-256", "SHA-384", "SHA-512"]
                                    case "MAC": return ["HMAC", "CMAC", "GMAC"]
                                    default: return []
                                }
                            }
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Verification Mode
                        ComboBox {
                            id: verificationModeSelector
                            Layout.fillWidth: true
                            model: ["Online", "Offline", "Hybrid"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                    }
                }
                
                // Verification Status
                GroupBox {
                    title: "Verification Status"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        Label {
                            text: "Verification Type: " + (verificationData.type || "N/A")
                        }
                        
                        Label {
                            text: "Verification Algorithm: " + (verificationData.algorithm || "N/A")
                        }
                        
                        Label {
                            text: "Verification Mode: " + (verificationData.mode || "N/A")
                        }
                        
                        Label {
                            text: "Verification Status: " + (verificationData.status || "N/A")
                        }
                        
                        Label {
                            text: "Verification Time: " + (verificationData.time || "N/A")
                        }
                        
                        Label {
                            text: "Verification Result: " + (verificationData.result || "N/A")
                        }
                    }
                }
                
                // Verification Details
                GroupBox {
                    title: "Verification Details"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ScrollView {
                        anchors.fill: parent
                        clip: true
                        
                        ListView {
                            id: verificationDetailsList
                            model: verificationData.details || []
                            delegate: ItemDelegate {
                                width: parent.width
                                contentItem: ColumnLayout {
                                    Label {
                                        text: modelData.name
                                        font.bold: true
                                    }
                                    Label {
                                        text: modelData.description
                                        wrapMode: Text.WordWrap
                                    }
                                    Label {
                                        text: "Status: " + modelData.status
                                        color: modelData.status === "Verified" ? "green" : "red"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Message Dialog
    MessageDialog {
        id: messageDialog
        title: "Key Verifier"
        buttons: MessageDialog.Ok
    }
    
    // Functions
    function showMessage(title, message) {
        messageDialog.title = title
        messageDialog.text = message
        messageDialog.open()
    }
    
    function updateVerificationData(data) {
        verificationData = data
    }
} 