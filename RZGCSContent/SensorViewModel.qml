import QtQuick
import QtCore

ListModel {
    id: sensorModel

    // Function to update sensor data
    function update_sensor(name, value) {
        for (let i = 0; i < count; i++) {
            if (get(i).name === name) {
                setProperty(i, "value", value)
                setProperty(i, "formattedValue", formatValue(name, value))
                return
            }
        }
    }

    // Function to format sensor values
    function formatValue(name, value) {
        switch(name) {
            case "GPS":
                return "Lat: " + value.latitude.toFixed(6) + "\nLon: " + value.longitude.toFixed(6)
            case "IMU":
                return "Roll: " + value.roll.toFixed(2) + "°\nPitch: " + value.pitch.toFixed(2) + "°"
            case "Speed":
                return value.toFixed(1) + " m/s"
            case "Battery":
                return value.toFixed(1) + "V"
            default:
                return value.toString()
        }
    }

    // Initial sensor list
    ListElement {
        name: "IMU"
        value: 0
        formattedValue: "Roll: 0.00°\nPitch: 0.00°"
    }
    ListElement {
        name: "Speed"
        value: 0
        formattedValue: "0.0 m/s"
    }
    ListElement {
        name: "Camera"
        value: "Offline"
        formattedValue: "Offline"
    }
    ListElement {
        name: "GPS"
        value: 0
        formattedValue: "Lat: 0.000000\nLon: 0.000000"
    }
    ListElement {
        name: "VTX"
        value: "Offline"
        formattedValue: "Offline"
    }
    ListElement {
        name: "Analog Output"
        value: 0
        formattedValue: "0"
    }
    ListElement {
        name: "Gimbal"
        value: "Offline"
        formattedValue: "Offline"
    }
    ListElement {
        name: "Servos"
        value: "Offline"
        formattedValue: "Offline"
    }
    ListElement {
        name: "Sonar"
        value: 0
        formattedValue: "0.0 m"
    }
    ListElement {
        name: "LightSensor"
        value: 0
        formattedValue: "0 lux"
    }
    ListElement {
        name: "Kompass"
        value: 0
        formattedValue: "0°"
    }
    ListElement {
        name: "Optical Flow"
        value: "Offline"
        formattedValue: "Offline"
    }
    ListElement {
        name: "Laser"
        value: "Offline"
        formattedValue: "Offline"
    }
}
