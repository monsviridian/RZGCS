#!/usr/bin/env python3
"""
Script to fix syntax errors in mavlink_v2_integration.py
"""

def fix_syntax_errors():
    with open('Python/backend/mavlink_v2_integration.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix specific indentation issues
    for i, line in enumerate(lines):
        # Fix _handle_heartbeat method
        if 'def _handle_heartbeat' in line:
            # Find the try block and fix indentation
            j = i + 1
            while j < len(lines) and 'try:' not in lines[j]:
                j += 1
            if j < len(lines):
                # Fix the try line
                lines[j] = '        try:\n'
                # Fix the next few lines
                for k in range(j + 1, min(j + 10, len(lines))):
                    if 'base_mode = message.payload.get' in lines[k]:
                        lines[k] = '            base_mode = message.payload.get(\'base_mode\', 0)\n'
                    elif 'custom_mode = message.payload.get' in lines[k]:
                        lines[k] = '            custom_mode = message.payload.get(\'custom_mode\', 0)\n'
                    elif 'except Exception as e:' in lines[k]:
                        break
        
        # Fix _handle_mission_item method
        elif 'def _handle_mission_item' in line:
            # Find the if statement and fix indentation
            j = i + 1
            while j < len(lines) and 'if self._mission_manager:' not in lines[j]:
                j += 1
            if j < len(lines):
                lines[j] = '            if self._mission_manager:\n'
                # Fix the next few lines
                for k in range(j + 1, min(j + 5, len(lines))):
                    if 'self._mission_manager.mission_items.append' in lines[k]:
                        lines[k] = '                self._mission_manager.mission_items.append(mission_item)\n'
                    elif 'self.missionItemReceived.emit' in lines[k]:
                        lines[k] = '                self.missionItemReceived.emit(mission_item)\n'
                    elif 'except Exception as e:' in lines[k]:
                        break
    
    # Write the corrected file
    with open('Python/backend/mavlink_v2_integration.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Syntax errors fixed!")

if __name__ == "__main__":
    fix_syntax_errors() 