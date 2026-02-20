import os
import json
from typing import Dict, Any, Optional

# Tải biến môi trường từ file .env (nếu có)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Không có dotenv thì bỏ qua

class Config:
    """Configuration cho Phil-CLI với tích hợp Phil-AI models và sandboxing"""
    
    # PHIL-AI Model Configuration - Sử dụng models tự train thay vì external APIs
    PHIL_AI_GATEWAY_URL = os.getenv("PHIL_AI_GATEWAY_URL", "http://phil-ai-gateway:8000")
    
    # Brain Model (Logic Engine) - Thay thế Llama-3-70B-Instruct
    BRAIN_MODEL_ENDPOINT = os.getenv("BRAIN_MODEL_ENDPOINT", "http://phil-ai-gateway:8000/v1")
    BRAIN_MODEL_NAME = os.getenv("BRAIN_MODEL_NAME", "Phil-70B-Coder-N1")
    
    # Vision Model (Eyes) - Thay thế các vision APIs
    VISION_MODEL_ENDPOINT = os.getenv("VISION_MODEL_ENDPOINT", "http://phil-ai-gateway:8000/v1")
    VISION_MODEL_NAME = os.getenv("VISION_MODEL_NAME", "Phil-InternVL2-76B-N1")
    
    # Audio Models (Ears & Mouth) - Tích hợp voice capabilities
    WHISPER_ENDPOINT = os.getenv("WHISPER_ENDPOINT", "http://phil-ai-gateway:8000/v1")
    TTS_ENDPOINT = os.getenv("TTS_ENDPOINT", "http://phil-ai-gateway:8000/v1")
    
    # Local Model Configuration - Tự chủ hoàn toàn
    USE_LOCAL_MODELS = os.getenv("USE_LOCAL_MODELS", "true").lower() == "true"
    LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "./models")
    
    # Security & Sandboxing Configuration - Từ openclaw
    SANDBOX_ENABLED = os.getenv("SANDBOX_ENABLED", "true").lower() == "true"
    SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "debian:bookworm-slim")
    SANDBOX_USER = os.getenv("SANDBOX_USER", "sandbox")
    SANDBOX_WORKSPACE = os.getenv("SANDBOX_WORKSPACE", "/home/sandbox/workspace")
    SANDBOX_MEMORY_LIMIT = os.getenv("SANDBOX_MEMORY_LIMIT", "1g")
    SANDBOX_CPU_LIMIT = os.getenv("SANDBOX_CPU_LIMIT", "1")
    
    # Container Security
    CONTAINER_SECURITY_OPTS = [
        "--cap-drop=ALL",           # Drop all capabilities
        "--security-opt=no-new-privileges",  # No new privileges
        "--read-only",              # Read-only root filesystem
        "--tmpfs=/tmp:rw,noexec,nosuid,size=100m",  # Tmpfs with restrictions
    ]
    
    # Network Security
    NETWORK_ISOLATION = os.getenv("NETWORK_ISOLATION", "true").lower() == "true"
    ALLOWED_PORTS = os.getenv("ALLOWED_PORTS", "8000,8001,8002,8003").split(",")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://phil_user:phil_password@localhost:5432/phil_cli_db")
    
    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-minimum-32-characters")
    API_KEY_NAME = os.getenv("API_KEY_NAME", "X-API-Key")
    API_KEY = os.getenv("API_KEY", "phil-local-key")
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8080"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Docker Configuration
    DOCKER_HOST = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
    
    # MCP Configuration
    MCP_SERVERS_CONFIG = os.getenv("MCP_SERVERS_CONFIG", "mcp_servers_config.json")
    
    # Workspace Configuration
    WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", "./workspace")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Model Context Protocol (MCP) Security
    MCP_SECURITY_LEVEL = os.getenv("MCP_SECURITY_LEVEL", "high")  # low, medium, high
    MCP_ALLOWED_TOOLS = os.getenv("MCP_ALLOWED_TOOLS", "").split(",") if os.getenv("MCP_ALLOWED_TOOLS") else []
    MCP_BLOCKED_TOOLS = os.getenv("MCP_BLOCKED_TOOLS", "filesystem:write,filesystem:delete").split(",")
    
    # Audit & Monitoring
    AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "true").lower() == "true"
    AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "30"))
    
    # Content Filtering
    CONTENT_FILTER_ENABLED = os.getenv("CONTENT_FILTER_ENABLED", "true").lower() == "true"
    MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "10000"))
    MAX_RESPONSE_LENGTH = int(os.getenv("MAX_RESPONSE_LENGTH", "50000"))
    
    @staticmethod
    def get_model_config() -> Dict[str, Any]:
        """Lấy config cho Phil-AI models"""
        return {
            "brain": {
                "endpoint": Config.BRAIN_MODEL_ENDPOINT,
                "model_name": Config.BRAIN_MODEL_NAME,
                "use_local": Config.USE_LOCAL_MODELS,
                "local_path": os.path.join(Config.LOCAL_MODEL_PATH, "brain")
            },
            "vision": {
                "endpoint": Config.VISION_MODEL_ENDPOINT,
                "model_name": Config.VISION_MODEL_NAME,
                "use_local": Config.USE_LOCAL_MODELS,
                "local_path": os.path.join(Config.LOCAL_MODEL_PATH, "vision")
            },
            "audio": {
                "whisper_endpoint": Config.WHISPER_ENDPOINT,
                "tts_endpoint": Config.TTS_ENDPOINT
            }
        }
    
    @staticmethod
    def get_sandbox_config() -> Dict[str, Any]:
        """Lấy config cho sandboxing"""
        return {
            "enabled": Config.SANDBOX_ENABLED,
            "image": Config.SANDBOX_IMAGE,
            "user": Config.SANDBOX_USER,
            "workspace": Config.SANDBOX_WORKSPACE,
            "memory_limit": Config.SANDBOX_MEMORY_LIMIT,
            "cpu_limit": Config.SANDBOX_CPU_LIMIT,
            "security_opts": Config.CONTAINER_SECURITY_OPTS,
            "network_isolation": Config.NETWORK_ISOLATION,
            "allowed_ports": Config.ALLOWED_PORTS
        }
    
    @staticmethod
    def get_security_config() -> Dict[str, Any]:
        """Lấy config cho security features"""
        return {
            "content_filter": {
                "enabled": Config.CONTENT_FILTER_ENABLED,
                "max_prompt_length": Config.MAX_PROMPT_LENGTH,
                "max_response_length": Config.MAX_RESPONSE_LENGTH
            },
            "mcp_security": {
                "level": Config.MCP_SECURITY_LEVEL,
                "allowed_tools": Config.MCP_ALLOWED_TOOLS,
                "blocked_tools": Config.MCP_BLOCKED_TOOLS
            },
            "audit": {
                "enabled": Config.AUDIT_ENABLED,
                "retention_days": Config.AUDIT_RETENTION_DAYS
            }
        }
    
    @staticmethod
    def validate():
        """Kiểm tra các cấu hình bắt buộc"""
        missing = []
        errors = []
        
        if not Config.DATABASE_URL:
            missing.append("DATABASE_URL")
        
        if not Config.SECRET_KEY or len(Config.SECRET_KEY) < 32:
            missing.append("SECRET_KEY (minimum 32 characters)")
        
        if not Config.API_KEY:
            missing.append("API_KEY")
        
        # Validate model endpoints
        if Config.USE_LOCAL_MODELS and not os.path.exists(Config.LOCAL_MODEL_PATH):
            try:
                os.makedirs(Config.LOCAL_MODEL_PATH, exist_ok=True)
            except Exception as e:
                errors.append(f"Không thể tạo LOCAL_MODEL_PATH: {e}")
        
        # Validate sandbox configuration
        if Config.SANDBOX_ENABLED:
            if not Config.SANDBOX_IMAGE:
                missing.append("SANDBOX_IMAGE")
            if not Config.SANDBOX_USER:
                missing.append("SANDBOX_USER")
        
        validation_result = len(missing) == 0 and len(errors) == 0
        error_message = ""
        
        if missing:
            error_message += f"Thiếu cấu hình: {', '.join(missing)}"
        if errors:
            if error_message:
                error_message += "; "
            error_message += f"Lỗi: {', '.join(errors)}"
        
        return validation_result, error_message or "OK"