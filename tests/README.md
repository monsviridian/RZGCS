# RZGCS Test Suite

This directory contains the test suite for the RZGCS application.

## Test Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for component interactions
- `data/`: Test data files (if needed)

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r ../requirements-test.txt
```

### Running All Tests

```bash
# Using the test runner script
python ../run_tests.py

# Or using pytest directly
pytest tests/
```

### Running Specific Tests

```bash
# Run a specific test file
pytest tests/unit/test_serial_connector.py

# Run a specific test class
pytest tests/unit/test_serial_connector.py::TestMavlinkSerialConnector

# Run a specific test method
pytest tests/unit/test_serial_connector.py::TestMavlinkSerialConnector::test_connect_success
```

### Test Coverage

To generate a coverage report:

```bash
pytest --cov=Python tests/
```

## Writing New Tests

1. For unit tests, add them to the appropriate file in `tests/unit/`
2. For integration tests, add them to `tests/integration/`
3. Use descriptive test method names starting with `test_`
4. Keep tests focused and test one thing at a time
5. Use fixtures for common setup/teardown

## Continuous Integration

The test runner generates JUnit-compatible XML reports in the `test-reports/` directory, which can be used by CI systems.

## Mocking

Use the `unittest.mock` library to mock external dependencies in tests. See existing tests for examples.
