import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from src.config import CODER_API_BASE, VN_API_BASE, API_KEY
from src.mcp_wrapper import MCPManager
from src.tools_project import list_files_recursive, read_file_content
from src.tools_code import write_to_project, execute_in_sandbox
from src.tools_vision import analyze_image
from src.mpc_planner import mpc_optimize_plan
from src.skills_manager import SkillManager

# --- MODEL SETUP ---
llm_vn = ChatOpenAI(model="vinai/PhoGPT-4B-Chat", openai_api_base=VN_API_BASE, openai_api_key=API_KEY, temperature=0.6)
llm_coder = ChatOpenAI(model="casperhansen/llama-3-70b-instruct-awq", openai_api_base=CODER_API_BASE, openai_api_key=API_KEY, temperature=0.1)

# --- STATE ---
class AgentState(TypedDict):
    user_id: str
    user_input_vn: str
    project_structure: str
    image_url: str
    goal_english: str      
    current_state: str     
    mpc_plan: str        
    code: str
    exec_result: str
    iterations: int
    final_response_vn: str

# --- NODES ---

# --- 1. SETUP MCP TOOLS ---
def get_mcp_capabilities():
    """Đọc config và tạo prompt cho Agent biết mình làm được gì"""
    try:
        with open("mcp_servers_config.json", "r") as f:
            servers = json.load(f).get("mcpServers", {})
        
        caps = []
        for name, conf in servers.items():
            caps.append(f"- Server '{name}': Connects to {conf['args'][1]}")
        
        return "\n".join(caps)
    except:
        return "No MCP servers configured."

mcp_info = get_mcp_capabilities()

# --- 2. UPDATE SYSTEM PROMPT ---
# Cập nhật prompt của NODE CODER và NODE MPC để nhận biết MCP

def mcp_controller_node(state):
    # ...
    prompt = f"""You are an Autonomous AI with MCP (Model Context Protocol) Integration.
    
    AVAILABLE MCP SERVERS (External Integration):
    {mcp_info}
    
    If you need to use these (e.g., read file from Git, Query SQLite), 
    write Python code using the 'mcp' library to connect and query them directly.
    
    Example to use MCP in Python Code:
    ```python
    # Code to spawn a subprocess for 'npx ...' and query it
    # OR simply use standard libraries since you have full terminal access via Sandbox.
    ```
    ...
    """

def perception_node(state):
    # Lấy cây thư mục mới nhất (sau khi user upload hoặc AI vừa sửa)
    structure = list_files_recursive(state['user_id'])
    
    # Nếu user upload file, đưa vào context
    context_msg = ""
    if structure:
        context_msg = f"\n[CURRENT PROJECT STRUCTURE]:\n{structure}"
    """Pha 1: Nhận thức (Perception) - Hiểu mục tiêu và Nhìn (Vision)"""
    prompt = f"Dịch yêu cầu sau sang tiếng Anh kỹ thuật (ngắn gọn) để làm Goal cho MPC Agent: {state['user_input_vn']}"
    
    # Nếu có ảnh, đưa thông tin ảnh vào trạng thái ban đầu
    vision_context = ""
    if state['image_url']:
        desc = analyze_image(state['image_url'])
        vision_context = f"\nVisual Context from Image: {desc}"
    
    res = llm_vn.invoke(prompt)
    technical_goal = res.content + vision_context
    
    return {
        "project_structure": structure, "technical_plan": "...",
        "goal_english": technical_goal, 
        "current_state": "Starting task. No actions taken yet."
    }

def coder_node(state):
    """Coder: Được phép đọc file và sửa file"""
    prompt = f"""You are a Lead Developer working on an existing project.
    
    PROJECT STRUCTURE:
    {state['project_structure']}
    
    TASK: {state['technical_plan']}
    
    CAPABILITIES:
    1. To READ a file, output: READ_FILE|path/to/file
    2. To WRITE/FIX a file, output: 
       ```python
       # WRITE_FILE: path/to/file.py
       ... code content ...
       ```
    3. To RUN command, output: CMD|python3 path/to/main.py
    
    Execute the task step-by-step.
    """

def mpc_controller_node(state):
    """Pha 2: MPC Controller - Tối ưu hóa hành động"""
    print(f"--- MPC ITERATION {state['iterations']} ---")
    
    # Gọi MPC Planner để tính toán bước đi tiếp theo
    # Nó sẽ tự động check Skill Manager bên trong hàm này
    response_content = mpc_optimize_plan(
        goal=state['goal_english'],
        current_state_desc=state['current_state'],
        available_tools_desc="Python Sandbox, Internet"
    )
    
    # Trích xuất Code từ phản hồi của MPC
    import re
    match = re.search(r"```python(.*?)```", response_content, re.DOTALL)
    code = match.group(1).strip() if match else ""
    
    return {"mpc_plan": response_content, "code": code, "iterations": state['iterations'] + 1}

def actuator_node(state):
    """Pha 3: Thực thi (Actuator) - Chạy code"""
    if not state['code']: 
        return {"exec_result": "No code provided by MPC.", "current_state": "MPC failed to generate code."}
    
    res = execute_in_sandbox(state['code'])
    
    # Cập nhật trạng thái mới dựa trên kết quả chạy
    new_state_desc = f"Executed Code. Result:\n{res}"
    return {"exec_result": res, "current_state": new_state_desc}

def skill_learner_node(state):
    """Pha 4: Học tập (Learning) - Nếu thành công, tự lưu thành Skill"""
    # Logic: Nếu code chạy thành công (không lỗi) và đây là iteration cuối, hỏi xem có nên lưu skill không
    if "ERROR" not in state['exec_result']:
        prompt = f"""Analyze this code execution. Is it a reusable function worth saving as a Skill?
        Goal: {state['goal_english']}
        Code: {state['code']}
        
        If yes, provide a NAME (snake_case) and DESCRIPTION.
        Format: SAVE_SKILL|name|description
        If no, return NO_SAVE.
        """
        res = llm_coder.invoke(prompt).content
        
        if "SAVE_SKILL" in res:
            parts = res.split("|")
            if len(parts) >= 3:
                name = parts[1].strip()
                desc = parts[2].strip()
                save_msg = SkillManager.save_skill(name, state['code'], desc)
                return {"current_state": state['current_state'] + f"\n[System]: {save_msg}"}
    
    return {}

def translator_out(state):
    """Pha 5: Giao tiếp - Báo cáo kết quả"""
    prompt = f"""User asked: {state['user_input_vn']}
    Final Result: {state['current_state']}
    Explain the result in Vietnamese. If a new skill was learned, mention it."""
    res = llm_vn.invoke(prompt)
    return {"final_response_vn": res.content}

# --- GRAPH WIRING ---
workflow = StateGraph(AgentState)

workflow.add_node("perception", perception_node)
workflow.add_node("mpc_controller", mpc_controller_node)
workflow.add_node("actuator", actuator_node)
workflow.add_node("skill_learner", skill_learner_node)
workflow.add_node("translator_out", translator_out)

workflow.set_entry_point("perception")
workflow.add_edge("perception", "mpc_controller")
workflow.add_edge("mpc_controller", "actuator")
workflow.add_edge("actuator", "skill_learner")

def check_convergence(state):
    """Kiểm tra xem sai số giữa Goal và State đã đủ nhỏ chưa"""
    # Nếu kết quả có "SUCCESS" hoặc đã chạy quá 5 lần -> Dừng
    # Nếu còn Lỗi -> Quay lại MPC Controller để chỉnh code
    if "ERROR" in state['exec_result'] and state['iterations'] < 5:
        return "mpc_controller"
    return "translator_out"

workflow.add_conditional_edges("skill_learner", check_convergence, {
    "mpc_controller": "mpc_controller",
    "translator_out": "translator_out"
})
workflow.add_edge("translator_out", END)

app_graph = workflow.compile()