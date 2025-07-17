# iPhone Backup Tool

A Python script to backup photos and videos directly from iPhone using pymobiledevice3.

## Features
- Direct iPhone access without iTunes or Image Capture
- Automatic organization by date (Year/Month folders)
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
# Basic backup
python iphone_backup.py

# Custom backup directory
python iphone_backup.py -d ~/MyBackups

# Show device info
python iphone_backup.py --info
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
