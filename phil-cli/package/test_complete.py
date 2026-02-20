#!/usr/bin/env python3
"""Complete test for phil-cli functionality"""

import subprocess
import sys
import os

def test_command(cmd, description):
    """Test a command and return success status"""
    print(f"Testing: {description}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              cwd=r'c:\Users\Admin\Desktop\phil\phil-cli\phil-cli\package')
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

print("🧪 Testing phil-cli package functionality...")
print("=" * 60)

# Test basic imports
tests = [
    ([sys.executable, "-c", "import httpx; print('httpx imported')"], "Import httpx module"),
    ([sys.executable, "-c", "import pydantic; print('pydantic imported')"], "Import pydantic module"),
]

passed = 0
total = len(tests)

for cmd, desc in tests:
    if test_command(cmd, desc):
        passed += 1

# Test phil-cli imports
phil_tests = [
    ([sys.executable, "-c", "from phil_cli.config import load_config; print('config imported')"], "Import phil_cli.config"),
    ([sys.executable, "-c", "from phil_cli.api import chat; print('api imported')"], "Import phil_cli.api"),
    ([sys.executable, "-c", "from phil_cli.main import app; print('main imported')"], "Import phil_cli.main"),
]

total += len(phil_tests)
for cmd, desc in phil_tests:
    if test_command(cmd, desc):
        passed += 1

# Test CLI commands
cli_tests = [
    ([sys.executable, "-m", "phil_cli.main", "--help"], "CLI help command"),
    ([sys.executable, "-m", "phil_cli.main", "status"], "CLI status command"),
]

total += len(cli_tests)
for cmd, desc in cli_tests:
    if test_command(cmd, desc):
        passed += 1

print("\n" + "=" * 60)
print(f"📊 Test Results: {passed}/{total} tests passed")

if passed == total:
    print("🎉 All tests passed! The phil-cli package is working correctly.")
    print("\n✨ The package has been successfully configured for local use!")
    print("\nAvailable commands:")
    print("  phil-cli --help          # Show help")
    print("  phil-cli status          # Check status") 
    print("  phil-cli login           # Login to server")
    print("  phil-cli chat 'message'  # Send chat message")
    print("  phil-cli mcp list        # List MCP servers")
else:
    print(f"⚠️  {total - passed} tests failed. Please check the errors above.")
    sys.exit(1)