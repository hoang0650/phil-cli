# Chỉ cần Python, không cần CUDA vì Logic chạy ở đây, Model chạy ở Runpod
FROM python:3.10-slim

WORKDIR /app

# Cài đặt các tool hệ thống cần thiết cho MCP (Nodejs cho Zalo/FB) và Audio
RUN apt-get update && apt-get install -y \
    nodejs npm \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt
COPY requirement.txt .
# Loại bỏ unsloth khỏi requirement vì Railway không có GPU để build nó
RUN sed -i '/unsloth/d' requirement.txt && \
    pip install --no-cache-dir -r requirement.txt

# Copy toàn bộ mã nguồn
COPY . .

# Mở port cho Streamlit
EXPOSE 8501

# Lệnh chạy mặc định
CMD ["streamlit", "run", "ui/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]