import sys
from cx_Freeze import setup, Executable

# Abhängigkeiten
build_exe_options = {
    "packages": [
        "PySide6", "pymavlink", "serial", "asyncio", "logging", 
        "math", "time", "threading", "os", "sys"
    ],
    "excludes": ["tkinter", "unittest"],
    "include_files": [
        ("RZGCSContent", "RZGCSContent"),
        ("Assets", "Assets"),
        "README.md",
        "requirements.txt"
    ],
    "include_msvcr": True,
    "build_exe": "build/RZGCS"
}

# Basis für die EXE-Datei
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Für GUI-Anwendungen unter Windows

# Icon-Datei (falls vorhanden)
icon = None
if sys.platform == "win32":
    icon = "Assets/icon.ico"
elif sys.platform == "darwin":
    icon = "Assets/icon.icns"

setup(
    name="RZ Ground Control Station",
    version="1.0.0",
    description="RZ Drone Ground Control Station",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "Python/main.py",
            base=base,
            target_name="RZGCS",
            icon=icon,
            shortcut_name="RZ Ground Control Station",
            shortcut_dir="DesktopFolder",
        )
    ]
)
