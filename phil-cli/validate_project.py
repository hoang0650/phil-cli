#!/usr/bin/env python3
"""
Phil-CLI Project Validation Script
Kiểm tra cấu trúc và cấu hình của dự án Phil-CLI
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Kiểm tra file có tồn tại không"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} thiếu: {filepath}")
        return False

def check_json_valid(filepath, description):
    """Kiểm tra file JSON có hợp lệ không"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✓ {description} JSON hợp lệ: {filepath}")
        return True
    except Exception as e:
        print(f"❌ {description} JSON lỗi: {filepath} - {e}")
        return False

def check_python_syntax(filepath, description):
    """Kiểm tra syntax Python"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            compile(f.read(), filepath, 'exec')
        print(f"✓ {description} syntax OK: {filepath}")
        return True
    except SyntaxError as e:
        print(f"❌ {description} syntax lỗi: {filepath} - {e}")
        return False
    except Exception as e:
        print(f"❌ {description} lỗi: {filepath} - {e}")
        return False

def validate_config():
    """Kiểm tra config.py"""
    config_path = "src/config.py"
    if not os.path.exists(config_path):
        print(f"❌ Config file thiếu: {config_path}")
        return False
    
    try:
        # Đọc và kiểm tra config
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Kiểm tra các config quan trọng
        required_configs = [
            "DATABASE_URL",
            "SECRET_KEY", 
            "API_KEY",
            "CODER_API_BASE",
            "VN_API_BASE",
            "MCP_SERVERS_CONFIG"
        ]
        
        missing_configs = []
        for config in required_configs:
            if config not in content:
                missing_configs.append(config)
        
        if missing_configs:
            print(f"❌ Config thiếu: {', '.join(missing_configs)}")
            return False
        
        print("✓ Config đầy đủ các thiết lập quan trọng")
        return True
        
    except Exception as e:
        print(f"❌ Config lỗi: {e}")
        return False

def main():
    print("🔍 Kiểm tra dự án Phil-CLI...")
    print("=" * 60)
    
    # Thư mục gốc
    root_dir = Path(__file__).parent
    os.chdir(root_dir)
    
    results = []
    
    # 1. Kiểm tra file cấu hình quan trọng
    print("\n📋 Kiểm tra file cấu hình...")
    results.append(check_file_exists("requirements.txt", "Requirements"))
    results.append(check_file_exists(".env.example", "Env example"))
    results.append(check_file_exists("docker-compose.yml", "Docker Compose"))
    results.append(check_file_exists("Dockerfile", "Dockerfile"))
    results.append(check_file_exists("mcp_servers_config.json", "MCP Servers Config"))
    
    # 2. Kiểm tra thư mục source
    print("\n📁 Kiểm tra cấu trúc source...")
    results.append(check_file_exists("src/", "Source directory"))
    results.append(check_file_exists("src/config.py", "Config module"))
    results.append(check_file_exists("src/api_server.py", "API server"))
    results.append(check_file_exists("src/agent_graph.py", "Agent graph"))
    results.append(check_file_exists("src/database/", "Database module"))
    results.append(check_file_exists("src/services/", "Services module"))
    results.append(check_file_exists("src/skills/", "Skills module"))
    
    # 3. Kiểm tra syntax Python
    print("\n🐍 Kiểm tra syntax Python...")
    python_files = [
        ("src/config.py", "Config"),
        ("src/api_server.py", "API Server"),
        ("src/agent_graph.py", "Agent Graph"),
        ("src/database/session.py", "Database Session"),
        ("src/database/models.py", "Database Models"),
        ("src/services/audit.py", "Audit Service"),
        ("src/run_server.py", "Server Runner"),
    ]
    
    for filepath, description in python_files:
        if os.path.exists(filepath):
            results.append(check_python_syntax(filepath, description))
    
    # 4. Kiểm tra JSON configs
    print("\n📄 Kiểm tra JSON configs...")
    json_files = [
        ("mcp_servers_config.json", "MCP Servers"),
    ]
    
    for filepath, description in json_files:
        if os.path.exists(filepath):
            results.append(check_json_valid(filepath, description))
    
    # 5. Kiểm tra config logic
    print("\n⚙️ Kiểm tra config logic...")
    results.append(validate_config())
    
    # 6. Kiểm tra Docker setup
    print("\n🐳 Kiểm tra Docker setup...")
    if os.path.exists("docker-compose.yml"):
        try:
            with open("docker-compose.yml", 'r') as f:
                content = f.read()
            
            required_services = ['postgres', 'redis', 'app', 'nginx']
            missing_services = []
            
            for service in required_services:
                if service not in content:
                    missing_services.append(service)
            
            if missing_services:
                print(f"❌ Docker Compose thiếu services: {', '.join(missing_services)}")
                results.append(False)
            else:
                print("✓ Docker Compose có đầy đủ services")
                results.append(True)
                
        except Exception as e:
            print(f"❌ Docker Compose lỗi: {e}")
            results.append(False)
    
    # Tổng kết
    print("\n" + "=" * 60)
    success_count = sum(results)
    total_count = len(results)
    
    print(f"Kết quả: {success_count}/{total_count} kiểm tra thành công")
    
    if success_count == total_count:
        print("🎉 Dự án Phil-CLI đã sẵn sàng!")
        print("\nTiếp theo:")
        print("1. Copy .env.example thành .env và chỉnh sửa")
        print("2. Chạy: docker-compose up -d")
        print("3. Truy cập: http://localhost:8080")
    else:
        print("⚠️  Cần khắc phục các lỗi trước khi chạy")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)