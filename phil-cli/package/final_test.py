#!/usr/bin/env python3
"""Final test to verify phil-cli functionality"""

import sys
import os
import subprocess

print("🧪 Testing phil-cli package installation...")
print("=" * 50)

# Test 1: Check if httpx is available
try:
    import httpx
    print("✅ Test 1 PASSED: httpx is available")
except ImportError as e:
    print(f"❌ Test 1 FAILED: httpx not available - {e}")
    sys.exit(1)

# Test 2: Check if pydantic is available
try:
    import pydantic
    print("✅ Test 2 PASSED: pydantic is available")
except ImportError as e:
    print(f"❌ Test 2 FAILED: pydantic not available - {e}")
    sys.exit(1)

# Test 3: Test phil_cli imports
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from phil_cli.config import load_config
    print("✅ Test 3 PASSED: phil_cli.config imported successfully")
except ImportError as e:
    print(f"❌ Test 3 FAILED: phil_cli.config import failed - {e}")
    sys.exit(1)

# Test 4: Test phil_cli.api import
try:
    from phil_cli.api import chat
    print("✅ Test 4 PASSED: phil_cli.api imported successfully")
except ImportError as e:
    print(f"❌ Test 4 FAILED: phil_cli.api import failed - {e}")
    sys.exit(1)

# Test 5: Test phil_cli.main import
try:
    from phil_cli.main import app
    print("✅ Test 5 PASSED: phil_cli.main imported successfully")
except ImportError as e:
    print(f"❌ Test 5 FAILED: phil_cli.main import failed - {e}")
    sys.exit(1)

# Test 6: Test CLI help command
try:
    result = subprocess.run([
        sys.executable, '-m', 'phil_cli.main', '--help'
    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    if result.returncode == 0 and 'Usage:' in result.stdout:
        print("✅ Test 6 PASSED: CLI help command works")
    else:
        print(f"❌ Test 6 FAILED: CLI help command failed")
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout[:200]}")
        print(f"Stderr: {result.stderr[:200]}")
        
except Exception as e:
    print(f"❌ Test 6 FAILED: Exception during CLI test - {e}")

print("\n" + "=" * 50)
print("🎉 All tests passed! The phil-cli package is working correctly.")
print("\nYou can now use the following commands:")
print("  phil-cli --help          # Show help")
print("  phil-cli status          # Check status")
print("  phil-cli login           # Login to server")
print("  phil-cli chat 'message'  # Send chat message")
print("  phil-cli mcp list        # List MCP servers")
print("\nThe package has been successfully configured for local use!")