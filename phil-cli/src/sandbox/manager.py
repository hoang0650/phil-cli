"""
Sandbox Management Module cho Phil-CLI
Dựa trên openclaw sandbox architecture với tính năng bảo mật nâng cao
"""

import os
import json
import subprocess
import tempfile
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SandboxManager:
    """Quản lý sandbox containers với security hardening"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.image = config.get("image", "debian:bookworm-slim")
        self.user = config.get("user", "sandbox")
        self.workspace = config.get("workspace", "/home/sandbox/workspace")
        self.memory_limit = config.get("memory_limit", "1g")
        self.cpu_limit = config.get("cpu_limit", "1")
        self.security_opts = config.get("security_opts", [])
        self.network_isolation = config.get("network_isolation", True)
        self.allowed_ports = config.get("allowed_ports", [])
        
        # Container tracking
        self.active_containers: Dict[str, Dict[str, Any]] = {}
        
    def create_sandbox(self, session_id: str, task_type: str = "general") -> Dict[str, Any]:
        """Tạo sandbox container với security hardening"""
        if not self.enabled:
            return {"status": "disabled", "message": "Sandboxing is disabled"}
        
        try:
            # Generate unique container name
            container_name = f"phil-sandbox-{session_id}-{uuid.uuid4().hex[:8]}"
            
            # Prepare volume mounts
            workspace_host = tempfile.mkdtemp(prefix=f"phil_workspace_{session_id}_")
            
            # Build docker command
            cmd = [
                "docker", "run", "-d", "--rm",
                "--name", container_name,
                "--memory", self.memory_limit,
                "--cpus", self.cpu_limit,
                "--user", f"{self.user}:{self.user}",
                "-v", f"{workspace_host}:{self.workspace}",
                "-w", self.workspace,
            ]
            
            # Add security options
            for opt in self.security_opts:
                cmd.extend(["--security-opt", opt])
            
            # Network isolation
            if self.network_isolation:
                cmd.extend(["--network", "none"])
            else:
                # Limited network access
                cmd.extend(["--network", "bridge"])
                if self.allowed_ports:
                    for port in self.allowed_ports:
                        cmd.extend(["-p", f"{port}:{port}"])
            
            # Add image
            cmd.append(self.image)
            cmd.extend(["sleep", "infinity"])
            
            # Create container
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            container_id = result.stdout.strip()
            
            # Setup user and workspace
            self._setup_container_user(container_id)
            
            sandbox_info = {
                "container_id": container_id,
                "container_name": container_name,
                "session_id": session_id,
                "workspace_host": workspace_host,
                "workspace_container": self.workspace,
                "task_type": task_type,
                "created_at": self._get_timestamp(),
                "status": "running"
            }
            
            self.active_containers[container_id] = sandbox_info
            logger.info(f"Created sandbox container: {container_name}")
            
            return sandbox_info
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to create sandbox: {e.stderr}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error creating sandbox: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _setup_container_user(self, container_id: str):
        """Setup user trong container"""
        try:
            # Create user
            subprocess.run([
                "docker", "exec", container_id,
                "useradd", "--create-home", "--shell", "/bin/bash", self.user
            ], check=True, capture_output=True)
            
            # Setup workspace
            subprocess.run([
                "docker", "exec", container_id,
                "mkdir", "-p", self.workspace
            ], check=True, capture_output=True)
            
            # Set permissions
            subprocess.run([
                "docker", "exec", container_id,
                "chown", "-R", f"{self.user}:{self.user}", self.workspace
            ], check=True, capture_output=True)
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not setup container user: {e.stderr}")
    
    def execute_command(self, container_id: str, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Thực thi command trong sandbox"""
        if not self.enabled:
            return {"status": "disabled", "message": "Sandboxing is disabled"}
        
        if container_id not in self.active_containers:
            return {"status": "error", "message": "Container not found"}
        
        try:
            # Validate command against security policies
            if not self._validate_command(command):
                return {
                    "status": "blocked",
                    "message": "Command blocked by security policy",
                    "command": command
                }
            
            # Execute command as sandbox user
            cmd = [
                "docker", "exec",
                "--user", self.user,
                container_id,
                "timeout", str(timeout),
                "bash", "-c", command
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
            
            return {
                "status": "success",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": f"Command timed out after {timeout}s"}
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _validate_command(self, command: str) -> bool:
        """Validate command against security policies"""
        # Block dangerous commands
        dangerous_patterns = [
            "rm -rf /", "dd if=", "mkfs", "fdisk", "sudo", "su ",
            "wget", "curl", "nc ", "netcat", "ssh", "scp",
            "systemctl", "service", "init", "reboot", "shutdown",
            "mount", "umount", "insmod", "rmmod"
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                logger.warning(f"Blocked dangerous command pattern: {pattern}")
                return False
        
        return True
    
    def get_container_info(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin container"""
        return self.active_containers.get(container_id)
    
    def list_containers(self) -> List[Dict[str, Any]]:
        """Liệt kê tất cả active containers"""
        return list(self.active_containers.values())
    
    def stop_container(self, container_id: str, remove_workspace: bool = True) -> Dict[str, Any]:
        """Dừng và xóa container"""
        if container_id not in self.active_containers:
            return {"status": "error", "message": "Container not found"}
        
        try:
            container_info = self.active_containers[container_id]
            
            # Stop container
            subprocess.run([
                "docker", "stop", container_id
            ], check=False, capture_output=True)
            
            # Clean up workspace
            if remove_workspace and os.path.exists(container_info["workspace_host"]):
                import shutil
                shutil.rmtree(container_info["workspace_host"], ignore_errors=True)
            
            # Remove from tracking
            del self.active_containers[container_id]
            
            logger.info(f"Stopped sandbox container: {container_info['container_name']}")
            
            return {"status": "success", "message": "Container stopped successfully"}
            
        except Exception as e:
            error_msg = f"Error stopping container: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def cleanup_all(self):
        """Dọn dẹp tất cả containers"""
        for container_id in list(self.active_containers.keys()):
            self.stop_container(container_id)
    
    def _get_timestamp(self) -> str:
        """Lấy timestamp hiện tại"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def create_network_policy(self, container_id: str, allowed_hosts: List[str]) -> Dict[str, Any]:
        """Tạo network policy cho container"""
        if not self.enabled:
            return {"status": "disabled", "message": "Sandboxing is disabled"}
        
        try:
            # Create iptables rules for network isolation
            # This is a simplified version - in production, use proper network policies
            policy_rules = []
            
            for host in allowed_hosts:
                rule = f"ALLOW {container_id} -> {host}"
                policy_rules.append(rule)
            
            return {
                "status": "success",
                "container_id": container_id,
                "allowed_hosts": allowed_hosts,
                "rules": policy_rules
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to create network policy: {str(e)}"}

# Global sandbox manager instance
_sandbox_manager: Optional[SandboxManager] = None

def get_sandbox_manager(config: Optional[Dict[str, Any]] = None) -> SandboxManager:
    """Lấy global sandbox manager instance"""
    global _sandbox_manager
    
    if _sandbox_manager is None:
        if config is None:
            # Import config nếu chưa có
            from src.config import Config
            config = Config.get_sandbox_config()
        
        _sandbox_manager = SandboxManager(config)
    
    return _sandbox_manager

def initialize_sandboxing():
    """Khởi tạo sandboxing system"""
    manager = get_sandbox_manager()
    
    if manager.enabled:
        logger.info("Sandboxing system initialized")
    else:
        logger.warning("Sandboxing is disabled - commands will run without isolation")
    
    return manager

def cleanup_sandboxes():
    """Cleanup tất cả sandboxes khi shutdown"""
    if _sandbox_manager:
        _sandbox_manager.cleanup_all()
        logger.info("All sandboxes cleaned up")