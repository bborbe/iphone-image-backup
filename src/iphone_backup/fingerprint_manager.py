#!/usr/bin/env python3
"""
Fingerprint management tool - now uses file-based fingerprinting
"""

import argparse
from pathlib import Path

from .fingerprint import FingerprintManager


def list_fingerprints(backup_dir: str | None = None) -> None:
    """List all fingerprints in the backup directory"""
    if not backup_dir:
        backup_dir = str(Path.home() / "Downloads" / "iPhoneImageBackup")

    backup_path = Path(backup_dir)

    if not backup_path.exists():
        print(f"❌ Backup directory does not exist: {backup_path}")
        return

    manager = FingerprintManager(backup_path)
    manager._build_fingerprint_cache()

    if not manager._fingerprint_cache:
        print("📭 No fingerprints found in backup directory")
        return

    print(f"📋 Found {len(manager._fingerprint_cache)} fingerprints:")
    print("-" * 80)

    for content_hash, fp in manager._fingerprint_cache.items():
        size_str = f"{fp.size:,} bytes"
        modified_str = (
            fp.modified_time.strftime("%Y-%m-%d %H:%M:%S") if fp.modified_time else "Unknown"
        )
        print(f"📸 {fp.file_path}")
        print(f"   Hash: {content_hash[:16]}...")
        print(f"   Size: {size_str}")
        print(f"   Modified: {modified_str}")
        print()


def show_stats(backup_dir: str | None = None) -> None:
    """Show backup directory statistics"""
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
    print(f"📸 Total files: {stats['total_files']:,}")
    print(f"💾 Total size: {stats['total_size']:,} bytes")
    print(f"📁 Directory: {stats['backup_directory']}")


def clear_cache(backup_dir: str | None = None) -> None:
    """Clear the fingerprint cache (just for testing)"""
    if not backup_dir:
        backup_dir = str(Path.home() / "Downloads" / "iPhoneImageBackup")

    backup_path = Path(backup_dir)

    if not backup_path.exists():
        print(f"❌ Backup directory does not exist: {backup_path}")
        return

    manager = FingerprintManager(backup_path)
    manager.clear_cache()

    print("✅ Fingerprint cache cleared")


def main() -> None:
    """Main function"""
    parser = argparse.ArgumentParser(description="Fingerprint management (file-based)")
    parser.add_argument("--backup-dir", help="Backup directory path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List all fingerprints")

    # Stats command
    subparsers.add_parser("stats", help="Show backup directory statistics")

    # Clear command
    subparsers.add_parser("clear-cache", help="Clear fingerprint cache")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    print("🔍 Fingerprint Manager (File-Based)")
    print("=" * 40)

    if args.command == "list":
        list_fingerprints(args.backup_dir)
    elif args.command == "stats":
        show_stats(args.backup_dir)
    elif args.command == "clear-cache":
        clear_cache(args.backup_dir)


if __name__ == "__main__":
    main()
