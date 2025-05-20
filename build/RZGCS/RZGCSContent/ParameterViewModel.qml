import QtQuick

ListModel {
    // Signal für das erfolgreiche Laden von Parametern
    signal parametersLoaded()
    
    // Beispielparameter basierend auf dem Screenshot
    // Flightcontroller-relevante Parameter
    ListElement {
        name: "OSD"
        option: "RCTR_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "PILOT"
        option: "RCT1_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "PIX"
        option: "RCT2_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "PSC"
        option: "RCT3_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "RALLY"
        option: "RCT4_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "RC"
        option: "RCT6_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "RWEND"
        option: "RC1_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "RINGENDA"
        option: "RC2_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "RPM"
        option: "RC3_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "RSSI"
        option: "RC4_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "RTL"
        option: "RC5_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "SERIAL"
        option: "RC6_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "SERVO"
        option: "RC8_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    ListElement {
        name: "SID"
        option: "RC9_OPTION"
        value: "Do Nothing"
        description: "RC input option"
    }
    
    // Funktion zum Hinzufügen eines Parameters
    function add_parameter(name, option, value, description) {
        append({
            "name": name,
            "option": option,
            "value": value,
            "description": description
        });
    }
    
    // Funktion zum Aktualisieren eines Parameters
    function update_parameter(index, name, option, value, description) {
        if (index >= 0 && index < count) {
            setProperty(index, "name", name);
            setProperty(index, "option", option);
            setProperty(index, "value", value);
            setProperty(index, "description", description);
        }
    }
    
    // Funktion zum Löschen aller Parameter
    function clear_parameters() {
        clear();
    }
    
    // Funktion zum Abrufen aller Parameter
    function get_parameters() {
        var parameters = [];
        for (var i = 0; i < count; i++) {
            parameters.push(get(i));
        }
        return parameters;
    }
    
    function rowCount() {
        return count;
    }
}
