"""Application configuration using Pydantic BaseSettings."""

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """iPhone backup configuration loaded from YAML config file and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Backup configuration
    backup_directory: str = Field(
        default="~/Downloads/iPhoneImageBackup",
        description="Directory where backups will be stored",
    )
    date_format: str = Field(
        default="%Y/%Y-%m-%d",
        description="Date format for organizing files (Year/Date)",
    )

    # Logging configuration
    log_file: str = Field(
        default="iphone_backup.log",
        description="Log file path",
    )

    # Configuration file path (not from env)
    config_file: str = Field(
        default="config.yaml",
        description="YAML configuration file path",
    )

    # Cached YAML config
    _yaml_config: dict[str, Any] = {}

    @field_validator("backup_directory")
    @classmethod
    def expand_path(cls, v: str) -> str:
        """Expand user home directory in path."""
        return str(Path(v).expanduser())

    def model_post_init(self, __context: Any) -> None:
        """Load YAML config after model initialization."""
        self._yaml_config = self._load_yaml_config()

    def _load_yaml_config(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        config_path = Path(self.config_file)

        if not config_path.exists():
            return self._get_default_yaml_config()

        try:
            with open(config_path) as f:
                config: dict[str, Any] = yaml.safe_load(f)
            return config
        except Exception as e:
            logging.warning(f"Failed to load YAML config from {config_path}: {e}")
            return self._get_default_yaml_config()

    def _get_default_yaml_config(self) -> dict[str, Any]:
        """Get default YAML configuration."""
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
            "logging": {
                "level": "INFO",
                "file": "iphone_backup.log",
            },
            "device": {
                "auto_connect": True,
                "trust_prompt": True,
            },
        }

    def get_photo_extensions(self) -> list[str]:
        """Get list of photo file extensions."""
        result: list[str] = self._yaml_config.get("files", {}).get("photo_extensions", [])
        return result

    def get_video_extensions(self) -> list[str]:
        """Get list of video file extensions."""
        result: list[str] = self._yaml_config.get("files", {}).get("video_extensions", [])
        return result

    def get_all_extensions(self) -> list[str]:
        """Get all supported file extensions."""
        return self.get_photo_extensions() + self.get_video_extensions()

    def get_exclude_files(self) -> list[str]:
        """Get list of files to exclude from backup."""
        result: list[str] = self._yaml_config.get("files", {}).get("exclude_files", [])
        return result

    def get_exclude_patterns(self) -> list[str]:
        """Get list of patterns to exclude from backup."""
        result: list[str] = self._yaml_config.get("files", {}).get("exclude_patterns", [])
        return result

    def get_backup_directory(self) -> str:
        """Get backup directory."""
        yaml_dir = self._yaml_config.get("backup", {}).get("default_directory")
        if yaml_dir:
            return str(Path(yaml_dir).expanduser())
        return self.backup_directory

    def get_date_format(self) -> str:
        """Get date format for organizing files."""
        result: str = self._yaml_config.get("backup", {}).get("date_format", self.date_format)
        return result

    def get_logging_level(self) -> str:
        """Get logging level."""
        result: str = self._yaml_config.get("logging", {}).get("level", "INFO")
        return result

    def get_logging_file(self) -> str:
        """Get logging file path."""
        result: str = self._yaml_config.get("logging", {}).get("file", self.log_file)
        return result

    def should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from backup."""
        import fnmatch

        # Check exact file matches
        exclude_files = self.get_exclude_files()
        if file_path in exclude_files:
            return True

        # Check pattern matches
        exclude_patterns = self.get_exclude_patterns()
        return any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns)
