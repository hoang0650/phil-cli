FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    nodejs npm \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt .

RUN sed -i '/unsloth/d' requirement.txt && \
    pip install --no-cache-dir -r requirement.txt

# Copy toàn bộ mã nguồn
COPY . .

# Mở port cho Streamlit
EXPOSE 8501

# Lệnh chạy mặc định
CMD ["streamlit", "run", "ui/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]