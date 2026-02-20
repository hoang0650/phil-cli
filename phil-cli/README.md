# Phil-CLI - The Self-Hosted Agentic AI Runtime

Phil-CLI là một runtime AI tự chủ (self-hosted) với kiến trúc "Tứ Trụ" (Brain/Vision/Ears/Mouth) và tích hợp Model Context Protocol (MCP), được thiết kế để chạy các tác vụ AI phức tạp một cách an toàn và hiệu quả với sandboxing nâng cao từ openclaw.

## 🧠 Kiến Trúc "Tứ Trụ" (The Big Four)

Phil-CLI sử dụng kiến trúc AI hoàn chỉnh với 4 thành phần cốt lõi từ Phil-AI:

- **Brain**: DeepSeek-R1-Distill-Llama-70B - Tư duy, Code, Logic (thay thế hoàn toàn API bên ngoài)
- **Vision**: InternVL2-76B - Nhìn, OCR, UI/UX (thay thế GPT-4V)
- **Ears**: Whisper-Large-v3 - Nghe thuật ngữ IT (chuyển giọng nói sang văn bản)
- **Mouth**: F5-TTS - Giọng nói định danh (chuyển văn bản sang giọng nói)

## 🛡️ Tính năng bảo mật nâng cao (từ openclaw)

- **Sandbox Container**: Chạy code trong container Docker cô lập với security hardening
- **Security Policy**: Kiểm soát quyền truy cập MCP tools theo cấp độ (high/medium/low)
- **Content Filtering**: Lọc nội dung nhạy cảm trong prompts và responses
- **Audit Logging**: Ghi lại toàn bộ hoạt động để kiểm tra bảo mật
- **Network Isolation**: Container chạy trong môi trường cô lập mạng

## 🏗️ Cấu Trúc Dự Án

```
phil-cli/
├── src/                          # Source code chính
│   ├── api_server.py            # FastAPI server với Phil-AI integration
│   ├── agent_graph.py           # Agent workflow với LangGraph
│   ├── config.py                # Configuration management (cập nhật cho Phil-AI)
│   ├── run_server.py            # Server runner
│   ├── database/                # Database modules
│   │   ├── session.py          # SQLAlchemy sessions
│   │   └── models.py           # Database models
│   ├── services/                # Business services
│   │   └── audit.py            # Audit logging service
│   ├── skills/                  # Skill management
│   │   └── manager.py          # Skill execution manager
│   ├── sandbox/                 # Sandboxing modules (mới)
│   │   └── manager.py          # Container sandbox management
│   ├── security/                # Security modules (mới)
│   │   └── policy.py           # Security policy enforcement
│   └── gateway/                 # Gateway modules (nếu có)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── docker-compose.yml         # Docker services
├── Dockerfile                   # App container
├── mcp_servers_config.json    # MCP servers configuration
└── validate_project.py        # Project validation script
```

## 🚀 Cách Chạy

### 1. Chuẩn Bị Môi Trường

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configurations
# Các biến quan trọng cần cấu hình:
# - DATABASE_URL: PostgreSQL connection string
# - SECRET_KEY: Secret key cho app (tối thiểu 32 ký tự)
# - API_KEY: API key cho services
# - PHIL_AI_GATEWAY_URL: URL của Phil-AI gateway (mới)
# - SANDBOX_ENABLED: Bật/tắt sandbox (mới)
# - SECURITY_LEVEL: Cấp độ bảo mật (high/medium/low) (mới)
```

### 2. Validation Project

Trước khi chạy, kiểm tra project:

```bash
python validate_project.py
```

Script này sẽ kiểm tra:
- ✅ Cấu trúc thư mục
- ✅ File cấu hình
- ✅ Syntax Python
- ✅ JSON configs
- ✅ Docker setup
- ✅ Kết nối Phil-AI models (mới)

### 3. Chạy Với Docker (Khuyến Nghị)

```bash
# Start all services
docker-compose up -d

# Kiểm tra logs
docker-compose logs -f

# Dừng services
docker-compose down
```

Services sẽ chạy:
- **PostgreSQL**: Database chính (port 5432)
- **Redis**: Cache và message broker (port 6379)
- **Phil-AI Models**: Brain (8000), Vision (8001), Ears (8002), Mouth (8003)
- **Phil-CLI App**: Application server (port 8000)
- **Nginx**: Reverse proxy (port 8080)

### 4. Chạy Development Mode (Không Docker)

Nếu không có Docker, cài dependencies và chạy:

```bash
# Cài dependencies
pip install -r requirements.txt

# Chạy validation
cp .env.example .env
# Edit .env với config phù hợp

# Chạy server
python src/run_server.py
```

## 🔧 Cấu Hình

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://phil_user:phil_password@localhost:5432/phil_cli_db` |
| `SECRET_KEY` | App secret key (≥32 chars) | `your-secret-key-here-minimum-32-characters` |
| `API_KEY` | API authentication key | `phil-local-key` |
| `PHIL_AI_GATEWAY_URL` | Phil-AI gateway URL (mới) | `http://localhost:3000` |
| `BRAIN_MODEL_ENDPOINT` | Brain model endpoint (mới) | `http://localhost:8000/v1` |
| `VISION_MODEL_ENDPOINT` | Vision model endpoint (mới) | `http://localhost:8001/v1` |
| `EARS_MODEL_ENDPOINT` | Ears model endpoint (mới) | `http://localhost:8002/v1` |
| `MOUTH_MODEL_ENDPOINT` | Mouth model endpoint (mới) | `http://localhost:8003/v1` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `MCP_SERVERS_CONFIG` | MCP config file path | `./mcp_servers_config.json` |
| `SANDBOX_ENABLED` | Bật sandbox container (mới) | `true` |
| `SECURITY_LEVEL` | Cấp độ bảo mật (mới) | `high` |

### MCP Servers Configuration

Xem `mcp_servers_config.json` để cấu hình các MCP servers:

- **filesystem**: File system access (có thể bị chặn ở security level cao)
- **git**: Git operations
- **sqlite**: Database operations
- **slack/telegram**: Messaging platforms
- **web-browser**: Browser automation

**Lưu ý**: Security policy sẽ kiểm soát quyền truy cập các tools dựa trên cấp độ bảo mật.

## 🧪 Testing

### Validation Script

```bash
# Kiểm tra toàn bộ project
python validate_project.py

# Test kết nối Phil-AI models
python test_phil_ai_connection.py

# Test sandbox functionality
python test_sandbox.py
```

### API Testing

Sau khi khởi động, truy cập:
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **Security Status**: http://localhost:8080/v1/security/status (mới)
- **Sandbox Test**: http://localhost:8080/v1/sandbox/execute (mới)

## 🔍 Troubleshooting

### Lỗi Kết Nối Phil-AI

1. Kiểm tra Phil-AI services đang chạy: `docker ps`
2. Test kết nối từng model: `curl http://localhost:8000/v1/models`
3. Kiểm tra logs của Phil-AI containers

### Lỗi Sandboxing

1. Kiểm tra Docker daemon đang chạy
2. Kiểm tra quyền Docker: `docker run hello-world`
3. Xem security logs: `docker-compose logs security`

### Lỗi Import Python

Nếu gặp lỗi import:
1. Kiểm tra Python version (≥3.8)
2. Cài dependencies: `pip install -r requirements.txt`
3. Chạy validation script để kiểm tra

### Lỗi Docker

1. Kiểm tra Docker và Docker Compose đã cài đặt
2. Chắc chắn ports 5432, 6379, 8000, 8080 không bị chiếm
3. Kiểm tra logs: `docker-compose logs -f [service-name]`

### Lỗi Database

1. Kiểm tra PostgreSQL connection string trong `.env`
2. Chắc chắn database đã tồn tại hoặc được tạo tự động
3. Kiểm tra credentials trong docker-compose.yml

## 📚 Architecture Documentation

Xem thêm chi tiết kiến trúc trong các file:
- `Cấu trúc dự án Phil-CLI đã cập nhật.md`
- `Phil-CLI_ The Self-Hosted Agentic AI Runtime.md`

## 🤝 Contributing

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push branch: `git push origin feature/your-feature`
5. Tạo Pull Request

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## 🔗 Links

- **Documentation**: [Link docs]
- **Issues**: [GitHub Issues]
- **Discussions**: [GitHub Discussions]
- **Phil-AI**: [Phil-AI Repository]

---

**Lưu ý**: Đây là project tự chủ (self-hosted) với bảo mật nâng cao. Đảm bảo bạn đã cấu hình bảo mật phù hợp khi deploy trong môi trường production. Không sử dụng API bên ngoài - tất cả models đều được tự train và host locally.