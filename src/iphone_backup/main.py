"""Main entry point for iPhone backup tool"""

import argparse
import logging
import sys

from .backup import iPhonePhotoBackup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iphone_backup.log'),
        logging.StreamHandler()
    ]
)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='iPhone Photo Backup Tool')
    parser.add_argument('-d', '--backup-dir',
                        help='Backup directory (default: ~/Downloads/iPhone Backup)')
    parser.add_argument('-l', '--list-devices', action='store_true',
                        help='List connected devices')
    parser.add_argument('-i', '--info', action='store_true',
                        help='Show device information')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create backup instance
    backup = iPhonePhotoBackup(args.backup_dir)

    # Handle different commands
    if args.list_devices:
        backup.list_devices()
    elif args.info:
        backup.device_info()
    else:
        # Default: backup photos
        print("🍎 iPhone Photo Backup Tool")
        print("=" * 30)

        success = backup.backup_all_photos()

        if success:
            print("\n🎉 Backup completed successfully!")
        else:
            print("\n💥 Backup failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()