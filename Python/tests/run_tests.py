#!/usr/bin/env python3
"""
RZGCS Test Runner

Dieses Skript führt alle Tests für die RZGCS-Anwendung aus.
"""

import pytest
import os
import sys
import platform
import argparse
from datetime import datetime

def run_tests(args):
    """Führt die Tests mit den angegebenen Argumenten aus"""
    # Get the current directory (where run_tests.py is located)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Add project root to system path for imports
    sys.path.insert(0, project_root)
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(current_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate timestamp for report filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Determine which tests to run
    if args.all:
        # Alle verfügbaren Tests ausführen
        test_files = [
            # Original tests
            'test_3d_map_standalone.py',
            'test_map_sockets.py',
            'test_3d_view.py',
            'test_connection.py',
            'test_end_to_end.py',
            'test_integration.py',
            'test_mavlink_connector.py',
            'test_mavlink_simulator.py',
            'test_parameter_model.py',
            'test_performance.py',
            'test_security.py',
            'test_sensorviewmodel.py',
            'test_simulated_drone.py',
            'test_ui_components.py',
            
            # Neue Tests
            'test_license_system.py',
            'test_platform_compatibility.py',
            'test_angel_mode.py'
        ]
    elif args.platform:
        # Plattformspezifische Tests ausführen
        test_files = [
            'test_platform_compatibility.py',
            'test_connection.py',
            'test_mavlink_connector.py'
        ]
    elif args.license:
        # Lizenzsystem-Tests ausführen
        test_files = [
            'test_license_system.py',
            'test_angel_mode.py'
        ]
    elif args.quick:
        # Schnelle Tests ohne UI-Komponenten
        test_files = [
            'test_license_system.py',
            'test_platform_compatibility.py',
            'test_mavlink_connector.py',
            'test_parameter_model.py',
            'test_sensorviewmodel.py'
        ]
    else:
        # Standard-Testauswahl (wichtigste Tests)
        test_files = [
            'test_3d_map_standalone.py',
            'test_map_sockets.py',
            'test_license_system.py',
            'test_platform_compatibility.py'
        ]
    
    # Filter tests based on current platform if requested
    if args.current_platform_only:
        current_platform = platform.system().lower()
        print(f"Filtering tests for current platform: {current_platform}")
        if current_platform == 'darwin':
            # Spezifische Tests für macOS
            test_files = [file for file in test_files if 'platform' in file or not any(x in file for x in ['3d', 'ui_components'])]
        elif current_platform == 'windows':
            # Alle Tests auf Windows laufen lassen
            pass
        elif current_platform == 'linux':
            # Spezifische Tests für Linux
            test_files = [file for file in test_files if 'platform' in file or not any(x in file for x in ['3d', 'ui_components'])]
    
    # Build pytest arguments
    pytest_args = [
        '--cov=..',  # Measure coverage for the entire project
        '--cov-report=html',  # Generate HTML coverage report
        f'--html={reports_dir}/test_report_{timestamp}.html',  # HTML test report
        '--self-contained-html',  # Make HTML report self-contained
        f'--junitxml={reports_dir}/junit_{timestamp}.xml',  # JUnit style XML report
    ]
    
    # Add verbosity level
    if args.verbose:
        pytest_args.append('-v')
    
    # Add test files to the command
    pytest_args.extend(test_files)
    
    # Change to the tests directory
    os.chdir(current_dir)
    
    # Print debug info
    print("\n" + "="*80)
    print(f"RZGCS Test Runner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print("="*80)
    print("Running tests from:", os.getcwd())
    print("Test files to run:")
    for i, test in enumerate(test_files, 1):
        print(f"  {i}. {test}")
    print("="*80 + "\n")
    
    # Run the tests
    exit_code = pytest.main(pytest_args)
    
    # Print a summary
    print("\n" + "="*80)
    print("Test execution completed!")
    print(f"Reports generated in: {reports_dir}")
    print(f"Exit code: {exit_code}")
    print("="*80 + "\n")
    
    return exit_code

def main():
    """Haupteinstiegspunkt mit Argumentparser"""
    parser = argparse.ArgumentParser(description='RZGCS Test Runner')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--platform', action='store_true', help='Run platform compatibility tests')
    parser.add_argument('--license', action='store_true', help='Run license system tests')
    parser.add_argument('--quick', action='store_true', help='Run quick tests without UI components')
    parser.add_argument('--current-platform-only', action='store_true', help='Run only tests compatible with current platform')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    return run_tests(args)

if __name__ == "__main__":
    sys.exit(main())