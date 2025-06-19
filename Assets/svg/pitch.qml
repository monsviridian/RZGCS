// Generated from SVG file C:\Users\fuckheinerkleinehack\Documents\RZGS2\RZGCS\Assets\svg\pitch.svg
import QtQuick
import QtQuick.Shapes

Item {
    implicitWidth: 48
    implicitHeight: 48
    transform: [
        Scale { xScale: width / 48; yScale: height / 48 }
    ]
    Shape {
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            strokeColor: "#ff50c6ff"
            strokeWidth: 3
            capStyle: ShapePath.FlatCap
            joinStyle: ShapePath.MiterJoin
            miterLimit: 4
            fillColor: "#00000000"
            fillRule: ShapePath.WindingFill
            PathSvg { path: "M 42 24 C 42 29.5228 33.9411 34 24 34 C 14.0589 34 6 29.5228 6 24 C 6 18.4772 14.0589 14 24 14 C 33.9411 14 42 18.4772 42 24 " }
        }
        ShapePath {
            strokeColor: "transparent"
            fillColor: "#ff50c6ff"
            fillRule: ShapePath.WindingFill
            PathSvg { path: "M 22 8 L 26 8 L 26 40 L 22 40 L 22 8 " }
        }
        ShapePath {
            strokeColor: "transparent"
            fillColor: "#ff50c6ff"
            fillRule: ShapePath.WindingFill
            PathSvg { path: "M 24 8 L 30 16 L 18 16 L 24 8 M 24 40 L 30 32 L 18 32 L 24 40 " }
        }
    }
}
