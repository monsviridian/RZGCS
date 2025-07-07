#!/usr/bin/env python3
"""
Test runner for RZGCS project.

This script discovers and runs all tests in the tests/ directory.
"""
import sys
import unittest
import xmlrunner
from pathlib import Path

def run_tests():
    """Discover and run all tests."""
    # Add project root to Python path
    project_root = str(Path(__file__).parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Discover all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run tests with XML output for CI
    test_runner = xmlrunner.XMLTestRunner(
        output='test-reports',
        verbosity=2,
        failfast=False,
        buffer=False,
        output_name='test-results',
    )
    
    # Run the tests
    result = test_runner.run(test_suite)
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
