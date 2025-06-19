import QtQuick 2.15
import QtQuick.Controls 2.15
import QtLocation 5.15
import QtPositioning 5.15

/**
 * ArduPilotMap - Emulates the map view from Mission Planner
 * Provides map display with vehicle position, waypoints and mission planning
 */
Item {
    id: mapRoot
    
    // Properties for map position and vehicle
    property real vehicleLat: 49.445232
    property real vehicleLon: 7.769488
    property real vehicleHeading: 0
    property bool isConnected: false
    property bool isArmed: false
    property string vehicleType: "copter" // copter, plane, rover, heli
    
    // Properties for mission planning
    property var missionWaypoints: []
    property var homePosition: QtPositioning.coordinate(vehicleLat, vehicleLon)
    property bool waypointMode: false  // Modus zum Setzen von Wegpunkten
    property int waypointCount: waypointModel ? waypointModel.count : 0  // Anzahl der Wegpunkte
    
    // Signals
    signal waypointAdded(double lat, double lon, double alt)
    signal waypointMoved(int index, double lat, double lon, double alt)
    signal homePositionSet(double lat, double lon)
    
    // Private properties
    property var _mapItems: []  // To track all map items
    
    Plugin {
        id: mapPlugin
        name: "osm" // OpenStreetMap
    }
    
    Map {
        id: map
        anchors.fill: parent
        plugin: mapPlugin
        center: homePosition
        zoomLevel: 18
        
        // Klick-Handler für Wegpunkte
        MouseArea {
            anchors.fill: parent
            onClicked: {
                if (mapRoot.waypointMode) {
                    // Nur im Wegpunktmodus Wegpunkte setzen
                    var coordinate = map.toCoordinate(Qt.point(mouseX, mouseY))
                    console.log("Wegpunkt gesetzt bei: " + coordinate.latitude + ", " + coordinate.longitude)
                    
                    // Wegpunkt hinzufügen (mit Standardhöhe von 50m)
                    addWaypoint(coordinate.latitude, coordinate.longitude, 50)
                    
                    // Signal an die übergeordnete Komponente senden
                    waypointAdded(coordinate.latitude, coordinate.longitude, 50)
                }
            }
            
            // Wegpunktmodus-Indikator anzeigen
            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 10
                width: waypointModeText.width + 20
                height: waypointModeText.height + 10
                color: "#22AA22"
                opacity: mapRoot.waypointMode ? 0.8 : 0
                radius: 5
                visible: mapRoot.waypointMode
                
                Text {
                    id: waypointModeText
                    anchors.centerIn: parent
                    text: "Wegpunkt-Modus aktiv"
                    color: "white"
                    font.bold: true
                }
                
                Behavior on opacity {
                    NumberAnimation { duration: 300 }
                }
            }
        }
        
        // Map controls
        MapItemView {
            id: waypointView
            model: ListModel { id: waypointModel }
            delegate: MapQuickItem {
                id: waypointMarker
                coordinate: QtPositioning.coordinate(model.lat, model.lon)
                anchorPoint.x: waypointIcon.width/2
                anchorPoint.y: waypointIcon.height
                sourceItem: Column {
                    Rectangle {
                        id: waypointIcon
                        width: 24
                        height: 24
                        radius: width/2
                        color: "green"
                        border.color: "white"
                        border.width: 2
                        
                        Text {
                            anchors.centerIn: parent
                            text: model.index
                            color: "white"
                            font.bold: true
                            font.pixelSize: 14
                        }
                    }
                    
                    Text {
                        text: model.alt.toFixed(1) + "m"
                        color: "white"
                        style: Text.Outline
                        styleColor: "black"
                        font.pixelSize: 10
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
                
                // Make waypoints draggable
                MouseArea {
                    anchors.fill: parent
                    drag.target: parent
                    onReleased: {
                        var coord = map.toCoordinate(Qt.point(parent.x, parent.y))
                        waypointMoved(model.index, coord.latitude, coord.longitude, model.alt)
                    }
                }
            }
        }
        
        // Home position marker
        MapQuickItem {
            id: homeMarker
            coordinate: homePosition
            anchorPoint.x: homeIcon.width/2
            anchorPoint.y: homeIcon.height
            sourceItem: Column {
                Image {
                    id: homeIcon
                    source: "../Assets/markers/home_marker.svg"
                    width: 32
                    height: 32
                    sourceSize.width: 32
                    sourceSize.height: 32
                }
                Text {
                    text: "H"
                    color: "white"
                    style: Text.Outline
                    styleColor: "black"
                    font.bold: true
                    font.pixelSize: 12
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }
        
        // Vehicle marker
        MapQuickItem {
            id: vehicleMarker
            coordinate: QtPositioning.coordinate(vehicleLat, vehicleLon)
            anchorPoint.x: vehicleIcon.width/2
            anchorPoint.y: vehicleIcon.height/2
            visible: isConnected
            
            sourceItem: Item {
                width: 48
                height: 48
                
                Image {
                    id: vehicleIcon
                    anchors.centerIn: parent
                    source: {
                        if (vehicleType === "copter") return "../../Assets/drone.png";
                        if (vehicleType === "plane") return "../../Assets/vehicles/plane.svg";
                        if (vehicleType === "rover") return "../../Assets/vehicles/rover.svg";
                        if (vehicleType === "heli") return "../../Assets/vehicles/helicopter.svg";
                        return "../../Assets/drone.png";
                    }
                    width: 48
                    height: 48
                    sourceSize.width: 48
                    sourceSize.height: 48
                    
                    // Rotate image based on heading
                    transform: Rotation {
                        origin.x: vehicleIcon.width/2
                        origin.y: vehicleIcon.height/2
                        angle: vehicleHeading
                    }
                }
                
                // Arming status indicator
                Rectangle {
                    width: 10
                    height: 10
                    radius: width/2
                    color: isArmed ? "green" : "red"
                    border.color: "white"
                    border.width: 1
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                }
            }
        }
        
        // Mission line path
        MapPolyline {
            id: missionPath
            line.width: 3
            line.color: "yellow"
            path: {
                var coords = [];
                // Add home position first
                coords.push(homePosition);
                
                // Add all waypoints
                for (var i = 0; i < waypointModel.count; i++) {
                    var item = waypointModel.get(i);
                    coords.push(QtPositioning.coordinate(item.lat, item.lon));
                }
                return coords;
            }
        }
        
        // Mouse area for adding waypoints
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            
            onClicked: {
                if (mouse.button === Qt.RightButton) {
                    // Right click to add waypoint
                    var coord = map.toCoordinate(Qt.point(mouse.x, mouse.y))
                    waypointAdded(coord.latitude, coord.longitude, 50.0) // Default altitude of 50m
                } else if (mouse.button === Qt.LeftButton) {
                    // Left click to set home position
                    var coord = map.toCoordinate(Qt.point(mouse.x, mouse.y))
                    homePosition = coord
                    homePositionChanged(coord.latitude, coord.longitude)
                }
            }
        }
    }
    
    // Functions to manage waypoints
    function addWaypoint(lat, lon, alt) {
        waypointModel.append({
            "index": waypointModel.count + 1,
            "lat": lat,
            "lon": lon,
            "alt": alt
        });
        updateMissionPath();
    }
    
    function updateWaypoint(index, lat, lon, alt) {
        if (index >= 0 && index < waypointModel.count) {
            waypointModel.setProperty(index, "lat", lat);
            waypointModel.setProperty(index, "lon", lon);
            waypointModel.setProperty(index, "alt", alt);
            updateMissionPath();
        }
    }
    
    function clearWaypoints() {
        waypointModel.clear();
        updateMissionPath();
    }
    
    function updateMissionPath() {
        // Force mission path to update by notifying bindings
        missionPath.path = missionPath.path;
    }
    
    // Update vehicle position when lat/lon changes
    onVehicleLatChanged: {
        vehicleMarker.coordinate.latitude = vehicleLat;
    }
    
    onVehicleLonChanged: {
        vehicleMarker.coordinate.longitude = vehicleLon;
    }
    
    // Set map center to follow vehicle
    function centerOnVehicle() {
        map.center = QtPositioning.coordinate(vehicleLat, vehicleLon);
    }
    
    // Set map center to home position
    function centerOnHome() {
        map.center = homePosition;
    }
    
    // Load mission waypoints from array
    function loadMission(waypoints) {
        clearWaypoints();
        for (var i = 0; i < waypoints.length; i++) {
            var wp = waypoints[i];
            addWaypoint(wp.lat, wp.lon, wp.alt);
        }
    }
    
    // Export mission waypoints to array
    function exportMission() {
        var result = [];
        for (var i = 0; i < waypointModel.count; i++) {
            var item = waypointModel.get(i);
            result.push({
                index: item.index,
                lat: item.lat,
                lon: item.lon,
                alt: item.alt
            });
        }
        return result;
    }
}
