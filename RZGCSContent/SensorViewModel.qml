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
                    update_sensor("GPS", gps_data, "");
                    update_sensor("Altitude", telemetry_data.relative_alt || telemetry_data.altitude, "m");
                }
                break;
                
            case "attitude":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    let imu_data = {"roll": telemetry_data.roll, "pitch": telemetry_data.pitch, "yaw": telemetry_data.yaw};
                    update_sensor("IMU", imu_data, "");
                }
                break;
                
            case "speed":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    update_sensor("Groundspeed", telemetry_data.groundspeed, "m/s");
                    update_sensor("Airspeed", telemetry_data.airspeed, "m/s");
                    update_sensor("Vertical Speed", telemetry_data.vspeed || telemetry_data.climb, "m/s");
                }
                break;
                
            case "battery":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    let bat_data = {
                        "voltage": telemetry_data.battery_voltage || telemetry_data.voltage, 
                        "current": telemetry_data.battery_current || telemetry_data.current, 
                        "remaining": telemetry_data.battery_remaining || telemetry_data.remaining
                    };
                    update_sensor("Battery", bat_data, "");
                }
                break;
                
            case "environment":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    update_sensor("Wind Speed", telemetry_data.wind_speed, "m/s");
                    update_sensor("Wind Direction", telemetry_data.wind_direction, "°");
                    update_sensor("Turbulence", (telemetry_data.turbulence * 100), "%");
                    update_sensor("Temperature", telemetry_data.temperature, "°C");
                }
                break;
                
            case "status":
                if (telemetry_data && typeof telemetry_data === 'object') {
                    update_sensor("Mode", telemetry_data.mode, "");
                    update_sensor("Armed", telemetry_data.armed ? "Yes" : "No", "");
                }
                break;
                
            case "all":
                // Für den Fall, dass alle Telemetriedaten auf einmal gesendet werden
                if (telemetry_data && typeof telemetry_data === 'object') {
                    console.log("Updating all telemetry data");
                    
                    // Position & Altitude
                    let gps_data = {"latitude": telemetry_data.latitude, "longitude": telemetry_data.longitude};
                    update_sensor("GPS", gps_data, "");
                    update_sensor("Altitude", telemetry_data.relative_alt || telemetry_data.altitude, "m");
                    
                    // Attitude
                    let imu_data = {"roll": telemetry_data.roll, "pitch": telemetry_data.pitch, "yaw": telemetry_data.yaw};
                    update_sensor("IMU", imu_data, "");
                    
                    // Speed
                    update_sensor("Groundspeed", telemetry_data.groundspeed, "m/s");
                    update_sensor("Airspeed", telemetry_data.airspeed, "m/s");
                    update_sensor("Vertical Speed", telemetry_data.vspeed || telemetry_data.climb, "m/s");
                    
                    // Battery
                    let bat_data = {
                        "voltage": telemetry_data.battery_voltage || telemetry_data.voltage, 
                        "current": telemetry_data.battery_current || telemetry_data.current, 
                        "remaining": telemetry_data.battery_remaining || telemetry_data.remaining
                    };
                    update_sensor("Battery", bat_data, "");
                    
                    // Environment
                    if (telemetry_data.wind_speed !== undefined) {
                        update_sensor("Wind Speed", telemetry_data.wind_speed, "m/s");
                        update_sensor("Wind Direction", telemetry_data.wind_direction, "°");
                        update_sensor("Turbulence", (telemetry_data.turbulence * 100), "%");
                        update_sensor("Temperature", telemetry_data.temperature, "°C");
                    }
                    
                    // Status
                    update_sensor("Mode", telemetry_data.mode, "");
                    update_sensor("Armed", telemetry_data.armed ? "Yes" : "No", "");
                }
                break;
                
            default:
                console.log("Unbekannter Telemetrietyp: " + telemetry_type);
        }
    }

    // Function to format sensor values
    function formatValue(name, value, unit) {
        switch(name) {
            case "GPS":
                return "Lat: " + value.latitude.toFixed(6) + "\nLon: " + value.longitude.toFixed(6)
            case "IMU":
                return "Roll: " + value.roll.toFixed(2) + "°\nPitch: " + value.pitch.toFixed(2) + "°"
            case "Speed":
                return value.toFixed(1) + " m/s"
            case "Groundspeed":
                return value.toFixed(1) + " m/s"
            case "Airspeed":
                return value.toFixed(1) + " m/s"
            case "Battery":
                if (typeof value === 'object') {
                    return value.voltage.toFixed(1) + "V, " + value.remaining + "%"
                }
                return value.toFixed(1) + "V"
            case "Höhe":
            case "Altitude":
                return value.toFixed(1) + " m"
            case "CPU Last":
                return value.toFixed(1) + "%"
            case "Firmware":
            case "Frame":
            case "Version":
                return value
            case "RC Inputs":
                let channels = []
                for (let ch in value) {
                    channels.push(ch + ": " + value[ch])
                }
                return channels.join("\n")
            case "Servos":
                let servos = []
                for (let s in value) {
                    servos.push(s + ": " + value[s])
                }
                return servos.join("\n")
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

    // Initial sensor list with FC relevant sensors
    ListElement {
        name: "IMU"
        value: 0
        unit: ""
        formattedValue: "Roll: 0.00°\nPitch: 0.00°"
    }
    ListElement {
        name: "Groundspeed"
        value: 0
        unit: "m/s"
        formattedValue: "0.0 m/s"
    }
    ListElement {
        name: "Airspeed"
        value: 0
        unit: "m/s"
        formattedValue: "0.0 m/s"
    }
    ListElement {
        name: "Altitude"
        value: 0
        unit: "m"
        formattedValue: "0.0 m"
    }
    ListElement {
        name: "GPS"
        value: 0
        unit: ""
        formattedValue: "Lat: 0.000000\nLon: 0.000000"
    }
    ListElement {
        name: "Battery"
        value: 0
        unit: "V"
        formattedValue: "0.0 V, 0%"
    }
    ListElement {
        name: "CPU Last"
        value: 0
        unit: "%"
        formattedValue: "0.0 %"
    }
    ListElement {
        name: "Firmware"
        value: "Unbekannt"
        unit: ""
        formattedValue: "Unbekannt"
    }
    ListElement {
        name: "Frame"
        value: "Unbekannt"
        unit: ""
        formattedValue: "Unbekannt"
    }
    ListElement {
        name: "RC Inputs"
        value: {}
        unit: ""
        formattedValue: "Keine Daten"
    }
    ListElement {
        name: "Servos"
        value: {}
        unit: ""
        formattedValue: "Keine Daten"
    }
    ListElement {
        name: "System Servos"
        value: "S1=0, S2=0, S3=0, S4=0"
        unit: ""
        formattedValue: "S1=0, S2=0, S3=0, S4=0"
    }
    ListElement {
        name: "System RC"
        value: "RC1=0, RC2=0, RC3=0, RC4=0"
        unit: ""
        formattedValue: "RC1=0, RC2=0, RC3=0, RC4=0"
    }
    ListElement {
        name: "System Mission"
        value: "WP#0"
        unit: ""
        formattedValue: "WP#0"
    }
    ListElement {
        name: "System CPU"
        value: "0.0%"
        unit: ""
        formattedValue: "0.0%"
    }
    ListElement {
        name: "Battery %"
        value: "0%"
        unit: ""
        formattedValue: "0%"
    }
}
