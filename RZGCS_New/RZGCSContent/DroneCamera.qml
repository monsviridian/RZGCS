import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

Rectangle {
    id: droneCameraView
    color: "#181f23"
    radius: 12
    border.color: "#23343b"
    border.width: 2

    property string videoSource: ""  // URL or source for the video feed
    property bool isConnected: false
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 8

        // Header
        Text {
            text: "CAMERA FEED"
            color: "#3ee6ff"
            font.pixelSize: 18
            font.bold: true
        }

        // Camera View
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#0f1416"
            radius: 8

            // Placeholder when no feed
            Text {
                anchors.centerIn: parent
                text: isConnected ? "Connecting..." : "No Camera Feed"
                color: "#e6faff"
                font.pixelSize: 16
            }

            // Video output when feed is available
            VideoOutput {
                id: videoOutput
                anchors.fill: parent
                visible: droneCameraView.videoSource !== ""
                source: mediaPlayer

                MediaPlayer {
                    id: mediaPlayer
                    source: droneCameraView.videoSource
                    autoPlay: true
                }
            }
        }

        // Camera Controls
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Button {
                text: "Snapshot"
                enabled: droneCameraView.isConnected
                onClicked: {
                    // Implement snapshot functionality
                }
            }

            Button {
                text: "Record"
                enabled: droneCameraView.isConnected
                onClicked: {
                    // Implement recording functionality
                }
            }

            Item { Layout.fillWidth: true }  // Spacer

            Text {
                text: isConnected ? "Connected" : "Disconnected"
                color: isConnected ? "#00ff00" : "#ff0000"
                font.pixelSize: 14
            }
        }
    }
} 