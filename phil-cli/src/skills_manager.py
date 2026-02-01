import os
import json
import re

SKILLS_DIR = "skills"
REGISTRY_FILE = os.path.join(SKILLS_DIR, "registry.json")

# Đảm bảo thư mục tồn tại
if not os.path.exists(SKILLS_DIR):
    os.makedirs(SKILLS_DIR)
    with open(os.path.join(SKILLS_DIR, "__init__.py"), "w") as f: f.write("")
if not os.path.exists(REGISTRY_FILE):
    with open(REGISTRY_FILE, "w") as f: json.dump({}, f)

class SkillManager:
    @staticmethod
    def save_skill(name, code, description):
        """Lưu một đoạn code thành kỹ năng tái sử dụng"""
        # 1. Clean tên skill để làm tên file (chỉ a-z, 0-9)
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '', name.lower())
        file_path = os.path.join(SKILLS_DIR, f"{safe_name}.py")
        
        # 2. Lưu code python
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        # 3. Cập nhật Registry
        with open(REGISTRY_FILE, "r") as f:
            registry = json.load(f)
        
        registry[safe_name] = {
            "description": description,
            "file": f"{safe_name}.py",
            "usage": f"from skills.{safe_name} import run"
        }
        
        with open(REGISTRY_FILE, "w") as f:
            json.dump(registry, f, indent=2)
            
        return f"Skill '{safe_name}' saved successfully."

    @staticmethod
    def get_all_skills():
        """Lấy danh sách kỹ năng để MPC tham khảo"""
        with open(REGISTRY_FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def retrieve_relevant_skills(query, llm_matcher=None):
        """Tìm kỹ năng phù hợp với yêu cầu (Dùng keyword đơn giản hoặc LLM)"""
        registry = SkillManager.get_all_skills()
        found_skills = []
        
        # Logic đơn giản: tìm keyword trong description
        # (Nâng cao: Dùng Vector DB nếu số lượng skill > 100)
        query_terms = query.lower().split()
        for name, data in registry.items():
            score = 0
            for term in query_terms:
                if term in data['description'].lower() or term in name:
                    score += 1
            if score > 0:
                found_skills.append(f"- Skill: {name}\n  Desc: {data['description']}\n  Import: {data['usage']}")
        
        if not found_skills:
            return "No specific pre-learned skills found."
        return "\n".join(found_skills)