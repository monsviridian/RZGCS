import QtQuick 2.15

QtObject {
    id: licenseManager
    
    // Fake license properties
    property bool isLicensed: true
    property string licenseType: "Development"
    property string licenseHolder: "Developer"
    property date expiryDate: new Date(2030, 0, 1)
    
    // Fake license methods
    function checkLicense() {
        return true;
    }
    
    function getLicenseInfo() {
        return {
            "licenseType": licenseType,
            "licenseHolder": licenseHolder,
            "expiryDate": expiryDate
        };
    }
}
