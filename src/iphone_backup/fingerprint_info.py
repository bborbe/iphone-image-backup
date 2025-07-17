#!/usr/bin/env python3
"""
Fingerprint information tool - shows stats about backup directory
"""

import argparse
import sys
from pathlib import Path

from .fingerprint import FingerprintManager


def show_stats(backup_dir: str = None):
    """Show fingerprint statistics for backup directory"""
    if not backup_dir:
        backup_dir = str(Path.home() / "Downloads" / "iPhoneImageBackup")
    
    backup_path = Path(backup_dir)
    
    if not backup_path.exists():
        print(f"❌ Backup directory does not exist: {backup_path}")
        return
    
    manager = FingerprintManager(backup_path)
    stats = manager.get_stats()
    
    print("📊 Backup Directory Statistics")
    print("=" * 40)
    print(f"📁 Directory: {stats['backup_directory']}")
    print(f"📸 Total files: {stats['total_files']:,}")
    print(f"💾 Total size: {stats['total_size']:,} bytes")
    
    if stats['total_size'] > 0:
        # Convert to human readable
        size_bytes = stats['total_size']
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                print(f"💾 Total size: {size_bytes:.1f} {unit}")
                break
            size_bytes /= 1024.0
        else:
            print(f"💾 Total size: {size_bytes:.1f} TB")


def check_duplicate(backup_dir: str = None, test_file: str = None):
    """Check if a file would be a duplicate"""
    if not backup_dir:
        backup_dir = str(Path.home() / "Downloads" / "iPhoneImageBackup")
    
    if not test_file:
        print("❌ Test file path required")
        return
    
    backup_path = Path(backup_dir)
    test_path = Path(test_file)
    
    if not backup_path.exists():
        print(f"❌ Backup directory does not exist: {backup_path}")
        return
    
    if not test_path.exists():
        print(f"❌ Test file does not exist: {test_path}")
        return
    
    # Read test file
    with open(test_path, 'rb') as f:
        file_data = f.read()
    
    manager = FingerprintManager(backup_path)
    duplicate_info = manager.get_duplicate_info(file_data)
    
    print(f"🔍 Checking: {test_path}")
    print("-" * 40)
    
    if duplicate_info['is_duplicate']:
        print("✅ This file is a duplicate!")
        print(f"📁 Already backed up as: {duplicate_info['backup_path']}")
        print(f"💾 Size: {duplicate_info['size']:,} bytes")
        if duplicate_info.get('modified_time'):
            print(f"📅 Modified: {duplicate_info['modified_time']}")
    else:
        print("❌ This file is NOT a duplicate")
        print("📥 Would be backed up as new file")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Fingerprint information tool')
    parser.add_argument('--backup-dir', help='Backup directory to analyze')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show backup directory statistics')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if file would be duplicate')
    check_parser.add_argument('file', help='File to check')
    
    args = parser.parse_args()
    
    if not args.command:
        # Default to stats if no command given
        args.command = 'stats'
    
    print("🔍 Fingerprint Information Tool")
    print("=" * 35)
    
    if args.command == 'stats':
        show_stats(args.backup_dir)
    elif args.command == 'check':
        check_duplicate(args.backup_dir, args.file)


if __name__ == "__main__":
    main()