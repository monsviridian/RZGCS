#!/usr/bin/env python3
"""
Script to fix indentation issues in mavlink_v2_integration.py
"""

def fix_indentation():
    with open('Python/backend/mavlink_v2_integration.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix specific indentation issues
    for i, line in enumerate(lines):
        # Fix update_battery method
        if 'def update_battery(self, voltage, current, remaining):' in line:
            # Fix the next few lines
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip().startswith('self._battery_'):
                    lines[j] = '        ' + lines[j].lstrip()
                elif lines[j].strip().startswith('self.battery'):
                    lines[j] = '        ' + lines[j].lstrip()
                elif lines[j].strip() == '':
                    break
    
    # Write back the fixed file
    with open('Python/backend/mavlink_v2_integration.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Indentation issues fixed!")

if __name__ == "__main__":
    fix_indentation() 