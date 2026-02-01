from langchain_core.messages import SystemMessage, HumanMessage
from src.config import CODER_API_BASE, API_KEY
from langchain_openai import ChatOpenAI
from src.skills_manager import SkillManager

llm = ChatOpenAI(model="casperhansen/llama-3-70b-instruct-awq", openai_api_base=CODER_API_BASE, openai_api_key=API_KEY, temperature=0.1)

def mpc_optimize_plan(goal, current_state_desc, available_tools_desc):
    """
    MPC Core:
    1. Quan sát trạng thái hiện tại (Current State).
    2. So sánh với Mục tiêu (Reference Trajectory).
    3. Tìm kiếm kỹ năng (Skills) có sẵn để rút ngắn quãng đường.
    4. Đưa ra Action tiếp theo (Control Input).
    """
    
    # 1. Tìm Skills phù hợp
    relevant_skills = SkillManager.retrieve_relevant_skills(goal)
    
    prompt = f"""You are an MPC (Model Predictive Control) Planner for an Autonomous AI.
    
    OBJECTIVE (REFERENCE): {goal}
    
    CURRENT STATE (OBSERVATION): 
    {current_state_desc}
    
    AVAILABLE SKILLS (MEMORY):
    {relevant_skills}
    
    AVAILABLE TOOLS:
    - Python Code Execution (Sandbox)
    - Web Search
    - Vision (Image Analysis)
    
    OPTIMIZATION TASK:
    Analyze the gap between Current State and Objective.
    Select the Next Best Action to minimize this gap.
    If a Skill matches the need, prioritize using it via `from skills... import ...`.
    
    OUTPUT FORMAT:
    Plan: [Short description of the strategy]
    Next Code: [Python code block to execute]
    """
    
    res = llm.invoke([SystemMessage(content=prompt)])
    return res.content