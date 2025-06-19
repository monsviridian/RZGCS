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
    property var encryptionData: ({})
    
    // Signals
    signal encryptKeysClicked()
    signal decryptKeysClicked()
    
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
                    text: "Key Encryptor"
                    font.pixelSize: 20
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Encrypt Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: encryptKeysClicked()
                }
                
                Button {
                    text: "Decrypt Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: decryptKeysClicked()
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
                
                // Encryption Settings
                GroupBox {
                    title: "Encryption Settings"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        // Encryption Type
                        ComboBox {
                            id: encryptionTypeSelector
                            Layout.fillWidth: true
                            model: ["Symmetric", "Asymmetric", "Hybrid"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Encryption Algorithm
                        ComboBox {
                            id: encryptionAlgorithmSelector
                            Layout.fillWidth: true
                            model: {
                                switch(encryptionTypeSelector.currentText) {
                                    case "Symmetric": return ["AES", "ChaCha20", "Twofish"]
                                    case "Asymmetric": return ["RSA", "ECC", "ElGamal"]
                                    case "Hybrid": return ["RSA-AES", "ECC-AES", "ElGamal-AES"]
                                    default: return []
                                }
                            }
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Encryption Mode
                        ComboBox {
                            id: encryptionModeSelector
                            Layout.fillWidth: true
                            model: ["ECB", "CBC", "CFB", "OFB", "CTR", "GCM"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Key Size
                        ComboBox {
                            id: keySizeSelector
                            Layout.fillWidth: true
                            model: {
                                switch(encryptionAlgorithmSelector.currentText) {
                                    case "AES": return ["128", "192", "256"]
                                    case "ChaCha20": return ["256"]
                                    case "Twofish": return ["128", "192", "256"]
                                    case "RSA": return ["2048", "4096", "8192"]
                                    case "ECC": return ["256", "384", "521"]
                                    case "ElGamal": return ["2048", "4096", "8192"]
                                    default: return []
                                }
                            }
                            enabled: isConnected && selectedUavId !== ""
                        }
                    }
                }
                
                // Encryption Status
                GroupBox {
                    title: "Encryption Status"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        Label {
                            text: "Encryption Type: " + (encryptionData.type || "N/A")
                        }
                        
                        Label {
                            text: "Encryption Algorithm: " + (encryptionData.algorithm || "N/A")
                        }
                        
                        Label {
                            text: "Encryption Mode: " + (encryptionData.mode || "N/A")
                        }
                        
                        Label {
                            text: "Key Size: " + (encryptionData.keySize || "N/A")
                        }
                        
                        Label {
                            text: "Encryption Status: " + (encryptionData.status || "N/A")
                        }
                        
                        Label {
                            text: "Encryption Time: " + (encryptionData.time || "N/A")
                        }
                        
                        Label {
                            text: "Encryption Result: " + (encryptionData.result || "N/A")
                        }
                    }
                }
                
                // Encryption Details
                GroupBox {
                    title: "Encryption Details"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ScrollView {
                        anchors.fill: parent
                        clip: true
                        
                        ListView {
                            id: encryptionDetailsList
                            model: encryptionData.details || []
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
                                        color: modelData.status === "Encrypted" ? "green" : "red"
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
        title: "Key Encryptor"
        buttons: MessageDialog.Ok
    }
    
    // Functions
    function showMessage(title, message) {
        messageDialog.title = title
        messageDialog.text = message
        messageDialog.open()
    }
    
    function updateEncryptionData(data) {
        encryptionData = data
    }
} 