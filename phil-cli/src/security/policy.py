"""
Security Policy Module cho Phil-CLI
Quản lý MCP tool restrictions và content filtering
"""

import re
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Mức độ bảo mật cho MCP tools"""
    LOW = "low"      # Cho phép hầu hết tools
    MEDIUM = "medium"  # Giới hạn một số tools nguy hiểm
    HIGH = "high"     # Chỉ cho phép tools an toàn
    CRITICAL = "critical"  # Chỉ cho phép read-only operations

class SecurityPolicy:
    """Quản lý security policies cho Phil-CLI"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.security_level = SecurityLevel(config.get("security_level", "high"))
        self.content_filters = config.get("content_filters", {})
        self.tool_restrictions = config.get("tool_restrictions", {})
        self.allowed_domains = set(config.get("allowed_domains", []))
        self.blocked_domains = set(config.get("blocked_domains", []))
        
        # Initialize default policies based on security level
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Khởi tạo default policies theo security level"""
        if self.security_level == SecurityLevel.HIGH:
            self._setup_high_security_policies()
        elif self.security_level == SecurityLevel.MEDIUM:
            self._setup_medium_security_policies()
        elif self.security_level == SecurityLevel.CRITICAL:
            self._setup_critical_security_policies()
        else:  # LOW
            self._setup_low_security_policies()
    
    def _setup_high_security_policies(self):
        """Setup policies cho HIGH security level"""
        # Block filesystem write/delete operations
        self.blocked_tools = {
            "filesystem": ["write_file", "delete_file", "create_directory", "delete_directory"],
            "shell": ["execute", "spawn_process"],
            "network": ["download_file", "upload_file", "raw_request"],
            "system": ["execute_command", "modify_permissions"]
        }
        
        # Content filtering
        self.content_filters = {
            "max_prompt_length": 10000,
            "max_response_length": 50000,
            "block_patterns": [
                r"password\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"api[_-]?key\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"secret\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"token\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card numbers
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  # Email addresses
            ]
        }
        
        # Domain restrictions
        self.allowed_domains = {
            "localhost", "127.0.0.1", "::1",
            "github.com", "pypi.org", "python.org",
            "docs.python.org", "stackoverflow.com"
        }
    
    def _setup_medium_security_policies(self):
        """Setup policies cho MEDIUM security level"""
        self.blocked_tools = {
            "filesystem": ["delete_file", "delete_directory"],
            "shell": ["spawn_process"],
            "network": ["raw_request"],
            "system": ["modify_permissions"]
        }
        
        self.content_filters = {
            "max_prompt_length": 20000,
            "max_response_length": 100000,
            "block_patterns": [
                r"password\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"api[_-]?key\s*[:=]\s*['\"]?[^'\"]+['\"]?"
            ]
        }
        
        self.allowed_domains = set()  # Allow most domains
        self.blocked_domains = {"malicious-site.com", "phishing-site.net"}
    
    def _setup_critical_security_policies(self):
        """Setup policies cho CRITICAL security level"""
        # Only allow read-only operations
        self.blocked_tools = {
            "filesystem": ["write_file", "delete_file", "create_directory", "delete_directory", "edit_file"],
            "shell": ["execute", "spawn_process"],
            "network": ["download_file", "upload_file", "raw_request"],
            "system": ["execute_command", "modify_permissions"],
            "database": ["write", "update", "delete"]
        }
        
        self.content_filters = {
            "max_prompt_length": 5000,
            "max_response_length": 20000,
            "block_patterns": [
                r"password\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"api[_-]?key\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"secret\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"token\s*[:=]\s*['\"]?[^'\"]+['\"]?",
                r"\b\d+\b"  # Block numbers (very restrictive)
            ]
        }
        
        self.allowed_domains = {"localhost", "127.0.0.1"}
    
    def _setup_low_security_policies(self):
        """Setup policies cho LOW security level"""
        self.blocked_tools = {
            "system": ["modify_permissions", "format_disk"]
        }
        
        self.content_filters = {
            "max_prompt_length": 50000,
            "max_response_length": 200000,
            "block_patterns": [
                r"password\s*[:=]\s*['\"]?[^'\"]+['\"]?"
            ]
        }
        
        self.allowed_domains = set()  # Allow all domains
        self.blocked_domains = set()
    
    def validate_tool_request(self, tool_name: str, tool_category: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MCP tool request"""
        # Check if tool category is blocked
        if tool_category in self.blocked_tools:
            if tool_name in self.blocked_tools[tool_category]:
                return {
                    "allowed": False,
                    "reason": f"Tool '{tool_name}' in category '{tool_category}' is blocked by security policy",
                    "security_level": self.security_level.value
                }
        
        # Additional parameter validation
        if not self._validate_tool_parameters(tool_name, parameters):
            return {
                "allowed": False,
                "reason": "Tool parameters failed security validation",
                "security_level": self.security_level.value
            }
        
        return {
            "allowed": True,
            "reason": "Tool request approved",
            "security_level": self.security_level.value
        }
    
    def _validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate tool parameters"""
        # Check for suspicious patterns in parameters
        param_str = str(parameters).lower()
        
        # Block suspicious file paths
        suspicious_paths = ["/etc/passwd", "/etc/shadow", "/root", "~/.ssh"]
        for path in suspicious_paths:
            if path in param_str:
                logger.warning(f"Blocked suspicious path in parameters: {path}")
                return False
        
        # Block suspicious URLs
        if "http" in param_str:
            if not self._validate_url_parameters(parameters):
                return False
        
        return True
    
    def _validate_url_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate URL parameters"""
        import urllib.parse
        
        # Extract URLs from parameters
        urls = []
        for key, value in parameters.items():
            if isinstance(value, str) and (value.startswith("http://") or value.startswith("https://")):
                urls.append(value)
        
        for url in urls:
            try:
                parsed = urllib.parse.urlparse(url)
                domain = parsed.netloc.lower()
                
                # Check blocked domains
                for blocked in self.blocked_domains:
                    if blocked in domain:
                        logger.warning(f"Blocked access to domain: {domain}")
                        return False
                
                # Check allowed domains (if whitelist is enabled)
                if self.allowed_domains and domain not in self.allowed_domains:
                    logger.warning(f"Domain not in allowed list: {domain}")
                    return False
                    
            except Exception as e:
                logger.warning(f"Error parsing URL {url}: {str(e)}")
                return False
        
        return True
    
    def filter_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """Filter content based on security policies"""
        # Length filtering
        max_length = self.content_filters.get(f"max_{content_type}_length", 10000)
        if len(content) > max_length:
            return {
                "allowed": False,
                "reason": f"Content exceeds maximum length of {max_length} characters",
                "filtered_content": content[:max_length] + "... [truncated]"
            }
        
        # Pattern filtering
        block_patterns = self.content_filters.get("block_patterns", [])
        for pattern in block_patterns:
            try:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(f"Blocked content matching pattern: {pattern}")
                    return {
                        "allowed": False,
                        "reason": "Content matches blocked pattern",
                        "pattern": pattern
                    }
            except re.error as e:
                logger.error(f"Invalid regex pattern {pattern}: {str(e)}")
        
        return {
            "allowed": True,
            "reason": "Content passed security filters",
            "filtered_content": content
        }
    
    def audit_log(self, action: str, details: Dict[str, Any], user_id: str = "system") -> None:
        """Log security events"""
        audit_entry = {
            "timestamp": self._get_timestamp(),
            "user_id": user_id,
            "action": action,
            "details": details,
            "security_level": self.security_level.value
        }
        
        # In production, this would write to a secure audit log
        logger.info(f"SECURITY_AUDIT: {json.dumps(audit_entry)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of current security policies"""
        return {
            "security_level": self.security_level.value,
            "blocked_tool_categories": list(self.blocked_tools.keys()),
            "blocked_tools_count": sum(len(tools) for tools in self.blocked_tools.values()),
            "content_filters": {
                "max_prompt_length": self.content_filters.get("max_prompt_length", 0),
                "max_response_length": self.content_filters.get("max_response_length", 0),
                "block_patterns_count": len(self.content_filters.get("block_patterns", []))
            },
            "domain_restrictions": {
                "allowed_domains_count": len(self.allowed_domains),
                "blocked_domains_count": len(self.blocked_domains)
            }
        }

# Global security policy instance
_security_policy: Optional[SecurityPolicy] = None

def get_security_policy(config: Optional[Dict[str, Any]] = None) -> SecurityPolicy:
    """Get global security policy instance"""
    global _security_policy
    
    if _security_policy is None:
        if config is None:
            # Import config if not provided
            from src.config import Config
            config = Config.get_security_config()
        
        _security_policy = SecurityPolicy(config)
    
    return _security_policy

def validate_tool_access(tool_name: str, tool_category: str, parameters: Dict[str, Any], user_id: str = "system") -> Dict[str, Any]:
    """Validate tool access request"""
    policy = get_security_policy()
    result = policy.validate_tool_request(tool_name, tool_category, parameters)
    
    # Audit the request
    policy.audit_log("tool_access_request", {
        "tool_name": tool_name,
        "tool_category": tool_category,
        "parameters": parameters,
        "result": result
    }, user_id)
    
    return result

def filter_content_security(content: str, content_type: str = "text", user_id: str = "system") -> Dict[str, Any]:
    """Filter content for security"""
    policy = get_security_policy()
    result = policy.filter_content(content, content_type)
    
    if not result["allowed"]:
        policy.audit_log("content_blocked", {
            "content_type": content_type,
            "reason": result["reason"],
            "content_preview": content[:100] + "..." if len(content) > 100 else content
        }, user_id)
    
    return result