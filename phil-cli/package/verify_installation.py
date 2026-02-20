#!/usr/bin/env python3
"""Verify phil-cli installation"""

import sys
import os

# Test basic imports
try:
    import httpx
    print("✓ httpx is available")
except ImportError as e:
    print(f"✗ httpx not available: {e}")
    sys.exit(1)

try:
    import pydantic
    print("✓ pydantic is available")
except ImportError as e:
    print(f"✗ pydantic not available: {e}")
    sys.exit(1)

# Test phil-cli imports
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from phil_cli.config import load_config
    print("✓ phil_cli.config imported successfully")
except ImportError as e:
    print(f"✗ phil_cli.config import failed: {e}")
    sys.exit(1)

try:
    from phil_cli.api import chat
    print("✓ phil_cli.api imported successfully")
except ImportError as e:
    print(f"✗ phil_cli.api import failed: {e}")
    sys.exit(1)

try:
    from phil_cli.main import app
    print("✓ phil_cli.main imported successfully")
    print("✓ phil-cli package is working correctly!")
except ImportError as e:
    print(f"✗ phil_cli.main import failed: {e}")
    sys.exit(1)

print("\n🎉 All tests passed! The phil-cli package is ready to use.")
print("\nYou can now use commands like:")
print("  phil-cli --help")
print("  phil-cli status") 
print("  phil-cli login")
print("  phil-cli chat 'Hello, how are you?'")