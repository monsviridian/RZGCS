#!/usr/bin/env python3
"""
QML Style Fix Utility
Automatically fixes QML style customization issues by applying necessary changes to QML files
"""

import os
import re
import sys
from pathlib import Path


def fix_qml_imports(qml_file_path):
    """Add Material style imports to QML file"""
    if not os.path.exists(qml_file_path):
        print(f"[ERROR] File not found: {qml_file_path}")
        return False
    
    with open(qml_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Material style imports are already present
    if "QtQuick.Controls.Material" in content:
        print(f"[INFO] Material imports already exist in {qml_file_path}")
        return True
    
    # Add Material style imports
    if "import QtQuick.Controls" in content:
        updated_content = content.replace(
            "import QtQuick.Controls",
            "import QtQuick.Controls.Material 2.15\nimport QtQuick.Controls 2.15"
        )
        
        with open(qml_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"[INFO] Added Material imports to {qml_file_path}")
        return True
    
    return False


def fix_qml_button_customization(qml_file_path):
    """Fix button customization in QML file"""
    if not os.path.exists(qml_file_path):
        print(f"[ERROR] File not found: {qml_file_path}")
        return False
    
    with open(qml_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix problematic contentItem customization
    button_pattern = r"(Button\s*{[^}]*?contentItem:\s*Text\s*{[^}]*?}[^}]*?})"
    
    # Extract button customizations
    matches = re.finditer(button_pattern, content, re.DOTALL)
    has_changes = False
    
    for match in matches:
        button_def = match.group(1)
        
        # Check if this button already uses Material components
        if "Material.foreground" in button_def:
            continue
        
        # Replace direct Text customization with Material style properties
        updated_button = button_def.replace(
            "contentItem: Text {",
            "Material.background: \"#2C2C2C\"\n        Material.foreground: \"white\"\n        // Using Material properties instead of direct customization\n        /*contentItem: Text {"
        )
        
        # Close the commented section
        updated_button = updated_button.replace(
            "}", 
            "}", 
            updated_button.count("}") - 1
        ) + "*/"
        
        # Update the content
        content = content.replace(button_def, updated_button)
        has_changes = True
    
    if has_changes:
        with open(qml_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[INFO] Fixed button customization in {qml_file_path}")
        return True
    
    return False


def create_style_config(qml_dir):
    """Create Material style configuration file"""
    config_file = os.path.join(qml_dir, "qtquickcontrols2.conf")
    
    if os.path.exists(config_file):
        print(f"[INFO] Style config already exists: {config_file}")
        return True
    
    config_content = """[Controls]
Style=Material

[Material]
Theme=Dark
Accent=Teal
Primary=BlueGrey
Variant=Dense
"""
    
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"[INFO] Created style config: {config_file}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create style config: {e}")
        return False


def main():
    """Main function"""
    # Set working directory to project root
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(str(project_root))
    print(f"Working directory: {os.getcwd()}")
    
    # Path to QML content directory
    qml_dir = os.path.join(os.getcwd(), "RZGCSContent")
    if not os.path.exists(qml_dir):
        print(f"[ERROR] QML directory not found: {qml_dir}")
        return 1
    
    # Create Material style configuration file
    create_style_config(qml_dir)
    
    # Files to fix (based on error logs)
    qml_files = [
        os.path.join(qml_dir, "App.qml"),
        os.path.join(qml_dir, "Screen01.ui.qml"),
        os.path.join(qml_dir, "PreflightView.ui.qml")
    ]
    
    # Fix QML imports and button customization
    for qml_file in qml_files:
        if os.path.exists(qml_file):
            fix_qml_imports(qml_file)
            fix_qml_button_customization(qml_file)
    
    print("\n[SUCCESS] QML style fixes applied. You can now run the MAVSDK MVVM integration with Material style support.")
    print("To run the application, use: python Python/rzgcs/mvvm/rzgcs_mvvm.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
