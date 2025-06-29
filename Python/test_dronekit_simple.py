#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple DroneKit Test Script
Tests basic DroneKit functionality with SITL simulator
"""

# Python 3.13 Kompatibilitätsfix für DroneKit
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

# Use real serial port for test
connection_string = 'com8'
baud = 115200

# Import DroneKit-Python
from dronekit import connect, VehicleMode

# Connect to the Vehicle (real serial)
print("Connecting to vehicle on: %s (baud %d)" % (connection_string, baud))
vehicle = connect(connection_string, wait_ready=True, baud=baud)

# Get some vehicle attributes (state)
print("Get some vehicle attribute values:")
print(" GPS: %s" % vehicle.gps_0)
print(" Battery: %s" % vehicle.battery)
print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
print(" Is Armable?: %s" % vehicle.is_armable)
print(" System status: %s" % vehicle.system_status.state)
print(" Mode: %s" % vehicle.mode.name)    # settable

# Test our custom connector
print("\nTesting our custom connector...")
from backend.rzgcs_dronekit.connector import DroneKitConnector

connector = DroneKitConnector(connection_string)
success = connector.establish_connection()

if success:
    print("✓ Custom connector connection successful!")
    print(" Connected: %s" % connector.is_connected)
    if connector.vehicle:
        print(" Vehicle ready: %s" % connector.vehicle.is_armable)
        print(" Flight mode: %s" % connector.vehicle.mode.name)
        print(" Armed: %s" % connector.vehicle.armed)
        print(" GPS: %s" % connector.vehicle.gps_0)
        print(" Battery: %s" % connector.vehicle.battery)
    
    # Close our connector
    connector.close_connection()
else:
    print("✗ Custom connector connection failed!")

# Close vehicle object before exiting script
vehicle.close()
print("Completed") 