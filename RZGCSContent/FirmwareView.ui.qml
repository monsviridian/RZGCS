import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

Rectangle {
    id: root
    color: "#181818"
    border.color: "#333"
    border.width: 1

    // ViewModel binding - must be set from parent
    property var firmwareViewModel
    
    // File Dialog for importing firmware files
    FileDialog {
        id: fileDialog
        title: "Firmware-Datei auswählen"
        nameFilters: ["Firmware-Dateien (*.hex *.bin *.px4)", "HEX-Dateien (*.hex)", "BIN-Dateien (*.bin)", "PX4-Dateien (*.px4)", "Alle Dateien (*)"]
        onAccepted: {
            if (firmwareViewModel) {
                firmwareViewModel.import_firmware_file(fileDialog.fileUrl.toString().replace("file:///", ""))
            }
        }
    }
    
    Component.onCompleted: {
        console.log("FirmwareView: Component completed")
        console.log("FirmwareView: firmwareViewModel:", firmwareViewModel)
        if (firmwareViewModel) {
            console.log("FirmwareView: is_connected:", firmwareViewModel.is_connected)
            console.log("FirmwareView: available_ports:", firmwareViewModel.available_ports)
            console.log("FirmwareView: imported_file_path:", firmwareViewModel.imported_file_path)
            firmwareViewModel.initialize()
        } else {
            console.log("W: FirmwareView: firmwareViewModel not available")
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 24

        // Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 20

            Text {
                text: "Firmware Flasher"
                color: "#e0e0e0"
                font.pixelSize: 28
                font.bold: true
            }

            Item { Layout.fillWidth: true }

            // Status-Rechteck im JAGCS-Stil
            Rectangle {
                width: 140
                height: 36
                radius: 18
                color: firmwareViewModel && firmwareViewModel.is_connected ? "#4caf50" : "#f44336"
                border.color: firmwareViewModel && firmwareViewModel.is_connected ? "#45a049" : "#d32f2f"
                border.width: 1
                Text {
                    anchors.centerIn: parent
                    text: firmwareViewModel && firmwareViewModel.is_connected ? "✓ Verbunden" : "✗ Nicht verbunden"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                }
            }
        }

        // Hauptbereich
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 32

            // Linke Spalte: Geräte, Firmware, Import
            ColumnLayout {
                spacing: 20
                Layout.preferredWidth: 400

                // Geräteverbindung (Mehrfachauswahl)
                GroupBox {
                    title: "Geräteverbindung (Mehrfachauswahl)"
                    Layout.fillWidth: true
                    background: Rectangle {
                        color: "#232323"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 6
                    }
                    label: Text {
                        text: parent.title
                        color: "#00bcd4"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12
                        ListView {
                            id: portListView
                            Layout.fillWidth: true
                            height: Math.min(200, (firmwareViewModel && firmwareViewModel.available_ports ? firmwareViewModel.available_ports.length * 36 : 0))
                            model: firmwareViewModel ? firmwareViewModel.available_ports : []
                            delegate: RowLayout {
                                spacing: 8
                                CheckBox {
                                    id: portCheckBox
                                    checked: firmwareViewModel && firmwareViewModel.selected_ports && firmwareViewModel.selected_ports.indexOf(modelData) !== -1
                                    onCheckedChanged: {
                                        if (firmwareViewModel) {
                                            firmwareViewModel.toggle_port_selection(modelData, checked)
                                        }
                                    }
                                }
                                Text { text: modelData; color: "white"; font.pixelSize: 14 }
                            }
                        }
                    }
                }

                // Firmware-Auswahl
                GroupBox {
                    title: "Firmware-Auswahl"
                    Layout.fillWidth: true
                    background: Rectangle {
                        color: "#232323"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 6
                    }
                    label: Text {
                        text: parent.title
                        color: "#00bcd4"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12
                        CheckBox {
                            id: developerVersionsCheck
                            text: "Entwicklungsversionen anzeigen"
                            checked: firmwareViewModel ? firmwareViewModel.show_developer_versions : false
                            onCheckedChanged: if (firmwareViewModel) firmwareViewModel.show_developer_versions = checked
                            contentItem: Text {
                                text: developerVersionsCheck.text
                                color: "white"
                                font.pixelSize: 14
                                leftPadding: developerVersionsCheck.indicator.width + developerVersionsCheck.spacing
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            height: 140
                            color: "#2a2a2a"
                            radius: 4
                            border.color: "#555"
                            border.width: 1
                            ListView {
                                anchors.fill: parent
                                anchors.margins: 4
                                model: firmwareViewModel ? firmwareViewModel.firmware_list : []
                                delegate: Rectangle {
                                    width: parent.width; height: 44; 
                                    color: ListView.isCurrentItem ? "#3a3a3a" : "transparent"
                                    radius: 4
                                    RowLayout {
                                        anchors.fill: parent; 
                                        anchors.margins: 8
                                        spacing: 12
                                        Text { 
                                            text: modelData.name; 
                                            color: "white"; 
                                            font.bold: true; 
                                            font.pixelSize: 14 
                                        }
                                        Text { 
                                            text: modelData.version; 
                                            color: "#00bcd4"; 
                                            font.pixelSize: 12 
                                        }
                                        Item { Layout.fillWidth: true }
                                        Text { 
                                            text: modelData.description; 
                                            color: "#999999"; 
                                            font.pixelSize: 11 
                                        }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            parent.ListView.view.currentIndex = index
                                            if (firmwareViewModel) {
                                                firmwareViewModel.selected_firmware_index = index
                                                firmwareViewModel.clear_imported_file()
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        Button {
                            Layout.fillWidth: true
                            height: 40
                            text: "⬇️ Firmware herunterladen"
                            enabled: firmwareViewModel && firmwareViewModel.selected_firmware_index >= 0 && !firmwareViewModel.in_progress && !firmwareViewModel.imported_file_path
                            onClicked: if (firmwareViewModel) firmwareViewModel.download_firmware()
                            background: Rectangle {
                                color: parent.enabled ? "#ff9800" : "#555"
                                radius: 6
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "white"
                                font.pixelSize: 16
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }

                // Eigene Firmware importieren
                GroupBox {
                    title: "Eigene Firmware importieren"
                    Layout.fillWidth: true
                    background: Rectangle {
                        color: "#232323"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 6
                    }
                    label: Text {
                        text: parent.title
                        color: "#00ff00"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12
                        RowLayout {
                            Layout.fillWidth: true
                            Button {
                                height: 40
                                text: "📁 Datei auswählen"
                                onClicked: fileDialog.open()
                                background: Rectangle {
                                    color: "#9c27b0"
                                    radius: 6
                                }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.pixelSize: 16
                                    font.bold: true
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                            Text {
                                text: firmwareViewModel && firmwareViewModel.imported_file_path ? firmwareViewModel.imported_file_name : "Keine Datei ausgewählt"
                                color: firmwareViewModel && firmwareViewModel.imported_file_path ? "#00ff00" : "#999999"
                                font.pixelSize: 13
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }
                        }
                        Text {
                            visible: firmwareViewModel && firmwareViewModel.imported_file_info
                            text: firmwareViewModel ? firmwareViewModel.imported_file_info : ""
                            color: "#cccccc"; font.pixelSize: 11
                        }
                    }
                }

                // Flash-Button (groß und prominent)
                Button {
                    Layout.fillWidth: true
                    height: 50
                    text: "⚡ Alle ausgewählten flashen"
                    enabled: firmwareViewModel && firmwareViewModel.selected_ports && firmwareViewModel.selected_ports.length > 0 && ((firmwareViewModel.firmware_downloaded && !firmwareViewModel.imported_file_path) || firmwareViewModel.imported_file_path) && !firmwareViewModel.in_progress
                    onClicked: if (firmwareViewModel) firmwareViewModel.flash_multiple_devices()
                    background: Rectangle {
                        color: parent.enabled ? "#ffb300" : "#555"
                        radius: 8
                        border.color: parent.enabled ? "#ffa000" : "#444"
                        border.width: 2
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.pixelSize: 18
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                // Wipe Settings Checkbox
                CheckBox {
                    id: wipeSettingsCheck
                    text: "🗑️ Einstellungen löschen (Wipe Settings)"
                    checked: firmwareViewModel ? firmwareViewModel.wipe_settings : false
                    onCheckedChanged: if (firmwareViewModel) firmwareViewModel.wipe_settings = checked
                    contentItem: Text {
                        text: wipeSettingsCheck.text
                        color: "#ff6600"
                        font.pixelSize: 14
                        font.bold: true
                        leftPadding: wipeSettingsCheck.indicator.width + wipeSettingsCheck.spacing
                    }
                }
            }

            // Rechte Spalte: Status, Log, Anleitung
            ColumnLayout {
                spacing: 20
                Layout.preferredWidth: 500

                // Status & Fortschritt
                GroupBox {
                    title: "Flash-Status pro Port"
                    Layout.fillWidth: true
                    background: Rectangle {
                        color: "#232323"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 6
                    }
                    label: Text {
                        text: parent.title
                        color: "#00bcd4"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    ListView {
                        Layout.fillWidth: true
                        height: Math.min(200, (firmwareViewModel && firmwareViewModel.selected_ports ? firmwareViewModel.selected_ports.length * 36 : 0))
                        model: firmwareViewModel ? firmwareViewModel.selected_ports : []
                        delegate: RowLayout {
                            spacing: 8
                            Text { text: modelData; color: "#00bcd4"; font.pixelSize: 14 }
                            ProgressBar {
                                value: firmwareViewModel && firmwareViewModel.port_progress && firmwareViewModel.port_progress[modelData] ? firmwareViewModel.port_progress[modelData] / 100.0 : 0
                                width: 120
                                height: 12
                            }
                            Text {
                                text: firmwareViewModel && firmwareViewModel.port_status && firmwareViewModel.port_status[modelData] ? firmwareViewModel.port_status[modelData] : ""
                                color: "#cccccc"
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                // Log-Bereich
                GroupBox {
                    title: "Log"
                    Layout.fillWidth: true
                    background: Rectangle {
                        color: "#232323"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 6
                    }
                    label: Text {
                        text: parent.title
                        color: "#00bcd4"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 150
                            clip: true
                            TextArea {
                                id: logTextArea
                                readOnly: true
                                text: firmwareViewModel ? firmwareViewModel.log_text : ""
                                color: "#cccccc"
                                font.pixelSize: 12
                                font.family: "Consolas, Monaco, monospace"
                                wrapMode: TextArea.Wrap
                                background: Rectangle {
                                    color: "#1a1a1a"
                                    border.color: "#555"
                                    border.width: 1
                                    radius: 4
                                }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Button {
                                text: "🗑️ Log löschen"
                                height: 32
                                onClicked: if (firmwareViewModel) firmwareViewModel.clear_log()
                                background: Rectangle {
                                    color: "#f44336"
                                    radius: 4
                                }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.pixelSize: 12
                                    font.bold: true
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: "Auto-Scroll: "
                                color: "#cccccc"
                                font.pixelSize: 12
                            }
                            CheckBox {
                                id: autoScrollCheck
                                checked: true
                                contentItem: Text {
                                    text: "Aktiviert"
                                    color: "#cccccc"
                                    font.pixelSize: 12
                                    leftPadding: autoScrollCheck.indicator.width + autoScrollCheck.spacing
                                }
                            }
                        }
                    }
                }

                // Anleitung
                GroupBox {
                    title: "Anleitung"
                    Layout.fillWidth: true
                    background: Rectangle {
                        color: "#232323"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 6
                    }
                    label: Text {
                        text: parent.title
                        color: "#00bcd4"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8
                        Text {
                            text: "1. 🔌 COM-Port wählen und Gerät verbinden\n2. 📋 Firmware aus Liste wählen ODER eigene Datei importieren\n3. ⬇️ Firmware herunterladen (optional)\n4. ⚡ Firmware flashen\n\n⚠️ Wichtige Hinweise:\n• Gerät muss im Bootloader-Modus sein\n• Flash-Vorgang nicht unterbrechen\n• Wipe Settings löscht alle Parameter\n• Backup vor dem Flashen erstellen"
                            color: "#cccccc"; font.pixelSize: 13; wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
    }
}
