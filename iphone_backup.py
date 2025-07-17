#!/usr/bin/env python3
"""
iPhone Photo Backup Script using pymobiledevice3
Direct photo backup from iPhone without Image Capture
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Check dependencies early
try:
    from pymobiledevice3.lockdown import create_using_usbmux
    from pymobiledevice3.services.afc import AfcService
    from pymobiledevice3.usbmux import select_device
    from pymobiledevice3.exceptions import *
except ImportError:
    print("❌ pymobiledevice3 not installed!")
    print("📦 Install with: pip install pymobiledevice3")
    sys.exit(1)

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    print("❌ Pillow not installed!")
    print("📦 Install with: pip install Pillow")
    sys.exit(1)

# Import the main function from the new modular structure
from iphone_backup.main import main

if __name__ == "__main__":
    main()
