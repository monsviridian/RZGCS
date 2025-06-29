#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom Vehicle subclass for RZGCS
Extends DroneKit's Vehicle class with custom attributes and message handling
"""

from dronekit import Vehicle
import math
import time

class RZGCSVehicle(Vehicle):
    """
    Custom Vehicle subclass for RZGCS with enhanced telemetry and status tracking
    """
    
    def __init__(self, *args, **kwargs):
        super(RZGCSVehicle, self).__init__(*args, **kwargs)
        
        # Custom telemetry attributes
        self._enhanced_telemetry = {
            'last_update': time.time(),
            'connection_quality': 100.0,
            'message_rate': 0.0,
            'error_count': 0,
            'warning_count': 0
        }
        
        # Message counters for rate calculation
        self._message_counters = {}
        self._last_message_time = time.time()
        
        # Setup message listeners
        self._setup_message_listeners()
    
    def _setup_message_listeners(self):
        """Setup message listeners for enhanced telemetry"""
        
        @self.on_message('HEARTBEAT')
        def heartbeat_listener(self, name, message):
            """Monitor heartbeat for connection quality"""
            current_time = time.time()
            self._enhanced_telemetry['last_update'] = current_time
            
            # Calculate message rate
            if 'HEARTBEAT' not in self._message_counters:
                self._message_counters['HEARTBEAT'] = 0
            self._message_counters['HEARTBEAT'] += 1
            
            # Update message rate every second
            if current_time - self._last_message_time >= 1.0:
                self._enhanced_telemetry['message_rate'] = self._message_counters['HEARTBEAT']
                self._message_counters['HEARTBEAT'] = 0
                self._last_message_time = current_time
                
                # Notify listeners of enhanced telemetry update
                self.notify_attribute_listeners('enhanced_telemetry', self._enhanced_telemetry)
        
        @self.on_message('SYS_STATUS')
        def sys_status_listener(self, name, message):
            """Monitor system status for errors and warnings"""
            # Count errors and warnings
            if hasattr(message, 'errors_count1') and message.errors_count1 > 0:
                self._enhanced_telemetry['error_count'] = message.errors_count1
            if hasattr(message, 'errors_count2') and message.errors_count2 > 0:
                self._enhanced_telemetry['warning_count'] = message.errors_count2
                
            # Notify listeners
            self.notify_attribute_listeners('enhanced_telemetry', self._enhanced_telemetry)
        
        @self.on_message('GPS_RAW_INT')
        def gps_listener(self, name, message):
            """Enhanced GPS monitoring"""
            # Calculate connection quality based on GPS fix
            if hasattr(message, 'fix_type'):
                if message.fix_type >= 3:  # 3D fix or better
                    self._enhanced_telemetry['connection_quality'] = 100.0
                elif message.fix_type == 2:  # 2D fix
                    self._enhanced_telemetry['connection_quality'] = 75.0
                elif message.fix_type == 1:  # No fix
                    self._enhanced_telemetry['connection_quality'] = 25.0
                else:
                    self._enhanced_telemetry['connection_quality'] = 0.0
                    
                # Notify listeners
                self.notify_attribute_listeners('enhanced_telemetry', self._enhanced_telemetry)
    
    @property
    def enhanced_telemetry(self):
        """Enhanced telemetry information"""
        return self._enhanced_telemetry
    
    @property
    def connection_quality(self):
        """Connection quality percentage"""
        return self._enhanced_telemetry.get('connection_quality', 0.0)
    
    @property
    def message_rate(self):
        """Current message rate (messages per second)"""
        return self._enhanced_telemetry.get('message_rate', 0.0)
    
    @property
    def error_count(self):
        """Number of system errors"""
        return self._enhanced_telemetry.get('error_count', 0)
    
    @property
    def warning_count(self):
        """Number of system warnings"""
        return self._enhanced_telemetry.get('warning_count', 0)
    
    def get_connection_status(self):
        """Get comprehensive connection status"""
        current_time = time.time()
        time_since_update = current_time - self._enhanced_telemetry['last_update']
        
        return {
            'connected': self.is_armable is not None,  # Basic connectivity check
            'connection_quality': self.connection_quality,
            'message_rate': self.message_rate,
            'time_since_last_update': time_since_update,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'is_armable': self.is_armable,
            'system_status': self.system_status.state if self.system_status else None,
            'mode': self.mode.name if self.mode else None,
            'armed': self.armed
        } 