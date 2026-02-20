import os
import importlib.util
import re
from typing import Dict, Any, List

class SkillManager:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.load_skills()

    def load_skills(self):
        """Tải tất cả các kỹ năng từ thư mục skills."""
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
        
        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            if os.path.isdir(skill_path):
                self.skills[skill_name] = self._parse_skill(skill_path)

    def _parse_skill(self, skill_path: str) -> Dict[str, Any]:
        """Phân tích cấu trúc của một kỹ năng."""
        skill_info = {
            "name": os.path.basename(skill_path),
            "path": skill_path,
            "description": "",
            "metadata": {},
            "executable": None,
            "type": "markdown" # Mặc định là markdown (openclaw style)
        }
        
        # 1. Parse SKILL.md (Cấu trúc chính của openclaw)
        md_path = os.path.join(skill_path, "SKILL.md")
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
                skill_info["description"] = content
                skill_info["metadata"] = self._extract_metadata_from_md(content)
        
        # 2. Kiểm tra tệp thực thi (Nếu có execute.py - phil-cli style)
        py_path = os.path.join(skill_path, "execute.py")
        if os.path.exists(py_path):
            skill_info["executable"] = py_path
            skill_info["type"] = "python"
            
        return skill_info

    def _extract_metadata_from_md(self, content: str) -> Dict[str, Any]:
        """Trích xuất metadata từ bảng Markdown trong SKILL.md."""
        metadata = {}
        # Tìm bảng metadata đầu tiên trong file
        # Cấu trúc bảng thường là | name | description | homepage | metadata |
        table_match = re.search(r"\| name \| description \| homepage \| metadata \|\s*\n\s*\| --- \| --- \| --- \| --- \|\s*\n\s*\| (.*?) \| (.*?) \| (.*?) \| (.*?) \|", content, re.MULTILINE)
        if table_match:
            metadata["name"] = table_match.group(1).strip()
            metadata["description"] = table_match.group(2).strip()
            metadata["homepage"] = table_match.group(3).strip()
            # Phần metadata chi tiết hơn có thể được parse thêm nếu cần
            
        return metadata

    def list_skills(self) -> List[str]:
        """Trả về danh sách tên các kỹ năng đã tải."""
        return list(self.skills.keys())

    def get_skill_details(self, skill_name: str) -> Dict[str, Any]:
        """Lấy thông tin chi tiết của một kỹ năng."""
        return self.skills.get(skill_name, {})

    def execute_skill(self, skill_name: str, **kwargs):
        """Thực thi kỹ năng."""
        if skill_name not in self.skills:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        skill = self.skills[skill_name]
        
        if skill["type"] == "python" and skill["executable"]:
            # Thực thi file Python
            spec = importlib.util.spec_from_file_location("skill_module", skill["executable"])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "run"):
                return module.run(**kwargs)
            return "Python skill loaded but no 'run' function found."
        
        elif skill["type"] == "markdown":
            # Đối với kỹ năng Markdown của openclaw, agent sẽ đọc SKILL.md 
            # và tự thực hiện các lệnh shell được mô tả trong đó.
            return f"Skill '{skill_name}' is a documentation-based skill. Please refer to its SKILL.md for instructions."

        return "Unknown skill type."

# Khởi tạo manager với đường dẫn mặc định
# manager = SkillManager("/home/ubuntu/phil-cli/skills")