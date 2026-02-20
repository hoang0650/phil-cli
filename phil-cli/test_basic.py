#!/usr/bin/env python3
"""
Test script đơn giản để kiểm tra import cơ bản
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing basic imports...")
    
    # Test config
    import config
    print("✓ Config module imported")
    
    print("\n🎉 Basic imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()