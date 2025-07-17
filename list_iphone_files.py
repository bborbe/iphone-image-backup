#!/usr/bin/env python3
"""
List all files on iPhone
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

# Check dependencies
try:
    from pymobiledevice3.lockdown import create_using_usbmux
    from pymobiledevice3.services.afc import AfcService
    from pymobiledevice3.usbmux import select_device
    from pymobiledevice3.exceptions import *
except ImportError:
    print("❌ pymobiledevice3 not installed!")
    print("📦 Install with: pip install pymobiledevice3")
    sys.exit(1)

logger = logging.getLogger(__name__)


class iPhoneFileLister:
    """Lists files on iPhone device"""
    
    def __init__(self):
        self.device = None
        self.lockdown = None
        self.afc = None
        self.device_info = {}
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'photo_files': 0,
            'other_files': 0,
            'errors': 0
        }
        
        # Common photo/video extensions
        self.photo_extensions = {
            '.jpg', '.jpeg', '.png', '.heic', '.gif', '.tiff', '.bmp',
            '.mov', '.mp4', '.m4v', '.dng', '.raw', '.cr2', '.nef'
        }
    
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
            device_name = self.device_info.get('DeviceName', 'Unknown iPhone')
            ios_version = self.device_info.get('ProductVersion', 'Unknown')

            print(f"✅ Connected to {device_name} (iOS {ios_version})")

            # Start AFC service for file access
            self.afc = AfcService(lockdown=self.lockdown)

            return True

        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """Get detailed file information"""
        info = {
            'name': Path(file_path).name,
            'path': file_path,
            'size': 0,
            'modified': None,
            'is_photo': False,
            'extension': Path(file_path).suffix.lower()
        }
        
        try:
            # Get file stats
            stat_info = self.afc.stat(file_path)
            
            if hasattr(stat_info, 'st_size'):
                info['size'] = stat_info.st_size
            
            if hasattr(stat_info, 'st_mtime'):
                info['modified'] = datetime.fromtimestamp(stat_info.st_mtime)
            elif hasattr(stat_info, 'st_ctime'):
                info['modified'] = datetime.fromtimestamp(stat_info.st_ctime)
            
            # Check if it's a photo
            info['is_photo'] = info['extension'] in self.photo_extensions
            
        except Exception as e:
            logger.debug(f"Could not get stats for {file_path}: {e}")
            self.stats['errors'] += 1
        
        return info
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"
    
    def list_directory(self, directory: str, recursive: bool = True, 
                      show_details: bool = False, photos_only: bool = False) -> list:
        """List files in a directory"""
        files = []
        
        try:
            if not self.afc.exists(directory):
                print(f"❌ Directory does not exist: {directory}")
                return files
            
            print(f"📂 Scanning: {directory}")
            
            if recursive:
                # Walk through all subdirectories
                for root, dirs, filenames in self.afc.walk(directory):
                    self.stats['total_dirs'] += len(dirs)
                    
                    for filename in filenames:
                        file_path = f"{root}/{filename}"
                        file_info = self.get_file_info(file_path)
                        
                        # Filter photos only if requested
                        if photos_only and not file_info['is_photo']:
                            continue
                        
                        files.append(file_info)
                        self.stats['total_files'] += 1
                        
                        if file_info['is_photo']:
                            self.stats['photo_files'] += 1
                        else:
                            self.stats['other_files'] += 1
            else:
                # List only current directory
                try:
                    dir_contents = self.afc.listdir(directory)
                    for item in dir_contents:
                        item_path = f"{directory}/{item}"
                        
                        try:
                            # Check if it's a directory
                            if self.afc.isdir(item_path):
                                self.stats['total_dirs'] += 1
                                continue
                            
                            file_info = self.get_file_info(item_path)
                            
                            # Filter photos only if requested
                            if photos_only and not file_info['is_photo']:
                                continue
                            
                            files.append(file_info)
                            self.stats['total_files'] += 1
                            
                            if file_info['is_photo']:
                                self.stats['photo_files'] += 1
                            else:
                                self.stats['other_files'] += 1
                        
                        except Exception as e:
                            logger.debug(f"Error processing {item_path}: {e}")
                            self.stats['errors'] += 1
                
                except Exception as e:
                    logger.error(f"Could not list directory {directory}: {e}")
                    self.stats['errors'] += 1
            
        except Exception as e:
            logger.error(f"Error accessing directory {directory}: {e}")
            self.stats['errors'] += 1
        
        return files
    
    def print_files(self, files: list, show_details: bool = False):
        """Print file list"""
        if not files:
            print("📭 No files found")
            return
        
        # Sort files by path
        files.sort(key=lambda x: x['path'])
        
        print(f"\n📋 Found {len(files)} files:")
        print("-" * 80)
        
        for file_info in files:
            if show_details:
                # Detailed view
                size_str = self.format_size(file_info['size'])
                modified_str = file_info['modified'].strftime("%Y-%m-%d %H:%M:%S") if file_info['modified'] else "Unknown"
                photo_indicator = "📸" if file_info['is_photo'] else "📄"
                
                print(f"{photo_indicator} {file_info['path']}")
                print(f"   Size: {size_str:>10} | Modified: {modified_str} | Ext: {file_info['extension']}")
                print()
            else:
                # Simple view
                photo_indicator = "📸" if file_info['is_photo'] else "📄"
                print(f"{photo_indicator} {file_info['path']}")
    
    def print_stats(self):
        """Print statistics"""
        print("\n" + "=" * 50)
        print("📊 SCAN SUMMARY")
        print("=" * 50)
        print(f"📁 Total directories: {self.stats['total_dirs']}")
        print(f"📄 Total files: {self.stats['total_files']}")
        print(f"📸 Photo/video files: {self.stats['photo_files']}")
        print(f"📄 Other files: {self.stats['other_files']}")
        if self.stats['errors'] > 0:
            print(f"❌ Errors: {self.stats['errors']}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='List files on iPhone')
    parser.add_argument('-d', '--directory', default='/',
                       help='Directory to scan (default: / for root)')
    parser.add_argument('-r', '--recursive', action='store_true', default=True,
                       help='Scan recursively (default: True)')
    parser.add_argument('--no-recursive', action='store_true',
                       help='Scan only current directory')
    parser.add_argument('--details', action='store_true',
                       help='Show detailed file information')
    parser.add_argument('--photos-only', action='store_true',
                       help='Show only photo/video files')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Handle recursive flag
    recursive = args.recursive and not args.no_recursive
    
    print("📱 iPhone File Lister")
    print("=" * 30)
    
    # Create lister and connect
    lister = iPhoneFileLister()
    
    if not lister.connect():
        sys.exit(1)
    
    # List files
    files = lister.list_directory(
        args.directory, 
        recursive=recursive, 
        show_details=args.details,
        photos_only=args.photos_only
    )
    
    # Print results
    lister.print_files(files, args.details)
    lister.print_stats()


if __name__ == "__main__":
    main()