import QtQuick
import QtQuick3D

Node {
    id: node

    // Resources
    PrincipledMaterial {
        id: material_material
        objectName: "Material"
        baseColor: "#ffcccccc"
        roughness: 0.5
        cullMode: PrincipledMaterial.NoCulling
        alphaMode: PrincipledMaterial.Opaque
    }
    PrincipledMaterial {
        id: default_MTL_material
        objectName: "DEFAULT_MTL"
        baseColor: "#ffcccccc"
        roughness: 1
        cullMode: PrincipledMaterial.NoCulling
        alphaMode: PrincipledMaterial.Opaque
    }

    // Nodes:
    Node {
        id: root
        objectName: "ROOT"
        Model {
            id: cube
            objectName: "Cube"
            source: "meshes/cube_mesh.mesh"
            materials: [
                material_material
            ]
        }
        Model {
            id: mk4_v2_10
            objectName: "mk4_v2_10"
            rotation: Qt.quaternion(0.99984, -0.017862, 0, 0)
            scale: Qt.vector3d(1, 1, 1)
            source: "meshes/mk4_v2_10_mesh.mesh"
            materials: [
                default_MTL_material
            ]
        }
    }

    // Animations:
}
