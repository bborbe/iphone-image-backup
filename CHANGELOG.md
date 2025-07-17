# Changelog

All notable changes to this project will be documented in this file.

Please choose versions by [Semantic Versioning](http://semver.org/).

* MAJOR version when you make incompatible API changes,
* MINOR version when you add functionality in a backwards-compatible manner, and
* PATCH version when you make backwards-compatible bug fixes.

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