# run_tests.py
import pytest
import os
import sys
from datetime import datetime

def run_tests():
    # Get the current directory (where run_tests.py is located)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(current_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate timestamp for report filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # List of test files to run
    test_files = [
        'test_3d_map_standalone.py',
        'test_map_sockets.py'
    ]
    
    # Run tests with coverage and generate HTML report
    pytest_args = [
        '--cov=..',  # Measure coverage for the entire project
        '--cov-report=html',  # Generate HTML coverage report
        f'--html={reports_dir}/test_report_{timestamp}.html',  # HTML test report
        '--self-contained-html',  # Make HTML report self-contained
        f'--junitxml={reports_dir}/junit.xml',  # JUnit style XML report
        '-v'  # Verbose output
    ] + test_files  # Add test files to the command
    
    # Change to the tests directory
    os.chdir(current_dir)
    
    # Print debug info
    print("Running tests from:", os.getcwd())
    print("Test files to run:", test_files)
    
    # Run the tests
    exit_code = pytest.main(pytest_args)
    
    # Print a summary
    print("\n" + "="*80)
    print("Test execution completed!")
    print(f"Reports generated in: {reports_dir}")
    print("="*80 + "\n")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())