"""
Pytest configuration and fixtures for RZGCS tests.
"""
import os
import sys
import pytest
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture(scope='session')
def test_data_dir():
    """Fixture to provide path to test data directory."""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    return TEST_DATA_DIR

# Add any common fixtures here
