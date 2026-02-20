#!/usr/bin/env python3
"""
Test script cuối cùng để kiểm tra toàn bộ project
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    results = []
    
    try:
        import config
        results.append("✓ Config imported")
    except Exception as e:
        results.append(f"❌ Config error: {e}")
    
    try:
        from database.session import get_db
        results.append("✓ Database session imported")
    except Exception as e:
        results.append(f"❌ Database error: {e}")
    
    try:
        from database.models import User, ApiKey, AuditLog
        results.append("✓ Database models imported")
    except Exception as e:
        results.append(f"❌ Models error: {e}")
    
    try:
        from services.audit import record_audit_log
        results.append("✓ Audit service imported")
    except Exception as e:
        results.append(f"❌ Audit error: {e}")
    
    try:
        from api_server import app
        results.append("✓ API server imported")
    except Exception as e:
        results.append(f"❌ API server error: {e}")
    
    try:
        from agent_graph import app_graph
        results.append("✓ Agent graph imported")
    except Exception as e:
        results.append(f"❌ Agent graph error: {e}")
    
    return results

if __name__ == "__main__":
    print("Testing Phil-CLI imports...")
    print("=" * 50)
    
    results = test_imports()
    
    for result in results:
        print(result)
    
    success_count = len([r for r in results if r.startswith("✓")])
    total_count = len(results)
    
    print("=" * 50)
    print(f"Results: {success_count}/{total_count} modules imported successfully")
    
    if success_count == total_count:
        print("🎉 All imports successful! Project structure is correct.")
    else:
        print("⚠️  Some imports failed. Check the errors above.")