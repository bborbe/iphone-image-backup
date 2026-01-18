"""Configuration management for iPhone backup tool"""

import logging
from pathlib import Path
from typing import Any

import yaml


class BackupConfig:
    """Handles configuration loading and management"""

    def __init__(self, config_file: str | None = None):
        self.config_file = config_file or "config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = Path(self.config_file)

        if not config_path.exists():
            # Return default configuration if file doesn't exist
            return self._get_default_config()

        try:
            with open(config_path) as f:
                config: dict[str, Any] = yaml.safe_load(f)
            return config
        except Exception as e:
            logging.warning(f"Could not load config file {config_path}: {e}")
            logging.info("Using default configuration")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration"""
        return {
            "backup": {
                "default_directory": "~/Downloads/iPhoneImageBackup",
                "create_subdirs": True,
                "date_format": "%Y/%Y-%m-%d",
            },
            "files": {
                "photo_extensions": [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".heic",
                    ".gif",
                    ".tiff",
                    ".bmp",
                    ".dng",
                    ".raw",
                    ".cr2",
                    ".nef",
                ],
                "video_extensions": [".mov", ".mp4", ".m4v", ".avi", ".mkv"],
                "exclude_files": [],
                "exclude_patterns": [
                    "*/Thumbnails/*",
                    "*/Cache/*",
                    "*/Metadata/*",
                    "*.tmp",
                    "*.cache",
                ],
            },
            "logging": {"level": "INFO", "file": "iphone_backup.log"},
            "device": {"auto_connect": True, "trust_prompt": True},
        }

    def get_photo_extensions(self) -> list[str]:
        """Get list of photo file extensions"""
        result: list[str] = self.config.get("files", {}).get("photo_extensions", [])
        return result

    def get_video_extensions(self) -> list[str]:
        """Get list of video file extensions"""
        result: list[str] = self.config.get("files", {}).get("video_extensions", [])
        return result

    def get_all_extensions(self) -> list[str]:
        """Get all supported file extensions"""
        photo_exts = self.get_photo_extensions()
        video_exts = self.get_video_extensions()
        return photo_exts + video_exts

    def get_exclude_files(self) -> list[str]:
        """Get list of files to exclude from backup"""
        result: list[str] = self.config.get("files", {}).get("exclude_files", [])
        return result

    def get_exclude_patterns(self) -> list[str]:
        """Get list of patterns to exclude from backup"""
        result: list[str] = self.config.get("files", {}).get("exclude_patterns", [])
        return result

    def get_backup_directory(self) -> str:
        """Get default backup directory"""
        result: str = self.config.get("backup", {}).get(
            "default_directory", "~/Downloads/iPhoneImageBackup"
        )
        return result

    def get_date_format(self) -> str:
        """Get date format for organizing files"""
        result: str = self.config.get("backup", {}).get("date_format", "%Y/%Y-%m-%d")
        return result

    def get_logging_level(self) -> str:
        """Get logging level"""
        result: str = self.config.get("logging", {}).get("level", "INFO")
        return result

    def get_logging_file(self) -> str:
        """Get logging file path"""
        result: str = self.config.get("logging", {}).get("file", "iphone_backup.log")
        return result

    def should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from backup"""
        import fnmatch

        # Check exact file matches
        exclude_files = self.get_exclude_files()
        if file_path in exclude_files:
            return True

        # Check pattern matches
        exclude_patterns = self.get_exclude_patterns()
        return any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns)

    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value by dot-separated key path"""
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value
