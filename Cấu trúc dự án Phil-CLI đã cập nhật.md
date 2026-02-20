# Cấu trúc dự án Phil-CLI đã cập nhật

Dưới đây là cấu trúc thư mục đầy đủ của dự án `phil-cli` sau khi được cập nhật và mở rộng, bao gồm cả các file mới đã được thêm vào:

```
PHIL-CLI/
├── .env.example                # Mẫu cấu hình môi trường
├── .gitignore
├── README.md                   # Tài liệu dự án (Đã cập nhật)
├── docker-compose.yml          # Hạ tầng triển khai (Single Node)
├── deploy_k8s.sh               # Script triển khai K8s
├── requirements.txt            # Thư viện Python cho Server
├── mcp_servers_config.json     # Cấu hình MCP (Zalo, Git...)
│
├── k8s/                        # Cấu hình Kubernetes
│   ├── 01-storage.yaml
│   ├── 02-brains.yaml
│   ├── 03-app.yaml
│   └── 04-ingress.yaml
│
├── nginx/                      # Cấu hình Gateway
│   ├── nginx.conf
│   └── .htpasswd
│
├── sandbox/                    # Môi trường thực thi code
│   └── Dockerfile              # Base Image chung (Sandbox + API)
│
├── package/                    # Client CLI (Gói cài đặt cho User)
│   ├── setup.py
│   ├── requirements.txt
│   ├── README.md
│   └── phil_cli/
│       ├── __init__.py
│       ├── main.py             # Entry point (Typer CLI)
│       ├── api.py              # Requests logic
│       └── config.py           # Local config storage
│
├── src/                        # Mã nguồn Backend Server
│   ├── __init__.py
│   ├── api_server.py           # FastAPI Controller (Main Entry)
│   ├── agent_graph.py          # LangGraph Logic (Bộ não điều phối)
│   ├── mpc_planner.py          # Thuật toán lập kế hoạch
│   │
│   ├── database/               # Database Module
│   │   ├── __init__.py
│   │   ├── session.py          # Kết nối PostgreSQL
│   │   └── models.py           # Định nghĩa User, AuditLog
│   │
│   ├── services/               # Business Logic
│   │   ├── audit.py            # Ghi log kiểm toán
│   │   ├── auth.py             # Xử lý JWT/API Key
│   │   └── automation.py       # [MỚI] Tự động hóa backend
│   │
│   ├── tools/                  # Các công cụ (Tools)
│   │   ├── tools_code.py       # Chạy code trong Sandbox
│   │   ├── tools_project.py    # Xử lý file/zip dự án
│   │   ├── tools_vision.py     # Xử lý ảnh
│   │   ├── tools_audio.py      # Xử lý âm thanh
│   │   └── mcp_wrapper.py      # Kết nối MCP
│   │
│   ├── skills/                 # Quản lý kỹ năng học được
│   │   ├── skills_manager.py
│   │   └── registry.json
│   │   └── manager.py          # [MỚI] Quản lý Skills
│   │
│   ├── gateway/                # [MỚI] Local Gateway Routing
│   │   └── router.py           # [MỚI] Định tuyến WebSocket
│   │
│   ├── channels/               # [MỚI] Quản lý kênh nhắn tin
│   │   └── manager.py          # [MỚI] Quản lý Channels
│   │
│   └── memory/                 # [MỚI] Hệ thống bộ nhớ và phiên
│       └── persistence.py      # [MỚI] Lưu trữ ngữ cảnh và phiên
│
└── workspace/                  # Thư mục dữ liệu động (Mount ra ngoài)
    ├── users/                  # Workspace riêng cho từng user
    ├── skills/                 # Code các skill đã học
    └── models/                 # Cache model HuggingFace

```

## Các file mới được thêm vào:

- `/home/ubuntu/phil-cli/src/gateway/router.py`: Triển khai Local Gateway Routing cơ bản với WebSocket.
- `/home/ubuntu/phil-cli/src/skills/manager.py`: Quản lý và thực thi các kỹ năng (Skills System).
- `/home/ubuntu/phil-cli/src/channels/manager.py`: Quản lý các kênh nhắn tin (Channels for Messaging).
- `/home/ubuntu/phil-cli/src/memory/persistence.py`: Lưu trữ ngữ cảnh và phiên làm việc (Memory & Session Persistence).
- `/home/ubuntu/phil-cli/src/services/automation.py`: Triển khai Automation Backend cơ bản.
- `/home/ubuntu/phil-cli/README.md`: File README.md đã được viết lại hoàn toàn để phản ánh các tính năng và định hướng mới của dự án.

Các thư mục mới được tạo để chứa các file này bao gồm:
- `phil-cli/src/gateway`
- `phil-cli/src/skills`
- `phil-cli/src/channels`
- `phil-cli/src/memory`
- `phil-cli/skills_repository`

Cấu trúc này phản ánh sự chuyển đổi của `phil-cli` thành một **Agent Runtime** toàn diện, tập trung vào khả năng tự chủ, bảo mật và khả năng mở rộng thông qua hệ thống Skills và tích hợp đa kênh.
