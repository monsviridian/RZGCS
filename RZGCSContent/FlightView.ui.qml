/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick
import QtQuick.Controls
import QtLocation 6.8
 import QtPositioning 6.8
import QtQuick3D 6.8





    Item {
    id: flightview
    width: 1920
    height: 1080

    Rectangle {
        id: maprectangle
        color: "black"
        anchors.fill: parent

        Item {
            x: 0
            y: 0
            width: 1271
            height: 712




            Plugin {
                id: osmFreePlugin
                name: "osm"
                PluginParameter {
                    name: "osm.mapping.custom.host"
                    value: "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
                }
                PluginParameter {
                    name: "osm.mapping.custom.tileSize"
                    value: "256"
                }
                PluginParameter {
                    name: "osm.mapping.custom.minimumLevel"
                    value: "2"
                }
                PluginParameter {
                    name: "osm.mapping.custom.maximumLevel"
                    value: "19"
                }
            }


            Map {
                id: map1
                anchors.fill: parent
                plugin: osmFreePlugin
                center {
                           // The Qt Company in Oslo
                    latitude: 48.1351
                    longitude: 11.5820
                }  // München Beispiel
                zoomLevel: 14
                // Routenanzeige
                        MapRoute {
                            id: routeItem
                            route: routeModel
                            line.color: "blue"
                            line.width: 4
                        }
                        RouteModel {
                                id: routeModel
                                plugin: mapPlugin
                                query: routeQuery
                            }
                        RouteQuery {
                                id: routeQuery
                                waypoints: [

                                ]
                            }

                // Marker für aktuelle GPS-Position
                MapQuickItem {
                    id: gpsMarker
                    anchorPoint.x: 12
                    anchorPoint.y: 12
                    coordinate {
                        // The Qt Company in Oslo
                 latitude: 48.1351
                 longitude: 11.5820
             }  // München Beispie
                    sourceItem: Rectangle {
                        width: 24
                        height: 24
                        color: "red"
                        radius: 12
                        border.width: 2
                        border.color: "white"
                    }
                }
            }

        }




    }

    Rectangle {
        id: mapcommandrect
        y: 708
        height: 186
        color: "black"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: 0
        anchors.rightMargin: 642
        anchors.bottomMargin: 186

        Button {
            id: armbutton
            x: 286
            y: 8
            width: 183
            height: 76
            text: qsTr("Set Position")
        }

        DelayButton {
            id: prearm
            x: 107
            y: 25
            width: 113
            height: 37
            text: qsTr("Prearm")
        }

        Switch {
            id: armswitch
            x: 95
            y: 68
            width: 175
            height: 85
            text: qsTr("Arm")
        }

        Switch {
            id: disarmswitch
            x: 839
            y: 78
            width: 193
            height: 66
            text: qsTr("Disarm")
        }

        Slider {
            id: slider
            x: 570
            y: 63
            value: 0

        }

        TextField {
            id: textField
            x: 595
            y: 25
            width: 162
            height: 32
            placeholderText: qsTr("Send Mission Plan")
        }

        Button {
            id: button
            x: 801
            y: 18
            width: 197
            height: 66
            text: qsTr("Reset")
        }

        ComboBox {
            id: comboBox
            x: 1060
            y: 18
            width: 215
            height: 97

        }

        Control {
            id: control
            x: 948
            y: 41
            width: 76
            height: 86
        }
    }

    Item {
        id: __materialLibrary__
    }



}
