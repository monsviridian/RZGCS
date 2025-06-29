function updateSensorData() {
    if (!sensorModel) return
    
    try {
        var rollValue = 0
        var pitchValue = 0
        var yawValue = 0
        
        // Search for needed values in the sensor model
        var roll = sensorModel.findSensorByName("roll")
        var pitch = sensorModel.findSensorByName("pitch")
        var yaw = sensorModel.findSensorByName("yaw")
        
        if (roll) rollValue = roll.value
        if (pitch) pitchValue = pitch.value
        if (yaw) yawValue = yaw.value
        
        // Keep connection status updated
        if (serialConnector) {
            connectionStatus.text = serialConnector.connected ? "Connected" : "Disconnected"
            connectionStatus.color = serialConnector.connected ? "#00ff00" : "#ff0000"
        }
    } catch (e) {
        // Fehler ignorieren
    }
} 