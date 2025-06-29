import QtQuick
import QtCore

ListModel {
    id: sensorModel
    
    // Beim Start beim Python-Backend registrieren
    Component.onCompleted: {
        console.log("SensorViewModel: Initializing...")
        
        if (typeof sensorModel !== 'undefined') {
            // Registriere das QML-Modell beim Python-Backend
            if (typeof sensorModel.register_qml_object === 'function') {
                sensorModel.register_qml_object(sensorModel)
                console.log("SensorViewModel: QML-Objekt beim Python-Backend registriert")
            }
            
            // Zusätzlich beim MissionPlannerStyle registrieren
            if (typeof missionPlannerStyle !== 'undefined' && missionPlannerStyle) {
                console.log("SensorViewModel: Registering with MissionPlannerStyle")
                missionPlannerStyle.register_sensor_view_model(sensorModel)
            } else {
                console.log("SensorViewModel: MissionPlannerStyle nicht verfügbar")
                
                // Versuche es später noch einmal
                registerTimer.start()
            }
        } else {
            console.error("SensorViewModel: sensorModel ist nicht definiert!")
        }
    }
    
    // Timer für erneuten Registrierungsversuch
    Timer {
        id: registerTimer
        interval: 500
        repeat: true
        running: false
        property int retryCount: 0
        
        onTriggered: {
            retryCount++
            console.log("SensorViewModel: Versuche erneut zu registrieren, Versuch: " + retryCount)
            
            if (typeof missionPlannerStyle !== 'undefined' && missionPlannerStyle) {
                console.log("SensorViewModel: Registering with MissionPlannerStyle")
                missionPlannerStyle.register_sensor_view_model(sensorModel)
                registerTimer.stop()
            } else if (retryCount > 10) {
                console.error("SensorViewModel: Aufgabe nach 10 Versuchen")
                registerTimer.stop()
            }
        }
    }

    // Function to update sensor data
    function update_sensor(name, value, unit = "") {
        for (let i = 0; i < count; i++) {
            if (get(i).name === name) {
                setProperty(i, "value", value)
                setProperty(i, "unit", unit)
                setProperty(i, "formattedValue", formatValue(name, value, unit))
                return
            }
        }
        
        // Wenn Sensor noch nicht existiert, füge ihn hinzu
        append({
            "name": name,
            "value": value,
            "unit": unit,
            "formattedValue": formatValue(name, value, unit)
        })
    }
    
    // Spezielle Funktion für die Verarbeitung von Telemetriedaten
    // Ähnlich zur MAVSDK-Integration
    function update_from_telemetry(telemetry_type, telemetry_data) {
        console.log("SensorViewModel: update_from_telemetry called with type: " + telemetry_type);
        
        switch(telemetry_type) {
            case "position":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    let gps_data = {"latitude": telemetry_data.latitude, "longitude": telemetry_data.longitude};
                    update_sensor("gps_latitude", gps_data.latitude, "°");
                    update_sensor("gps_longitude", gps_data.longitude, "°");
                    update_sensor("gps_altitude", telemetry_data.relative_alt || telemetry_data.altitude, "m");
                }
                break;
                
            case "attitude":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    let imu_data = {"roll": telemetry_data.roll, "pitch": telemetry_data.pitch, "yaw": telemetry_data.yaw};
                    update_sensor("roll", imu_data.roll, "°");
                    update_sensor("pitch", imu_data.pitch, "°");
                    update_sensor("yaw", imu_data.yaw, "°");
                }
                break;
                
            case "speed":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    update_sensor("groundspeed", telemetry_data.groundspeed, "m/s");
                    update_sensor("airspeed", telemetry_data.airspeed, "m/s");
                    update_sensor("vertical_speed", telemetry_data.vspeed || telemetry_data.climb, "m/s");
                }
                break;
                
            case "battery":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    let bat_data = {
                        "voltage": telemetry_data.battery_voltage || telemetry_data.voltage, 
                        "current": telemetry_data.battery_current || telemetry_data.current, 
                        "remaining": telemetry_data.battery_remaining || telemetry_data.remaining
                    };
                    update_sensor("battery_voltage", bat_data.voltage, "V");
                    update_sensor("battery_current", bat_data.current, "A");
                    update_sensor("battery_percentage", bat_data.remaining, "%");
                }
                break;
                
            case "environment":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    update_sensor("heading", telemetry_data.wind_direction, "°");
                }
                break;
                
            case "status":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    update_sensor("throttle", telemetry_data.mode, "%");
                }
                break;
                
            case "all":
                // Für den Fall, dass alle Telemetriedaten auf einmal gesendet werden
                if (telemetry_data && typeof telemetry_data === 'object') {
                    console.log("Updating all telemetry data");
                    
                    // Position & Altitude
                    let gps_data = {"latitude": telemetry_data.latitude, "longitude": telemetry_data.longitude};
                    update_sensor("gps_latitude", gps_data.latitude, "°");
                    update_sensor("gps_longitude", gps_data.longitude, "°");
                    update_sensor("gps_altitude", telemetry_data.relative_alt || telemetry_data.altitude, "m");
                    
                    // Attitude
                    let imu_data = {"roll": telemetry_data.roll, "pitch": telemetry_data.pitch, "yaw": telemetry_data.yaw};
                    update_sensor("roll", imu_data.roll, "°");
                    update_sensor("pitch", imu_data.pitch, "°");
                    update_sensor("yaw", imu_data.yaw, "°");
                    
                    // Speed
                    update_sensor("groundspeed", telemetry_data.groundspeed, "m/s");
                    update_sensor("airspeed", telemetry_data.airspeed, "m/s");
                    update_sensor("vertical_speed", telemetry_data.vspeed || telemetry_data.climb, "m/s");
                    
                    // Battery
                    let bat_data = {
                        "voltage": telemetry_data.battery_voltage || telemetry_data.voltage, 
                        "current": telemetry_data.battery_current || telemetry_data.current, 
                        "remaining": telemetry_data.battery_remaining || telemetry_data.remaining
                    };
                    update_sensor("battery_voltage", bat_data.voltage, "V");
                    update_sensor("battery_current", bat_data.current, "A");
                    update_sensor("battery_percentage", bat_data.remaining, "%");
                    
                    // Environment
                    if (telemetry_data.wind_direction !== undefined) {
                        update_sensor("heading", telemetry_data.wind_direction, "°");
                    }
                    
                    // Status
                    update_sensor("throttle", telemetry_data.mode, "%");
                }
                break;
                
            default:
                console.log("Unbekannter Telemetrietyp: " + telemetry_type);
        }
    }

    // Function to format sensor values
    function formatValue(name, value, unit) {
        switch(name) {
            case "gps_latitude":
            case "gps_longitude":
                return value.toFixed(6) + "°"
            case "roll":
            case "pitch":
            case "yaw":
            case "heading":
                return value.toFixed(1) + "°"
            case "groundspeed":
                return (value * 3.6).toFixed(1) + " km/h"  // Convert m/s to km/h
            case "airspeed":
            case "vertical_speed":
                return value.toFixed(1) + " m/s"
            case "battery_voltage":
                return value.toFixed(1) + " V"
            case "battery_current":
                return value.toFixed(1) + " A"
            case "battery_percentage":
            case "throttle":
                return value.toFixed(1) + " %"
            case "gps_altitude":
                return value.toFixed(1) + " m"
            case "gps_hdop":
            case "gps_vdop":
                return value.toFixed(1)
            case "gps_satellites":
                return value.toString()
            case "gps_fix_type":
                switch(value) {
                    case 0: return "No Fix"
                    case 1: return "GPS"
                    case 2: return "DGPS"
                    case 3: return "RTK Float"
                    case 4: return "RTK Fixed"
                    default: return "Unknown"
                }
            default:
                if (unit) {
                    if (typeof value === 'number') {
                        return value.toFixed(1) + " " + unit
                    }
                    return value + " " + unit
                }
                return value.toString()
        }
    }

    // Function to find a sensor by name
    function findSensorByName(name) {
        for (let i = 0; i < count; i++) {
            if (get(i).name === name) {
                return get(i)
            }
        }
        return null
    }

    // Initial sensor list with FC relevant sensors
    ListElement {
        name: "roll"
        value: 0
        unit: "°"
        formattedValue: "0.0°"
    }
    ListElement {
        name: "pitch"
        value: 0
        unit: "°"
        formattedValue: "0.0°"
    }
    ListElement {
        name: "yaw"
        value: 0
        unit: "°"
        formattedValue: "0.0°"
    }
    ListElement {
        name: "groundspeed"
        value: 0
        unit: "m/s"
        formattedValue: "0.0 m/s"
    }
    ListElement {
        name: "airspeed"
        value: 0
        unit: "m/s"
        formattedValue: "0.0 m/s"
    }
    ListElement {
        name: "gps_altitude"
        value: 0
        unit: "m"
        formattedValue: "0.0 m"
    }
    ListElement {
        name: "gps_latitude"
        value: 0
        unit: "°"
        formattedValue: "0.000000°"
    }
    ListElement {
        name: "gps_longitude"
        value: 0
        unit: "°"
        formattedValue: "0.000000°"
    }
    ListElement {
        name: "battery_voltage"
        value: 0
        unit: "V"
        formattedValue: "0.0 V"
    }
    ListElement {
        name: "battery_current"
        value: 0
        unit: "A"
        formattedValue: "0.0 A"
    }
    ListElement {
        name: "battery_percentage"
        value: 0
        unit: "%"
        formattedValue: "0.0 %"
    }
    ListElement {
        name: "throttle"
        value: 0
        unit: "%"
        formattedValue: "0.0 %"
    }
    ListElement {
        name: "vertical_speed"
        value: 0
        unit: "m/s"
        formattedValue: "0.0 m/s"
    }
    ListElement {
        name: "heading"
        value: 0
        unit: "°"
        formattedValue: "0.0°"
    }
}
