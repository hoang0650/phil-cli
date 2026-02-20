#!/usr/bin/env python3
"""
Test script để kiểm tra import của các module chính
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing imports...")
    
    # Test config
    from config import Config
    print("✓ Config imported successfully")
    
    # Test database
    from database.session import get_db
    print("✓ Database session imported successfully")
    
    # Test models
    from database.models import User, ApiKey, AuditLog
    print("✓ Database models imported successfully")
    
    # Test services
    from services.audit import record_audit_log
    print("✓ Audit service imported successfully")
    
    # Test API server
    from api_server import app
    print("✓ API server imported successfully")
    
    # Test agent graph
    from agent_graph import app_graph
    print("✓ Agent graph imported successfully")
    
    print("\n🎉 All imports successful! Project structure is correct.")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()