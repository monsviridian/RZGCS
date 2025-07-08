pragma Singleton
import QtQuick 2.15

QtObject {
    // Farben
    readonly property color backgroundColor: "#181c1f"
    readonly property color panelColor: "#232b2e"
    readonly property color borderColor: "#2e3a3e"
    readonly property color accentColor: "#00e0c6"
    readonly property color textColor: "#cccccc"
    readonly property color textSecondaryColor: "#999999"
    readonly property color errorColor: "#ff6666"
    readonly property color warningColor: "#ffb84b"
    readonly property color successColor: "#4caf50"
    readonly property color infoColor: "#2196f3"
    
    // Schriftgrößen
    readonly property int fontSizeSmall: 10
    readonly property int fontSizeDefault: 12
    readonly property int fontSizeMedium: 14
    readonly property int fontSizeLarge: 16
    readonly property int fontSizeTitle: 18
    readonly property int fontSizeHeader: 24
    
    // Abstände
    readonly property int spacingSmall: 4
    readonly property int spacingDefault: 8
    readonly property int spacingMedium: 12
    readonly property int spacingLarge: 16
    readonly property int spacingXLarge: 24
    
    // Ecken-Radien
    readonly property int radiusSmall: 4
    readonly property int radiusDefault: 8
    readonly property int radiusLarge: 12
    
    // Animationen
    readonly property int animationDurationFast: 150
    readonly property int animationDurationDefault: 300
    readonly property int animationDurationSlow: 500
    
    // Margins
    readonly property int marginSmall: 8
    readonly property int marginDefault: 16
    readonly property int marginLarge: 24
    
    // Z-Index Werte
    readonly property int zIndexBase: 0
    readonly property int zIndexPanel: 1
    readonly property int zIndexOverlay: 10
    readonly property int zIndexModal: 100
    readonly property int zIndexToast: 1000
} 