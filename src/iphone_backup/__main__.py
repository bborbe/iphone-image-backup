"""Entry point for the iphone-backup application."""

import argparse
import logging
import sys

from pydantic import ValidationError

from iphone_backup.commands.backup import backup_photos
from iphone_backup.commands.info import show_device_info
from iphone_backup.commands.list_devices import list_connected_devices
from iphone_backup.config import Config
from iphone_backup.logging_setup import configure_logging

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="iPhone Photo Backup Tool - Direct backup using pymobiledevice3",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )

    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Configuration file path",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # backup subcommand (default operation)
    backup_parser = subparsers.add_parser("backup", help="Backup photos from iPhone")
    backup_parser.add_argument(
        "-d",
        "--backup-dir",
        help="Backup directory (default: from config file)",
    )

    # info subcommand
    subparsers.add_parser("info", help="Show device information")

    # list-devices subcommand
    subparsers.add_parser("list-devices", help="List connected devices")

    return parser.parse_args()


def cmd_backup(args: argparse.Namespace, config: Config) -> None:
    """Run the backup command."""
    backup_photos(args.backup_dir, config.config_file)


def cmd_info(args: argparse.Namespace, config: Config) -> None:
    """Run the info command."""
    show_device_info(config.config_file)


def cmd_list_devices(args: argparse.Namespace, config: Config) -> None:
    """Run the list-devices command."""
    list_connected_devices(config.config_file)


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Load configuration
    try:
        config = Config(config_file=args.config)
    except ValidationError as e:
        # Configure minimal logging for error reporting
        configure_logging("ERROR")
        logger.error("Configuration error:")
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            logger.error(f"  {field}: {error['msg']}")
        sys.exit(1)

    # Configure logging
    log_file = config.get_logging_file() if args.command == "backup" else None
    configure_logging(args.log_level, log_file)

    # Log configuration
    logger.info(f"Backup directory: {config.get_backup_directory()}")
    logger.info(f"Config file: {config.config_file}")

    # Execute command
    try:
        if args.command == "backup":
            cmd_backup(args, config)
        elif args.command == "info":
            cmd_info(args, config)
        elif args.command == "list-devices":
            cmd_list_devices(args, config)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        sys.exit(1)
    except OSError as e:
        logger.error(f"I/O error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception:
        logger.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
