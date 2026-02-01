import docker
import os
import subprocess

class Sandbox:
    def __init__(self, image="python:3.11-slim"):
        try:
            self.client = docker.from_env()
            self.image = image
            self.container = None
            self.use_docker = True
        except Exception:
            self.use_docker = False

    def start(self):
        if self.use_docker and not self.container:
            try:
                self.container = self.client.containers.run(
                    self.image,
                    command="tail -f /dev/null",
                    detach=True,
                    tty=True,
                    working_dir="/workspace",
                    volumes={os.getcwd(): {"bind": "/workspace", "mode": "rw"}}
                )
            except Exception:
                self.use_docker = False
        return self.container

    def execute(self, command):
        if self.use_docker:
            if not self.container:
                self.start()
            if self.container:
                exec_result = self.container.exec_run(command)
                return exec_result.output.decode('utf-8'), exec_result.exit_code
        
        # Fallback to local execution if Docker fails or is not available
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout + result.stderr, result.returncode
        except Exception as e:
            return str(e), 1

    def stop(self):
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
            except Exception:
                pass
            self.container = None
