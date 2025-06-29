import QtQuick 2.15

QtObject {
    id: dummyLicenseController
    
    // Dummy Lizenzeigenschaften
    property bool isLicensed: true
    property string licenseType: "Professional"
    property string licenseExpiry: "31.12.2025"
    property string licenseKey: "DUMMY-KEY-1234-5678"
    
    // Dummy Methoden
    function activateLicense(key) {
        console.log("Dummy: Lizenz mit Key aktiviert:", key)
        return true
    }
    
    function deactivateLicense() {
        console.log("Dummy: Lizenz deaktiviert")
        return true
    }
    
    function checkLicense() {
        console.log("Dummy: Lizenzprüfung durchgeführt")
        return true
    }
}
