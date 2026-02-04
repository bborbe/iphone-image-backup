"""Shared test fixtures for iphone_backup tests."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_backup_dir() -> Generator[Path]:
    """Create temporary backup directory that's automatically cleaned up.

    Yields:
        Path: Temporary directory path for backup testing
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Create temporary directory for general testing.

    Yields:
        Path: Temporary directory path
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
