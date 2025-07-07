#!/usr/bin/env python3
"""
Script to fix syntax errors in mavlink_v2_integration.py
"""

import re

def fix_syntax_errors():
    with open('Python/backend/mavlink_v2_integration.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix indentation issues in _handle_heartbeat
    content = re.sub(
        r'(\s+)base_mode = message\.payload\.get\(\'base_mode\', 0\)\n(\s+)custom_mode = message\.payload\.get\(\'custom_mode\', 0\)',
        r'\1            base_mode = message.payload.get(\'base_mode\', 0)\n\1            custom_mode = message.payload.get(\'custom_mode\', 0)',
        content
    )
    
    # Fix indentation in _handle_mission_item
    content = re.sub(
        r'(\s+)if self\._mission_manager:\n(\s+)self\._mission_manager\.mission_items\.append\(mission_item\)\n(\s+)self\.missionItemReceived\.emit\(mission_item\)',
        r'\1            if self._mission_manager:\n\1                self._mission_manager.mission_items.append(mission_item)\n\1                self.missionItemReceived.emit(mission_item)',
        content
    )
    
    # Remove duplicate _handle_parameter_value method
    content = re.sub(
        r'\s+def _handle_parameter_value\(self, message: MAVLinkV2Message\) -> None:\s*\n\s+"""Handle parameter value message"""\s*\n\s+try:\s*\n\s+param_id = message\.payload\.get\(\'param_id\', \'\'\)\.rstrip\(\'\\x00\'\)\s*\n\s+param_value = message\.payload\.get\(\'param_value\', 0\)\s*\n\s+self\.parameterUpdated\.emit\(param_id, param_value\)\s*\n\s+except Exception as e:\s*\n\s+logger\.error\(f"Error handling parameter value: \{e\}"\)',
        '',
        content
    )
    
    # Fix other indentation issues
    content = re.sub(
        r'(\s+)def _handle_parameter_value\(self, message: MAVLinkV2Message\) -> None:',
        r'\1    def _handle_parameter_value(self, message: MAVLinkV2Message) -> None:',
        content
    )
    
    with open('Python/backend/mavlink_v2_integration.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Syntax errors fixed!")

if __name__ == "__main__":
    fix_syntax_errors() 