# HOW TO START RZGCS (Python Backend)

This guide explains how to set up and run the RZGCS Python backend, including the QML UI.

## 1. Prerequisites
- Python 3.10 or newer (https://www.python.org/downloads/)
- Windows PowerShell (recommended)

## 2. Setup Steps

### a) Open a terminal and navigate to the Python directory:
```powershell
cd path\to\RZGCS\Python
```

### b) Create a virtual environment (only needed once):
```powershell
python -m venv venv
```

### c) Activate the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```
You should see `(venv)` at the start of your prompt.

### d) Install all dependencies:
```powershell
pip install -r requirements.txt
```

## 3. Running the Application

With the virtual environment activated, start the main application:
```powershell
python main.py
```

**Note:** `main.py` is now the primary startup script that imports and runs `dronekit_main.py`.

## 4. Troubleshooting
- If you see errors about missing modules, ensure you are in the virtual environment and have installed all requirements.
- If you get a script execution policy error, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- For QML/UI errors, check that all QML files are present in `RZGCSContent/`.

## 5. Notes
- To exit the virtual environment, simply close the terminal or run `deactivate`.
- If you update dependencies, re-run `pip install -r requirements.txt`.
- The `main.py` script provides better error handling and startup information.

---
For further help, contact the project maintainer or check the documentation in the `docs/` folder. 