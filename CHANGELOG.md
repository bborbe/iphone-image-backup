# Changelog

All notable changes to this project will be documented in this file.

Please choose versions by [Semantic Versioning](http://semver.org/).

* MAJOR version when you make incompatible API changes,
* MINOR version when you add functionality in a backwards-compatible manner, and
* PATCH version when you make backwards-compatible bug fixes.

## v0.5.1

- Fix Makefile precommit target to include sync dependency
- Add sync target for consistent dependency management

## v0.5.0

- migrate to modern Python architecture with pyproject.toml and src/ layout
- add Pydantic BaseSettings for configuration management
- implement factory pattern for dependency injection
- add command pattern with separate modules for backup/info/list-devices
- add tests/conftest.py with shared pytest fixtures
- add comprehensive test coverage for command modules
- improve exception logging in config modules
- replace print statements with logging in configuration handling
- add uv.lock for reproducible builds
- update all modules with strict mypy type checking
- clean up Makefile precommit message formatting

## v0.4.2

- modernize PIL API usage by replacing deprecated _getexif() with getexif()
- improve code safety with .get() method for dictionary access
- add explanatory comments for timestamp preference logic
- clean up Makefile formatting and structure
- update test mocks to match modernized API implementation

## v0.4.1

- fix date extraction logic for iPhone filesystem metadata
- update date extractor to properly handle AFC stat dictionary format
- fix filesystem date extraction to prioritize st_birthtime over st_mtime
- add make test target for running unit tests
- update test cases to match corrected date extraction implementation

## v0.4.0

- implement file-based fingerprint system for duplicate prevention
- replace database-based fingerprinting with file-based approach
- move fingerprint tools to proper src directory structure
- add comprehensive test suite for fingerprint functionality
- integrate fingerprint duplicate detection into backup workflow
- add support for additional raw photo formats (dng, raw, cr2, nef)
- add duplicates tracking to backup statistics
- fix all test failures and ensure complete test coverage

## v0.3.0

- allow skip files from backup (if stuck on phone)
- add configurable file exclusion patterns and specific file exclusions
- implement YAML-based configuration management
- add support for excluding files by exact path match
- add support for excluding files by glob patterns
- improve backup workflow to respect exclusion settings

## v0.2.0

- add list files for debugging
- implement comprehensive iPhone file system exploration tool
- add device file listing functionality for troubleshooting
- support for browsing iPhone directory structure
- add file metadata display and analysis capabilities

## v0.1.0

- add iPhone image backup functionality
- direct iPhone photo/video backup using pymobiledevice3
- bypass iTunes/Image Capture for direct device access
- automatic date-based folder organization (YYYY/YYYY-MM-DD)
- support for HEIC, JPG, PNG, MOV, MP4, and other common formats
- EXIF date extraction with filesystem fallback
- modular architecture with separate components for device, scanning, backup
- comprehensive test suite with unit tests for all components
- error handling for device connection issues and file access problems
- detailed backup statistics and progress reporting

## v0.0.1

- initial commit
- project setup with LICENSE and README
- basic project structure and documentation