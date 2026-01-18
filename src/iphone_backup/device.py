"""iPhone device connection and communication"""

import logging
from typing import Any

from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.afc import AfcService
from pymobiledevice3.usbmux import select_device

logger = logging.getLogger(__name__)


class iPhoneDevice:
    """Handles iPhone device connection and file operations"""

    def __init__(self) -> None:
        self.device: Any = None
        self.lockdown: Any = None
        self.afc: Any = None
        self.device_info: dict[str, Any] = {}

    def connect(self) -> bool:
        """Connect to iPhone device"""
        try:
            print("🔍 Looking for connected iPhone...")
            self.device = select_device()

            if not self.device:
                print("❌ No iPhone found. Make sure it's connected and unlocked.")
                return False

            print(f"📱 Found device: {self.device}")

            # Create lockdown connection
            self.lockdown = create_using_usbmux(serial=self.device.serial)

            # Get device info
            self.device_info = self.lockdown.all_values
            device_name = self.device_info.get("DeviceName", "Unknown iPhone")
            ios_version = self.device_info.get("ProductVersion", "Unknown")

            print(f"✅ Connected to {device_name} (iOS {ios_version})")

            # Start AFC service for file access
            self.afc = AfcService(lockdown=self.lockdown)

            return True

        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            print(f"❌ Connection failed: {e}")
            return False

    def get_file_contents(self, file_path: str) -> bytes:
        """Get file contents from iPhone"""
        if not self.afc:
            raise RuntimeError("Device not connected")
        result: bytes = self.afc.get_file_contents(file_path)
        return result

    def stat(self, file_path: str) -> Any:
        """Get file stats from iPhone"""
        if not self.afc:
            raise RuntimeError("Device not connected")
        return self.afc.stat(file_path)

    def exists(self, file_path: str) -> bool:
        """Check if file exists on iPhone"""
        if not self.afc:
            raise RuntimeError("Device not connected")
        result: bool = self.afc.exists(file_path)
        return result

    def walk(self, directory: str) -> Any:
        """Walk directory tree on iPhone"""
        if not self.afc:
            raise RuntimeError("Device not connected")
        return self.afc.walk(directory)

    def list_devices(self) -> None:
        """List all connected devices"""
        try:
            from pymobiledevice3.usbmux import list_devices

            devices = list_devices()

            if not devices:
                print("📱 No devices found")
                return

            print("📱 Connected devices:")
            for device in devices:
                print(f"   - {device}")

        except Exception as e:
            print(f"❌ Error listing devices: {e}")

    def get_device_info(self) -> dict[str, Any]:
        """Get device information"""
        if not self.device_info:
            raise RuntimeError("Device not connected")
        return self.device_info

    def print_device_info(self) -> None:
        """Print device information"""
        if not self.device_info:
            print("❌ Device not connected")
            return

        print("📱 Device Information:")
        print("-" * 30)
        print(f"Name: {self.device_info.get('DeviceName', 'Unknown')}")
        print(f"Model: {self.device_info.get('ProductType', 'Unknown')}")
        print(f"iOS Version: {self.device_info.get('ProductVersion', 'Unknown')}")
        print(f"Serial: {self.device_info.get('SerialNumber', 'Unknown')}")
        print(f"UDID: {self.device_info.get('UniqueDeviceID', 'Unknown')}")
