_Bản dịch tiếng Việt ở dưới._

# Phil-CLI: The Self-Hosted Agentic AI Runtime

**Phil-CLI** is an open-source, self-hosted AI agent runtime designed for developers and businesses who demand full control, security, and extensibility. It transforms the command line into an intelligent, autonomous interface capable of complex reasoning, multi-step planning, and seamless integration with your digital life.

Built upon the robust foundation of [OpenClaw](https://github.com/openclaw/openclaw), Phil-CLI extends its capabilities to become a true "agent runtime" that doesn't just assist—it **acts**.

## 🌟 Why Choose Phil-CLI?

- **Agentic by Design**: Moves beyond simple command execution. Phil-CLI features a sophisticated planner that enables multi-step task decomposition and autonomous execution.
- **Uncompromised Security**: With a local-first architecture and sandboxed code execution, you maintain complete control over your data and toolchain.
- **Infinitely Extensible**: A powerful **Skills System** allows you to teach the agent new abilities using simple Markdown and Python scripts. The community-driven repository is poised to grow exponentially.
- **Omni-Channel Interaction**: Engage with your agent through various **Messaging Channels** like Telegram, Discord, and Slack, turning conversations into actions.
- **Persistent Memory**: The agent remembers past interactions, maintaining context for more natural and effective long-term collaboration.
- **Automation Backend**: Automate routine tasks like sending emails, managing your calendar, and organizing files with the built-in automation engine.

## 🏗️ Architecture Overview

Phil-CLI is architected as a modular, microservice-oriented system that ensures scalability and maintainability.

| Component | Description | Key Technologies |
| :--- | :--- | :--- |
| **Local Gateway** | Securely routes messages and manages WebSocket connections between channels and the agent. | FastAPI, Nginx |
| **Agent Runtime (Pi)** | The core brain, responsible for planning, reasoning, and orchestrating skill execution. | LangGraph, Python |
| **Skills Engine** | Dynamically loads and executes skills from the repository in a sandboxed environment. | Docker, Python |
| **Messaging Channels** | Adapters that connect the agent to popular messaging platforms. | Webhooks, API Clients |
| **Memory System** | Provides short-term session context and long-term knowledge persistence. | PostgreSQL, Redis |

## 🚀 Getting Started

_(Installation and setup instructions will be detailed here.)_

## 🛠️ Key Features in Detail

### Local Gateway Routing

The gateway acts as the central nervous system, ensuring that all communication is secure and efficiently routed. It supports WebSocket for real-time, bidirectional communication, enabling a responsive user experience.

### The Skills System

This is the heart of Phil-CLI's extensibility. A "skill" is a self-contained module that combines a `SKILL.md` file for documentation and a Python script for execution. This design makes it incredibly easy for anyone to contribute new capabilities.

> **Example Skill**: A skill to fetch the weather might have a Markdown file describing its `city` parameter and a Python script that calls a weather API.

### Channels for Messaging

Break free from the terminal. Phil-CLI can be integrated with your favorite messaging apps, allowing you to delegate tasks and receive updates wherever you are. The system is designed to be easily extended with new channels.

### Memory & Session Persistence

Our memory system gives the agent a sense of history. It can recall previous conversations and completed tasks, making interactions feel more like a partnership than a series of commands.

## 📈 Roadmap

- [ ] **Community Skill Repository**: A public platform for sharing and discovering new skills.
- [ ] **Advanced Code Generation**: Deeper integration with LLMs for on-the-fly tool and script creation.
- [ ] **GUI Control Panel**: A web-based interface for managing the agent, channels, and skills.
- [ ] **Expanded Channel Support**: Adding support for WhatsApp, Microsoft Teams, and more.

## 🤝 Contributing

We welcome contributions from the community! Whether it's building a new skill, adding a channel, or improving the core runtime, your help is invaluable. Please see our contributing guidelines for more details.

---

# Phil-CLI: Nền tảng AI Agent Tự Host

**Phil-CLI** là một nền tảng AI agent (runtime) mã nguồn mở, tự host được thiết kế cho các nhà phát triển và doanh nghiệp yêu cầu sự kiểm soát, bảo mật và khả năng mở rộng toàn diện. Nó biến dòng lệnh thành một giao diện thông minh, tự chủ, có khả năng suy luận phức tạp, lập kế hoạch đa bước và tích hợp liền mạch vào cuộc sống số của bạn.

Được xây dựng trên nền tảng vững chắc của [OpenClaw](https://github.com/openclaw/openclaw), Phil-CLI mở rộng khả năng của mình để trở thành một "agent runtime" thực thụ, không chỉ hỗ trợ—mà còn **hành động**.

## 🌟 Tại sao chọn Phil-CLI?

- **Thiết kế Agentic**: Vượt xa việc thực thi lệnh đơn giản. Phil-CLI có một bộ lập kế hoạch tinh vi cho phép phân rã tác vụ đa bước và thực thi tự chủ.
- **Bảo mật tuyệt đối**: Với kiến trúc ưu tiên cục bộ (local-first) và thực thi mã trong sandbox, bạn duy trì toàn quyền kiểm soát dữ liệu và chuỗi công cụ của mình.
- **Khả năng mở rộng vô hạn**: **Hệ thống Kỹ năng (Skills System)** mạnh mẽ cho phép bạn dạy cho agent những khả năng mới bằng các tập lệnh Markdown và Python đơn giản. Kho lưu trữ do cộng đồng đóng góp sẵn sàng phát triển theo cấp số nhân.
- **Tương tác đa kênh**: Tương tác với agent của bạn thông qua các **Kênh Nhắn tin (Messaging Channels)** khác nhau như Telegram, Discord và Slack, biến các cuộc trò chuyện thành hành động.
- **Bộ nhớ bền vững**: Agent ghi nhớ các tương tác trong quá khứ, duy trì ngữ cảnh để cộng tác lâu dài tự nhiên và hiệu quả hơn.
- **Backend tự động hóa**: Tự động hóa các tác vụ thông thường như gửi email, quản lý lịch và sắp xếp tệp với công cụ tự động hóa tích hợp.

## 🏗️ Tổng quan kiến trúc

Phil-CLI được kiến trúc như một hệ thống mô-đun, hướng vi dịch vụ để đảm bảo khả năng mở rộng và bảo trì.

| Thành phần | Mô tả | Công nghệ chính |
| :--- | :--- | :--- |
| **Local Gateway** | Định tuyến tin nhắn an toàn và quản lý kết nối WebSocket giữa các kênh và agent. | FastAPI, Nginx |
| **Agent Runtime (Pi)** | Bộ não trung tâm, chịu trách nhiệm lập kế hoạch, suy luận và điều phối thực thi kỹ năng. | LangGraph, Python |
| **Skills Engine** | Tải và thực thi động các kỹ năng từ kho lưu trữ trong môi trường sandbox. | Docker, Python |
| **Messaging Channels** | Các bộ điều hợp kết nối agent với các nền tảng nhắn tin phổ biến. | Webhooks, API Clients |
| **Memory System** | Cung cấp ngữ cảnh phiên ngắn hạn và lưu trữ kiến thức dài hạn. | PostgreSQL, Redis |

## 🚀 Bắt đầu

_(Hướng dẫn cài đặt và thiết lập sẽ được trình bày chi tiết ở đây.)_

## 🛠️ Chi tiết các tính năng chính

### Định tuyến Gateway cục bộ

Gateway hoạt động như hệ thần kinh trung ương, đảm bảo mọi giao tiếp đều an toàn và được định tuyến hiệu quả. Nó hỗ trợ WebSocket để giao tiếp hai chiều thời gian thực, cho phép trải nghiệm người dùng nhạy bén.

### Hệ thống Kỹ năng (Skills System)

Đây là trái tim của khả năng mở rộng của Phil-CLI. Một "kỹ năng" là một mô-đun độc lập kết hợp tệp `SKILL.md` để làm tài liệu và một tập lệnh Python để thực thi. Thiết kế này giúp mọi người cực kỳ dễ dàng đóng góp các khả năng mới.

> **Ví dụ về Kỹ năng**: Một kỹ năng để lấy thông tin thời tiết có thể có một tệp Markdown mô tả tham số `city` của nó và một tập lệnh Python gọi API thời tiết.

### Kênh Nhắn tin (Channels for Messaging)

Hãy thoát khỏi terminal. Phil-CLI có thể được tích hợp với các ứng dụng nhắn tin yêu thích của bạn, cho phép bạn giao phó nhiệm vụ và nhận cập nhật mọi lúc mọi nơi. Hệ thống được thiết kế để dễ dàng mở rộng với các kênh mới.

### Bộ nhớ & Lưu trữ phiên

Hệ thống bộ nhớ của chúng tôi mang lại cho agent một cảm giác về lịch sử. Nó có thể nhớ lại các cuộc trò chuyện trước đó và các nhiệm vụ đã hoàn thành, làm cho các tương tác giống như một sự hợp tác hơn là một chuỗi các lệnh.

## 📈 Lộ trình phát triển

- [ ] **Kho Kỹ năng Cộng đồng**: Một nền tảng công khai để chia sẻ và khám phá các kỹ năng mới.
- [ ] **Tạo mã nâng cao**: Tích hợp sâu hơn với các LLM để tạo công cụ và tập lệnh một cách nhanh chóng.
- [ ] **Bảng điều khiển GUI**: Một giao diện dựa trên web để quản lý agent, các kênh và kỹ năng.
- [ ] **Hỗ trợ Kênh mở rộng**: Thêm hỗ trợ cho WhatsApp, Microsoft Teams, và nhiều hơn nữa.

## 🤝 Đóng góp

Chúng tôi hoan nghênh các đóng góp từ cộng đồng! Dù đó là xây dựng một kỹ năng mới, thêm một kênh, hay cải thiện runtime cốt lõi, sự giúp đỡ của bạn là vô giá. Vui lòng xem hướng dẫn đóng góp của chúng tôi để biết thêm chi tiết.
