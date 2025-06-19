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
    property var signingData: ({})
    
    // Signals
    signal signKeysClicked()
    signal encryptKeysClicked()
    
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
                    text: "Key Signer"
                    font.pixelSize: 20
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Sign Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: signKeysClicked()
                }
                
                Button {
                    text: "Encrypt Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: encryptKeysClicked()
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
                
                // Signing Settings
                GroupBox {
                    title: "Signing Settings"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        // Signing Type
                        ComboBox {
                            id: signingTypeSelector
                            Layout.fillWidth: true
                            model: ["Digital Signature", "HMAC", "MAC", "Certificate"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Signing Algorithm
                        ComboBox {
                            id: signingAlgorithmSelector
                            Layout.fillWidth: true
                            model: {
                                switch(signingTypeSelector.currentText) {
                                    case "Digital Signature": return ["RSA", "ECDSA", "EdDSA"]
                                    case "HMAC": return ["HMAC-SHA256", "HMAC-SHA384", "HMAC-SHA512"]
                                    case "MAC": return ["CMAC", "GMAC"]
                                    case "Certificate": return ["X.509", "PGP"]
                                    default: return []
                                }
                            }
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Signing Mode
                        ComboBox {
                            id: signingModeSelector
                            Layout.fillWidth: true
                            model: ["Detached", "Attached", "Enveloped"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                    }
                }
                
                // Signing Status
                GroupBox {
                    title: "Signing Status"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        Label {
                            text: "Signing Type: " + (signingData.type || "N/A")
                        }
                        
                        Label {
                            text: "Signing Algorithm: " + (signingData.algorithm || "N/A")
                        }
                        
                        Label {
                            text: "Signing Mode: " + (signingData.mode || "N/A")
                        }
                        
                        Label {
                            text: "Signing Status: " + (signingData.status || "N/A")
                        }
                        
                        Label {
                            text: "Signing Time: " + (signingData.time || "N/A")
                        }
                        
                        Label {
                            text: "Signing Result: " + (signingData.result || "N/A")
                        }
                    }
                }
                
                // Signing Details
                GroupBox {
                    title: "Signing Details"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ScrollView {
                        anchors.fill: parent
                        clip: true
                        
                        ListView {
                            id: signingDetailsList
                            model: signingData.details || []
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
                                        color: modelData.status === "Signed" ? "green" : "red"
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
        title: "Key Signer"
        buttons: MessageDialog.Ok
    }
    
    // Functions
    function showMessage(title, message) {
        messageDialog.title = title
        messageDialog.text = message
        messageDialog.open()
    }
    
    function updateSigningData(data) {
        signingData = data
    }
} 