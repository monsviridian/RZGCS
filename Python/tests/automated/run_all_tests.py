#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RZGCS Automated Test Suite Runner
This script discovers and runs all automated tests for the RZGCS application
"""

import os
import sys
import unittest
import time
import argparse
from datetime import datetime

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def discover_and_run_tests(pattern='test_*.py', verbose=True, output_file=None):
    """Discover and run all tests matching the pattern"""
    start_time = time.time()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern=pattern)
    
    # Set up test runner
    if output_file:
        with open(output_file, 'w') as f:
            runner = unittest.TextTestRunner(stream=f, verbosity=2 if verbose else 1)
            result = runner.run(suite)
    else:
        runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
        result = runner.run(suite)
    
    end_time = time.time()
    
    # Print summary
    print("\n" + "="*80)
    print(f"RZGCS Test Suite completed in {end_time - start_time:.2f} seconds")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*80)
    
    # Return non-zero exit code if there were failures or errors
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run RZGCS automated tests')
    parser.add_argument('--pattern', default='test_*.py', help='Pattern for test files to run')
    parser.add_argument('--quiet', action='store_true', help='Run tests with minimal output')
    parser.add_argument('--output', help='Output file for test results')
    parser.add_argument('--timestamp', action='store_true', help='Add timestamp to output file')
    
    args = parser.parse_args()
    
    # Add timestamp to output file if requested
    output_file = args.output
    if output_file and args.timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base, ext = os.path.splitext(output_file)
        output_file = f"{base}_{timestamp}{ext}"
    
    print(f"Running RZGCS tests with pattern: {args.pattern}")
    sys.exit(discover_and_run_tests(args.pattern, not args.quiet, output_file))
