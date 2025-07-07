# HOW TO START RZGCS

This guide explains how to set up and run the RZGCS application from the project root.

## 1. Prerequisites
- Python 3.10 or newer (https://www.python.org/downloads/)
- Windows PowerShell (recommended)

## 2. Setup Steps

### a) Open a terminal and navigate to the RZGCS root directory:
```powershell
cd path\to\RZGCS
```

### b) Navigate to the Python directory and create a virtual environment (only needed once):
```powershell
cd Python
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

### e) Return to the project root:
```powershell
cd ..
```

## 3. Running the Application

With the virtual environment activated, start the main application from the project root:
```powershell
python main.py
```

**Note:** `main.py` in the project root imports and runs the Python backend from `Python/dronekit_main.py`.

## 4. Alternative: Running from Python directory

You can also run the application directly from the Python directory:
```powershell
cd Python
python main.py
```

## 5. Troubleshooting
- If you see errors about missing modules, ensure you are in the virtual environment and have installed all requirements.
- If you get a script execution policy error, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- For QML/UI errors, check that all QML files are present in `RZGCSContent/`.

## 6. Notes
- To exit the virtual environment, simply close the terminal or run `deactivate`.
- If you update dependencies, re-run `pip install -r requirements.txt` from the Python directory.
- The `main.py` script provides better error handling and startup information.

---
For further help, contact the project maintainer or check the documentation in the `docs/` folder. 