FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    curl wget git build-essential \
    nodejs npm \
    golang-go \
    rustc cargo \
    ffmpeg \
    zip unzip \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirement.txt .

RUN pip3 install --no-cache-dir -r requirement.txt

WORKDIR /workspace
RUN mkdir -p /workspace/users /workspace/skills

CMD ["tail", "-f", "/dev/null"]