# iPhone Backup Tool

A Python script to backup photos and videos directly from iPhone using pymobiledevice3.

## Features
- Direct iPhone access without iTunes or Image Capture
- Automatic organization by date (Year/Date folders: `2024/2024-06-15/`, `2025/2025-07-17/`)
- Duplicate handling
- Progress tracking and logging
- HEIC, JPG, PNG, and video support

## Installation

### Using pyenv (Recommended)

```bash
# Create virtual environment
pyenv virtualenv 3.11.4 iphone-image-backup
pyenv local iphone-image-backup

# Install dependencies
pip install -r requirements.txt
```

### Standard Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic backup - saves to ~/Downloads/iPhone Backup/
python iphone_backup.py

# Custom backup directory - specify where to save photos
python iphone_backup.py -d ~/MyBackups

# Show device info - displays iPhone model, iOS version, serial number
python iphone_backup.py --info

# List connected devices - shows all connected iOS devices
python iphone_backup.py --list-devices

# Verbose output - shows detailed logging information
python iphone_backup.py --verbose
```

## Requirements
- Python 3.8+
- Connected iPhone (unlocked and trusted)
- macOS or Linux

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
MIT License - see LICENSE file
