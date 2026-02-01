# 🤖 Phil AI Agent (phil-cli)

**Phil Agentic AI System** - Hệ thống AI Tự chủ Đa phương thức (Multimodal), có khả năng Nghe, Nói, Nhìn, Lập trình và Tự học.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![GPU](https://img.shields.io/badge/GPU-NVIDIA_A100-green)

## 📖 Giới thiệu

**Phil AI Agent** là một tác nhân AI toàn năng được thiết kế để chạy **Self-hosted** (tự lưu trữ), đảm bảo quyền riêng tư tuyệt đối và khả năng mở rộng không giới hạn thông qua giao thức MCP (Model Context Protocol).

Hệ thống hoạt động dựa trên kiến trúc **Dual-Brain**:
1.  **🛡️ Security Layer (The Gatekeeper):**
    * **Nginx Gateway:** Quản lý lưu lượng, Rate Limiting (chống DDoS), Routing và SSL Termination.
    * **Isolation:** Mỗi người dùng có không gian Workspace riêng biệt, đảm bảo dữ liệu không bị lộ.

2.  **🧠 The Dual-Brain Core:**
    * **Logic Engine:** `Llama-3-70B-Instruct` (AWQ) - Xử lý tư duy phức tạp, MPC Planning.
    * **Language Soul:** `PhoGPT-4B` - Chuyên trách văn hóa và ngôn ngữ Tiếng Việt.

3.  **👁️👂🗣️ Sensory Modules:**
    * **Vision:** `Qwen2-VL` (OCR & Image Understanding).
    * **Hearing:** `Faster-Whisper Large-v3` (High-fidelity STT).
    * **Speech:** `XTTS-v2` (Multilingual TTS with Voice Cloning).

4.  **🔌 Expansion & Action:**
    * **MCP Protocol:** Kết nối Telegram, Discord, Zalo (Puppeteer), Git, Database.
    * **Docker Sandbox:** Môi trường thực thi code an toàn.

---

## 📂 Cấu trúc dự án

```text
phil-cli/
├── nginx/                   # API Gateway & Security
│   ├── nginx.conf           # Cấu hình chặn cửa, SSL, Rate limit
│   └── .htpasswd            # (Tùy chọn) Danh sách user hợp lệ
├── docker-compose.yml       # Hạ tầng 5 Model AI (Brain, Eyes, Ears, Mouth)
├── mcp_servers_config.json  # Cấu hình kết nối công cụ mở rộng
├── src/                     # Mã nguồn Core Logic
│   ├── agent_graph.py       # Bộ não trung tâm (LangGraph)
│   ├── mpc_planner.py       # Thuật toán lập kế hoạch
│   └── tools_*.py           # Các module chức năng
├── skills/                  # Kho kỹ năng Agent tự học
├── sandbox/                 # Môi trường thực thi code
├── ui/                      # Giao diện Web (Streamlit)
├── cli.py                   # Giao diện dòng lệnh (Terminal)
└── training/                # Module tự học (Fine-tuning)
```

## 🚀 Tính Năng Nổi Bật

| Tính năng | Mô tả |
| :--- | :--- |
| **Global Scalability** | Hỗ trợ phục vụ đồng thời nhiều user nhờ Nginx Load Balancing và Async Queue. |
| **Model Predictive Control** | Sử dụng thuật toán MPC để lập kế hoạch nhiều bước (Thinking -> Planning -> Coding -> Review). |
| **Coding Master** | Tự động viết, chạy, debug code Python/Bash trong Sandbox bị cô lập. |
| **Full Multimodal** | Nghe giọng nói, nhìn hình ảnh/tài liệu và phản hồi bằng giọng nói tự nhiên. |
| **Self-Evolution** | Tự động fine-tune model (Unsloth) sau mỗi chu kỳ hoạt động để thông minh hơn. |

---

## Cài đặt

### 1. Yêu cầu phần cứng

* **Server:** GPU Cluster (Runpod/AWS/GCP) với tối thiểu 1x A100 (80GB VRAM) hoặc 2x A6000.
* **Storage:** 200GB SSD.
* **Docker & Docker Compose.**

### Bước 1: Thiết lập Môi trường
```bash
# Clone repository
git clone [https://github.com/your-repo/phil-cli.git](https://github.com/your-repo/phil-cli.git)
cd phil-cli

# Cấu hình biến môi trường (Bảo mật)
cp .env.example .env
# Chỉnh sửa .env: Thêm API Keys, Tokens cho Telegram/Discord
```

### Bước 2: Khởi động Hệ thống (Backend)

```bash
# Chạy hạ tầng AI & Gateway bảo mật
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps
```
Lúc này, hệ thống sẽ ẩn toàn bộ port 8000-8004 và chỉ mở port **80 (HTTP)** hoặc **443 (HTTPS).**

### Bước 3: Client Connection
Bạn có thể kết nối với Phil thông qua 3 giao diện:
1. **CLI (Terminal):** Dành cho Developer.
```bash
python cli.py --user="admin"
```
2. **Web UI (Streamlit):** Dành cho End-user.
```bash
streamlit run ui/app.py
```
3. **API Integration:** Tích hợp vào Mobile App hoặc Website khác.
Endpoint: `http://your-server-ip/api/coder/v1/chat/completions`

---

### 🔌 Mở rộng (MCP)
Để kết nối thêm công cụ (ví dụ: Google Drive, Slack), hãy chỉnh sửa file `mcp_servers_config.json`:

```bash
"gdrive": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-gdrive"]
}
```

### 🔒 Bảo Mật & Multi-tenancy
Để phục vụ toàn cầu, hệ thống áp dụng các quy chuẩn:
* **API Key Authentication:** Mọi request phải có Header Authorization.

* **Rate Limiting**: Giới hạn 60 requests/phút mỗi user để bảo vệ GPU.

* **Sandboxing:** Code của user A chạy trong container tách biệt với user B (Cần cấu hình Kubernetes cho Production).


### 🤝 Đóng Góp (Contributing)
Dự án Phil AI Agent là mã nguồn mở. Chúng tôi chào đón mọi đóng góp về:

* Tối ưu hóa MPC Planner.

* Thêm MCP Server mới (Notion, Slack...).

* Cải thiện bộ dataset Tiếng Việt cho PhoGPT.

### 📜 License
MIT License. Created by PHGroup.
```bash
### Tóm tắt thay đổi
1.  **Thêm Nginx Gateway:** Bảo vệ các model AI, không cho truy cập trực tiếp.
2.  **Cập nhật Docker Compose:** Ẩn port nội bộ, chỉ expose port Gateway.
3.  **README:** Viết lại theo hướng Enterprise/SaaS, nhấn mạnh bảo mật và khả năng mở rộng.
---