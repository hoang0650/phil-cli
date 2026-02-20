#!/usr/bin/env python3
"""Test script to verify phil-cli functionality"""

import sys
import os

# Add the package directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from phil_cli.main import app
    print("✓ Successfully imported phil_cli.main")
    
    # Test basic CLI functionality
    print("✓ Testing CLI help...")
    app(["--help"])
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()