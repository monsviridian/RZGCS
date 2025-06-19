# RZGCS Logger Documentation

## Overview
The Logger module is a core component of the RZGCS (Remote Zentrum Ground Control Station) application. It provides a centralized logging system that integrates with both Python's standard logging module and the Qt framework's signal/slot mechanism.

## Class: Logger

### Description
The `Logger` class is a Qt-based logging system that maintains a history of log messages, provides methods for adding new logs, and emits signals when the log collection changes. It integrates with Python's standard logging module while also providing Qt-friendly interfaces.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `logs` | QVariantList | A list of all log entries in the system, accessible from QML. |

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `logAdded` | str | Emitted when a new log entry is added to the system. |
| `logsChanged` | None | Emitted when the collection of logs changes. |

### Methods

#### `__init__()`
Initializes the Logger instance.
- Creates an empty log collection
- Sets the maximum number of logs to keep (1000)
- Configures the Python logging system
- Initializes the logger with a confirmation message

#### `addLog(message: str)`
Adds a new log entry to the system.
- **Parameters:**
  - `message`: The message text to log
- **Behavior:**
  - Timestamps the message
  - Prints the log entry to the console
  - Adds the entry to the logs collection
  - Trims the collection if it exceeds the maximum size
  - Emits the `logAdded` and `logsChanged` signals
  - Prints the current log count

#### `getLogs() -> str`
Returns all logs as a single string.
- **Returns:** A newline-separated string of all log entries

#### `clear()`
Clears all logs from the system.
- **Behavior:**
  - Empties the logs collection
  - Emits the `logsChanged` signal
  - Adds a "Logs cleared" message

## Integration with Qt/QML

The Logger class is designed to be accessible from QML through the following mechanisms:
- The `logs` property can be bound to QML elements
- The `logAdded` signal can trigger QML event handlers
- The `addLog()` method can be called from QML

## Message Filtering System

The Logger works in conjunction with a comprehensive MAVLink message filtering system that:

1. Caches the most recent values of each message type
2. Only logs messages when values change significantly (using configurable thresholds)
3. Enforces minimum time intervals between logging the same message type
4. Ensures critical messages like status texts are always logged

This filtering system helps reduce log spamming when a real flight controller is connected, ensuring that the logs remain manageable and focused on important information.

## Best Practices

1. Use the `addLog()` method for application-level messages that should be displayed in the UI
2. For more complex logging needs, consider using the standard Python `logging` module directly
3. Keep in mind the 1000 log entry limit when designing UI elements that display logs
4. When implementing new message handlers, consider appropriate filtering thresholds to avoid log spam

## Example Usage

### Python
```python
# Obtain logger instance
logger = Logger()

# Add a log entry
logger.addLog("Connection established")

# Get all logs as a string
all_logs = logger.getLogs()

# Clear all logs
logger.clear()
```

### QML
```qml
// Assuming the logger is exposed as a context property named "logger"

// Display all logs
ListView {
    model: logger.logs
    delegate: Text {
        text: modelData
    }
}

// Add a new log entry
Button {
    text: "Log Event"
    onClicked: logger.addLog("Button clicked")
}

// React to new log entries
Connections {
    target: logger
    function onLogAdded(message) {
        console.log("New log: " + message)
    }
}
```
