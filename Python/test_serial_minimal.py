import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect
import traceback

for port in ['COM8', 'com8']:
    print(f"\nTrying connection to vehicle on: {port} (baud 115200)")
    try:
        vehicle = connect(port, wait_ready=True, baud=115200)
        print("Connected!")
        print("Mode:", vehicle.mode.name)
        vehicle.close()
        break
    except Exception as e:
        print(f"Failed to connect on {port}: {e}")
        traceback.print_exc() 