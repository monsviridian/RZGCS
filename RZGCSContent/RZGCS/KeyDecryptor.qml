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
    property var decryptionData: ({})
    
    // Signals
    signal decryptKeysClicked()
    signal manageKeysClicked()
    
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
                    text: "Key Decryptor"
                    font.pixelSize: 20
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Decrypt Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: decryptKeysClicked()
                }
                
                Button {
                    text: "Manage Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: manageKeysClicked()
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
                
                // Decryption Settings
                GroupBox {
                    title: "Decryption Settings"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        // Decryption Type
                        ComboBox {
                            id: decryptionTypeSelector
                            Layout.fillWidth: true
                            model: ["Symmetric", "Asymmetric", "Hybrid"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Decryption Algorithm
                        ComboBox {
                            id: decryptionAlgorithmSelector
                            Layout.fillWidth: true
                            model: {
                                switch(decryptionTypeSelector.currentText) {
                                    case "Symmetric": return ["AES", "ChaCha20", "Twofish"]
                                    case "Asymmetric": return ["RSA", "ECC", "ElGamal"]
                                    case "Hybrid": return ["RSA-AES", "ECC-AES", "ElGamal-AES"]
                                    default: return []
                                }
                            }
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Decryption Mode
                        ComboBox {
                            id: decryptionModeSelector
                            Layout.fillWidth: true
                            model: ["ECB", "CBC", "CFB", "OFB", "CTR", "GCM"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Key Size
                        ComboBox {
                            id: keySizeSelector
                            Layout.fillWidth: true
                            model: {
                                switch(decryptionAlgorithmSelector.currentText) {
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
                
                // Decryption Status
                GroupBox {
                    title: "Decryption Status"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        Label {
                            text: "Decryption Type: " + (decryptionData.type || "N/A")
                        }
                        
                        Label {
                            text: "Decryption Algorithm: " + (decryptionData.algorithm || "N/A")
                        }
                        
                        Label {
                            text: "Decryption Mode: " + (decryptionData.mode || "N/A")
                        }
                        
                        Label {
                            text: "Key Size: " + (decryptionData.keySize || "N/A")
                        }
                        
                        Label {
                            text: "Decryption Status: " + (decryptionData.status || "N/A")
                        }
                        
                        Label {
                            text: "Decryption Time: " + (decryptionData.time || "N/A")
                        }
                        
                        Label {
                            text: "Decryption Result: " + (decryptionData.result || "N/A")
                        }
                    }
                }
                
                // Decryption Details
                GroupBox {
                    title: "Decryption Details"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ScrollView {
                        anchors.fill: parent
                        clip: true
                        
                        ListView {
                            id: decryptionDetailsList
                            model: decryptionData.details || []
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
                                        color: modelData.status === "Decrypted" ? "green" : "red"
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
        title: "Key Decryptor"
        buttons: MessageDialog.Ok
    }
    
    // Functions
    function showMessage(title, message) {
        messageDialog.title = title
        messageDialog.text = message
        messageDialog.open()
    }
    
    function updateDecryptionData(data) {
        decryptionData = data
    }
} 