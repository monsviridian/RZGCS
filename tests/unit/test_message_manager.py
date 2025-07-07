"""
Unit tests for the MessageManager class.
"""
import pytest
from unittest.mock import MagicMock

class TestMessageManager:
    """Test cases for MessageManager."""
    
    @pytest.fixture
    def message_manager(self):
        """Create a MessageManager instance for testing."""
        from Python.message_manager import MessageManager
        return MessageManager()
    
    def test_initialization(self, message_manager):
        """Test that MessageManager initializes correctly."""
        assert len(message_manager.messages) == 0
        assert message_manager.max_messages == 1000
        
    def test_add_message(self, message_manager):
        """Test adding a message to the manager."""
        test_message = "Test message"
        message_manager.add_message(test_message, 1)  # 1 = INFO type
        
        assert len(message_manager.messages) == 1
        assert message_manager.messages[0]["message"] == test_message
        assert message_manager.messages[0]["type"] == 1
        
    def test_message_trimming(self, message_manager):
        """Test that messages are trimmed when max_messages is reached."""
        message_manager.max_messages = 5
        
        # Add more messages than the limit
        for i in range(10):
            message_manager.add_message(f"Message {i}", 1)
            
        # Should only keep the last 5 messages
        assert len(message_manager.messages) == 5
        assert message_manager.messages[0]["message"] == "Message 5"
        
    def test_clear_messages(self, message_manager):
        """Test clearing all messages."""
        # Add some test messages
        for i in range(3):
            message_manager.add_message(f"Test {i}", 1)
            
        # Clear and verify
        message_manager.clear_messages()
        assert len(message_manager.messages) == 0
