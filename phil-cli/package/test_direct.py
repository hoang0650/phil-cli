#!/usr/bin/env python3
"""Test CLI directly"""

import subprocess
import sys
import os

# Change to package directory
os.chdir(r'c:\Users\Admin\Desktop\phil\phil-cli\phil-cli\package')

# Test direct execution
try:
    result = subprocess.run([sys.executable, '-m', 'phil_cli.main', '--help'], 
                          capture_output=True, text=True, cwd=r'c:\Users\Admin\Desktop\phil\phil-cli\phil-cli\package')
    
    if result.returncode == 0:
        print("✓ CLI help command successful!")
        print("Output:", result.stdout[:200])
    else:
        print("✗ CLI help command failed")
        print("Error:", result.stderr)
        
except Exception as e:
    print(f"✗ Exception: {e}")

# Test status command
try:
    result = subprocess.run([sys.executable, '-m', 'phil_cli.main', 'status'], 
                          capture_output=True, text=True, cwd=r'c:\Users\Admin\Desktop\phil\phil-cli\phil-cli\package')
    
    if result.returncode == 0:
        print("✓ CLI status command successful!")
        print("Output:", result.stdout[:200])
    else:
        print("✗ CLI status command failed")
        print("Error:", result.stderr)
        
except Exception as e:
    print(f"✗ Exception: {e}")