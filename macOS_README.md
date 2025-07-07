# RZGCS macOS Deployment

This guide explains how to deploy RZGCS (RZ Ground Control Station) on macOS.

## Prerequisites

### System Requirements
- macOS 10.15 (Catalina) or newer
- Python 3.10 or newer
- Git
- At least 2GB free disk space

### Required Software
1. **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/)
2. **Git**: Install via Homebrew or download from [git-scm.com](https://git-scm.com/)

### Optional but Recommended
- **Homebrew**: Package manager for macOS
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/monsviridian/RZGCS.git
cd RZGCS
```

### 2. Run the Deployment Script
```bash
chmod +x deploy_macos.sh
./deploy_macos.sh
```

### 3. Install the Application
```bash
./install_RZGCS_macOS.sh
```

## Manual Setup

If you prefer to set up manually or the automated script fails:

### 1. Set up Python Environment
```bash
cd Python
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

### 2. Test the Application
```bash
python main.py
```

### 3. Create App Bundle (Optional)
```bash
# The deploy_macos.sh script handles this automatically
# Manual creation requires additional setup
```

## Deployment Output

After running `deploy_macos.sh`, you'll get:

### Files Created
- **RZGCS.app**: macOS application bundle
- **RZGCS-macOS.dmg**: Disk image for distribution
- **install_RZGCS_macOS.sh**: Installation script

### App Bundle Structure
```
RZGCS.app/
├── Contents/
│   ├── Info.plist          # App metadata
│   ├── MacOS/
│   │   └── RZGCS          # Launcher script
│   └── Resources/
│       ├── Python/         # Python backend
│       ├── RZGCSContent/   # QML UI files
│       ├── main.py         # Main entry point
│       └── AppIcon.icns    # App icon
```

## Installation Options

### Option 1: System-wide Installation
```bash
./install_RZGCS_macOS.sh
```
This installs RZGCS to `/Applications/` and makes it available system-wide.

### Option 2: User Installation
```bash
cp -R RZGCS.app ~/Applications/
```
This installs RZGCS to your user's Applications folder.

### Option 3: Run from Current Directory
```bash
open RZGCS.app
```
This runs RZGCS from the current directory without installation.

## Troubleshooting

### Common Issues

#### 1. Python Not Found
```bash
# Install Python via Homebrew
brew install python

# Or download from python.org
# https://www.python.org/downloads/
```

#### 2. Permission Denied
```bash
# Make scripts executable
chmod +x deploy_macos.sh
chmod +x install_RZGCS_macOS.sh
```

#### 3. Virtual Environment Issues
```bash
# Remove and recreate virtual environment
cd Python
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

#### 4. PySide6 Installation Issues
```bash
# Install Qt dependencies
brew install qt

# Or try installing with specific flags
pip install PySide6 --no-cache-dir
```

#### 5. App Bundle Won't Launch
```bash
# Check the launcher script permissions
chmod +x RZGCS.app/Contents/MacOS/RZGCS

# Check the Python environment
source Python/venv/bin/activate
python main.py
```

### Debug Mode

To run RZGCS in debug mode:
```bash
cd Python
source venv/bin/activate
python -u main.py
```

### Log Files

Check for error logs in:
- Console.app (Applications > Utilities > Console)
- System logs: `log show --predicate 'process == "RZGCS"'`

## Development

### Running from Source
```bash
# Clone and setup
git clone https://github.com/monsviridian/RZGCS.git
cd RZGCS

# Setup Python environment
cd Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Run the application
python main.py
```

### Modifying the App Bundle
```bash
# Edit the deployment script
nano deploy_macos.sh

# Rebuild the app bundle
./deploy_macos.sh
```

## Distribution

### Creating a DMG
The deployment script automatically creates a DMG file:
```bash
./deploy_macos.sh
# Creates: RZGCS-macOS.dmg
```

### Code Signing (Optional)
For distribution outside your organization:
```bash
# Get an Apple Developer certificate
# Then sign the app bundle
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" RZGCS.app
```

### Notarization (Optional)
For distribution on the Mac App Store:
```bash
# Submit for notarization
xcrun altool --notarize-app --primary-bundle-id "com.rzgcs.app" --username "your-apple-id@example.com" --password "@env:APPLE_ID_PASSWORD" --file RZGCS-macOS.dmg
```

## Security

### Gatekeeper
macOS may block the app due to Gatekeeper. To allow:
1. Right-click on RZGCS.app
2. Select "Open"
3. Click "Open" in the dialog

### App Sandboxing
The current deployment doesn't use app sandboxing. For App Store distribution, additional configuration is required.

## Support

### Getting Help
- Check the main [README.md](README.md) for general information
- Review [HOW_TO_START.md](HOW_TO_START.md) for setup instructions
- Check the [Python/HOW_TO_START.md](Python/HOW_TO_START.md) for backend setup

### Reporting Issues
- Create an issue on GitHub with macOS-specific details
- Include macOS version: `sw_vers`
- Include Python version: `python3 --version`
- Include error messages and logs

## Version History

- **v1.0**: Initial macOS deployment
  - Basic app bundle creation
  - DMG installer generation
  - Python virtual environment setup
  - QML UI integration

---

For more information, see the main project documentation. 