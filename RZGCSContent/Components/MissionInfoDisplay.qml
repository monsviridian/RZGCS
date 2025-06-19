import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * MissionInfoDisplay - Shows mission status information
 * Displays current waypoint, total waypoints, and distance to next waypoint
 */
Rectangle {
    id: root
    color: "#333333"
    radius: 4
    
    // Properties
    property int currentWaypoint: 0
    property int waypointCount: 0
    property string distanceToWaypoint: "--"
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8
        
        // Title
        Label {
            text: "Mission Status"
            font.pixelSize: 14
            font.bold: true
            color: "#FFFFFF"
            Layout.fillWidth: true
        }
        
        // Mission information
        GridLayout {
            columns: 2
            Layout.fillWidth: true
            
            Label {
                text: "Current WP:"
                color: "#CCCCCC"
                font.pixelSize: 12
            }
            
            Label {
                text: currentWaypoint + " / " + waypointCount
                color: "#FFFFFF"
                font.pixelSize: 12
                font.bold: true
            }
            
            Label {
                text: "Distance to WP:"
                color: "#CCCCCC"
                font.pixelSize: 12
            }
            
            Label {
                text: distanceToWaypoint + " m"
                color: "#FFFFFF"
                font.pixelSize: 12
                font.bold: true
            }
        }
        
        // Mission controls
        RowLayout {
            Layout.fillWidth: true
            spacing: 6
            
            Button {
                text: "Upload Mission"
                Layout.fillWidth: true
                enabled: missionPlannerStyle && missionPlannerStyle.connected
                onClicked: {
                    if (missionPlannerStyle) {
                        missionPlannerStyle.uploadMission();
                    }
                }
            }
            
            Button {
                text: "Start Mission"
                Layout.fillWidth: true
                enabled: missionPlannerStyle && missionPlannerStyle.connected && 
                         missionPlannerStyle.armed && waypointCount > 0
                onClicked: {
                    if (missionPlannerStyle) {
                        missionPlannerStyle.startMission();
                    }
                }
            }
        }
    }
}
