#!/usr/bin/env python3
"""
Test script for MAVLink v2 connection with improved error handling
"""

import sys
import os
import logging

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from mavlink_v2_integration import MAVLinkV2Integration

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_port_availability():
    """Test port availability checking"""
    print("=== Testing Port Availability ===")
    
    integration = MAVLinkV2Integration()
    
    # Get available ports
    ports = integration.get_available_ports()
    print(f"Available ports: {len(ports)}")
    for port in ports:
        print(f"  - {port['device']}: {port['description']}")
    
    # Test specific ports
    test_ports = ['COM8', 'COM1', 'tcp:127.0.0.1:5760']
    
    for port in test_ports:
        print(f"\nTesting port: {port}")
        is_available = integration.test_port_connection(port)
        print(f"  Available: {is_available}")
        
        help_text = integration.get_port_troubleshooting_help(port)
        print(f"  Help: {help_text}")

def test_connection_attempt():
    """Test connection attempt with error handling"""
    print("\n=== Testing Connection Attempt ===")
    
    integration = MAVLinkV2Integration()
    
    # Test with a port that might be in use
    integration.set_connection_string("COM8")
    
    print("Attempting to connect to COM8...")
    success = integration.connect_mavlink()
    print(f"Connection result: {success}")
    
    if not success:
        print("Connection failed as expected due to port access issues")
    else:
        print("Connection succeeded - disconnecting...")
        integration.disconnect_mavlink()

def test_network_connection():
    """Test network connection (should work even without actual MAVLink device)"""
    print("\n=== Testing Network Connection ===")
    
    integration = MAVLinkV2Integration()
    
    # Test with network connection
    integration.set_connection_string("tcp:127.0.0.1:5760")
    
    print("Attempting to connect to TCP localhost...")
    success = integration.connect_mavlink()
    print(f"Connection result: {success}")
    
    if success:
        print("Network connection succeeded - disconnecting...")
        integration.disconnect_mavlink()
    else:
        print("Network connection failed (expected if no MAVLink server running)")

def main():
    """Main test function"""
    setup_logging()
    
    print("MAVLink v2 Connection Test")
    print("=" * 40)
    
    try:
        test_port_availability()
        test_connection_attempt()
        test_network_connection()
        
        print("\n=== Test Complete ===")
        print("The improved error handling should now provide better feedback")
        print("for port access issues and connection problems.")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 