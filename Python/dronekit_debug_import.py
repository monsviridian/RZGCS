# Python 3.13 Kompatibilitätsfix für DroneKit/pymavlink
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

import sys
try:
    import dronekit
    print('dronekit.__file__:', dronekit.__file__)
    print('dronekit attributes:', dir(dronekit))
except Exception as e:
    print('Fehler beim Import von dronekit:', e)

print('sys.path:')
for p in sys.path:
    print('  ', p) 