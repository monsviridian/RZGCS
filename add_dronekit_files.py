#!/usr/bin/env python3
"""
Add dronekit frontend and backend files to git
"""

import os
import subprocess
from pathlib import Path

def read_qml_list():
    """Read QML files from qml_liste.txt"""
    qml_files = []
    try:
        with open('qml_liste.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('C:'):
                    # Extract relative path from absolute path
                    relative_path = line.split('RZGCS\\')[-1]
                    qml_files.append(relative_path)
    except FileNotFoundError:
        print("qml_liste.txt not found")
        return []
    return qml_files

def get_dronekit_dependencies():
    """Get frontend and backend dependencies from dronekit_main.py"""
    dependencies = []
    
    # Frontend dependencies (ViewModels, Dummy components, etc.)
    frontend_patterns = [
        'Python/dummy_qml_components.py',
        'Python/dummy_license_controller.py', 
        'Python/dronekit_sensor_viewmodel.py',
        'Python/viewmodel/mission_planner_viewmodel.py',
        'Python/dronekit_parameter_viewmodel.py',
        'Python/backend/flight_control/viewmodels/flight_navigation_viewmodel.py',
        'Python/backend/firmware/firmware_viewmodel.py',
        'Python/backend/mavlink_v2_integration.py',
        'Python/backend/protocol_connection_manager.py',
        'Python/backend/parameter_manager.py',
        'Python/backend/calibration_controller.py',
        'Python/mavlink_connector.py'
    ]
    
    # Backend dependencies
    backend_patterns = [
        'Python/backend/',
        'Python/rzgcs_dronekit/',
        'Python/telemetry/',
        'Python/flight_control/',
        'Python/flight_planning/'
    ]
    
    dependencies.extend(frontend_patterns)
    dependencies.extend(backend_patterns)
    
    return dependencies

def add_files_to_git():
    """Add files to git"""
    print("Adding QML files...")
    qml_files = read_qml_list()
    
    for qml_file in qml_files:
        if os.path.exists(qml_file):
            try:
                subprocess.run(['git', 'add', qml_file], check=True)
                print(f"Added: {qml_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error adding {qml_file}: {e}")
        else:
            print(f"File not found: {qml_file}")
    
    print("\nAdding dronekit dependencies...")
    dependencies = get_dronekit_dependencies()
    
    for dep in dependencies:
        if os.path.exists(dep):
            try:
                subprocess.run(['git', 'add', dep], check=True)
                print(f"Added: {dep}")
            except subprocess.CalledProcessError as e:
                print(f"Error adding {dep}: {e}")
        else:
            print(f"File not found: {dep}")
    
    # Add dronekit_main.py itself
    if os.path.exists('Python/dronekit_main.py'):
        try:
            subprocess.run(['git', 'add', 'Python/dronekit_main.py'], check=True)
            print("Added: Python/dronekit_main.py")
        except subprocess.CalledProcessError as e:
            print(f"Error adding dronekit_main.py: {e}")
    
    # Add the QML list file
    if os.path.exists('qml_liste.txt'):
        try:
            subprocess.run(['git', 'add', 'qml_liste.txt'], check=True)
            print("Added: qml_liste.txt")
        except subprocess.CalledProcessError as e:
            print(f"Error adding qml_liste.txt: {e}")

if __name__ == "__main__":
    add_files_to_git()
    print("\nDone! Files have been added to git.") 