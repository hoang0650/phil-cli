#!/bin/bash

# Phil AI Agent - Enterprise Setup Script
# © 2026 PHGROUP TECHNOLOGY SOLUTIONS CO., LTD

set -e

echo "------------------------------------------------"
echo "🚀 Khởi tạo hệ thống Phil AI Agent..."
echo "------------------------------------------------"

# 1. Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Lỗi: Không tìm thấy Python3. Vui lòng cài đặt Python 3.10 trở lên."
    exit 1
fi

# 2. Tạo môi trường ảo cho Server
echo "📦 Đang tạo môi trường ảo cho Server..."
python3 -m venv venv_server
source venv_server/bin/activate

# 3. Cài đặt các thư viện cần thiết
echo "📥 Đang cài đặt các thư viện phụ thuộc..."
pip install --upgrade pip
pip install -r requirement.txt

# 4. Cấu hình biến môi trường mẫu
if [ ! -f .env ]; then
    echo "📝 Tạo file cấu hình .env mẫu..."
    cp .env.example .env || {
        echo "CODER_API_BASE=http://localhost:8000/v1" > .env
        echo "VN_API_BASE=http://localhost:8001/v1" >> .env
        echo "API_KEY=phil_admin_secret_$(openssl rand -hex 8)" >> .env
        echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phil_db" >> .env
    }
    echo "⚠️ Vui lòng chỉnh sửa file .env để cấu hình đúng các URL của vLLM."
fi

# 5. Cài đặt CLI Client
echo "💻 Đang cài đặt Phil CLI Client..."
cd phil-cli/package
pip install .
cd ../..

echo "------------------------------------------------"
echo "✅ Cài đặt hoàn tất!"
echo "------------------------------------------------"
echo "Để khởi động Server:"
echo "  source venv_server/bin/activate"
echo "  python3 -m src.api_server"
echo ""
echo "Để sử dụng CLI:"
echo "  phil-cli --help"
echo "------------------------------------------------"