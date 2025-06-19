#!/usr/bin/env python3
"""
Simple MAVSDK Runner
This script runs the existing MAVSDK integration with Material style for QML
"""

import os
import sys
import importlib
from pathlib import Path

# Set style before importing PySide6
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# Import PySide6
import PySide6
from PySide6.QtQuickControls2 import QQuickStyle

# Project path
project_root = str(Path(__file__).resolve().parent.parent)
print(f"Project root: {project_root}")

# Set working directory to project root
os.chdir(project_root)
print(f"Working directory: {os.getcwd()}")

# Set Material style explicitly
QQuickStyle.setStyle("Material")

# Create Material style configuration file if it doesn't exist
config_file = os.path.join(project_root, "RZGCSContent", "qtquickcontrols2.conf")
if not os.path.exists(config_file):
    config_content = """[Controls]
Style=Material

[Material]
Theme=Dark
Accent=Teal
Primary=BlueGrey
Variant=Dense
"""
    with open(config_file, "w") as f:
        f.write(config_content)

# Update App.qml imports if necessary
qml_file = os.path.join(project_root, "RZGCSContent", "App.qml")
if os.path.exists(qml_file):
    with open(qml_file, "r") as f:
        content = f.read()
    
    # Add Material style imports if not present
    if "QtQuick.Controls.Material" not in content:
        content = content.replace(
            "import QtQuick.Controls",
            "import QtQuick.Controls.Material 2.15\nimport QtQuick.Controls 2.15"
        )
        with open(qml_file, "w") as f:
            f.write(content)

# Import the main module
sys.path.insert(0, os.path.join(project_root, "Python"))
import mavsdk_rzgcs_main

# Run the main function
if __name__ == "__main__":
    print("Starting RZGCS with Material style for QML...")
    sys.exit(mavsdk_rzgcs_main.main())
