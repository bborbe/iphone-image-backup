"""Configuration management for iPhone backup tool"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Any


class BackupConfig:
    """Handles configuration loading and management"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "config.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            # Return default configuration if file doesn't exist
            return self._get_default_config()
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"⚠️  Warning: Could not load config file {config_path}: {e}")
            print("📝 Using default configuration")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'backup': {
                'default_directory': "~/Downloads/iPhoneImageBackup",
                'create_subdirs': True,
                'date_format': "%Y/%Y-%m-%d"
            },
            'files': {
                'photo_extensions': [".jpg", ".jpeg", ".png", ".heic", ".gif", ".tiff", ".bmp", ".dng", ".raw", ".cr2", ".nef"],
                'video_extensions': [".mov", ".mp4", ".m4v", ".avi", ".mkv"],
                'exclude_files': [],
                'exclude_patterns': [
                    "*/Thumbnails/*",
                    "*/Cache/*",
                    "*/Metadata/*",
                    "*.tmp",
                    "*.cache"
                ]
            },
            'logging': {
                'level': "INFO",
                'file': "iphone_backup.log"
            },
            'device': {
                'auto_connect': True,
                'trust_prompt': True
            }
        }
    
    def get_photo_extensions(self) -> List[str]:
        """Get list of photo file extensions"""
        return self.config.get('files', {}).get('photo_extensions', [])
    
    def get_video_extensions(self) -> List[str]:
        """Get list of video file extensions"""
        return self.config.get('files', {}).get('video_extensions', [])
    
    def get_all_extensions(self) -> List[str]:
        """Get all supported file extensions"""
        photo_exts = self.get_photo_extensions()
        video_exts = self.get_video_extensions()
        return photo_exts + video_exts
    
    def get_exclude_files(self) -> List[str]:
        """Get list of files to exclude from backup"""
        return self.config.get('files', {}).get('exclude_files', [])
    
    def get_exclude_patterns(self) -> List[str]:
        """Get list of patterns to exclude from backup"""
        return self.config.get('files', {}).get('exclude_patterns', [])
    
    def get_backup_directory(self) -> str:
        """Get default backup directory"""
        return self.config.get('backup', {}).get('default_directory', "~/Downloads/iPhoneImageBackup")
    
    def get_date_format(self) -> str:
        """Get date format for organizing files"""
        return self.config.get('backup', {}).get('date_format', "%Y/%Y-%m-%d")
    
    def get_logging_level(self) -> str:
        """Get logging level"""
        return self.config.get('logging', {}).get('level', "INFO")
    
    def get_logging_file(self) -> str:
        """Get logging file path"""
        return self.config.get('logging', {}).get('file', "iphone_backup.log")
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from backup"""
        import fnmatch
        
        # Check exact file matches
        exclude_files = self.get_exclude_files()
        if file_path in exclude_files:
            return True
        
        # Check pattern matches
        exclude_patterns = self.get_exclude_patterns()
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        
        return False
    
    def get_config_value(self, key_path: str, default=None):
        """Get a configuration value by dot-separated key path"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value