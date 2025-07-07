"""
Unit tests for the MAVLink message handler.
"""
import pytest
import time
from unittest.mock import MagicMock, patch

class TestMessageHandler:
    """Test cases for the MAVLink message handler."""
    
    @pytest.fixture
    def message_handler(self):
        """Create a MessageHandler instance for testing."""
        from Python.message_handler import MessageHandler
        return MessageHandler()
    
    def test_handle_message_first_time(self, message_handler):
        """Test handling a message for the first time."""
        test_msg = {"type": "GPS_RAW_INT", "data": {"lat": 48.12345, "lon": 11.56789}}
        
        # First call should process the message
        result = message_handler.handle_message(test_msg)
        assert result is True
        
    def test_handle_message_duplicate_filtering(self, message_handler):
        """Test duplicate message filtering."""
        test_msg = {"type": "GPS_RAW_INT", "data": {"lat": 48.12345, "lon": 11.56789}}
        
        # First call should process
        assert message_handler.handle_message(test_msg) is True
        
        # Immediate duplicate should be filtered out
        assert message_handler.handle_message(test_msg) is False
        
    def test_handle_message_min_interval(self, message_handler, monkeypatch):
        """Test minimum interval between same message types."""
        test_msg = {"type": "ATTITUDE", "data": {"roll": 0.1, "pitch": 0.2}}
        
        # First message should be processed
        assert message_handler.handle_message(test_msg) is True
        
        # Second message with same type but different data should be filtered due to min interval
        test_msg["data"]["roll"] = 0.15
        assert message_handler.handle_message(test_msg) is False
        
        # After min interval, new message should be processed
        monkeypatch.setattr(time, 'time', lambda: time.time() + 2.0)  # Fast forward time
        assert message_handler.handle_message(test_msg) is True
        
    def test_handle_message_significant_change(self, message_handler):
        """Test that significant changes bypass the min interval."""
        test_msg = {"type": "SYS_STATUS", "data": {"voltage_battery": 12.3}}
        
        # First message
        assert message_handler.handle_message(test_msg) is True
        
        # Small change should be filtered
        test_msg["data"]["voltage_battery"] = 12.31
        assert message_handler.handle_message(test_msg) is False
        
        # Significant change should be processed
        test_msg["data"]["voltage_battery"] = 11.5  # Big drop in voltage
        assert message_handler.handle_message(test_msg) is True
        
    def test_handle_critical_message(self, message_handler):
        """Test that critical messages are always processed."""
        critical_msg = {"type": "STATUSTEXT", "data": {"text": "CRITICAL: Low battery"}}
        
        # Should always be processed regardless of timing
        assert message_handler.handle_message(critical_msg) is True
        assert message_handler.handle_message(critical_msg) is True  # Even duplicates
