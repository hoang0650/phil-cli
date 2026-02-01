from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.config import VISION_API_BASE, API_KEY

llm_vision = ChatOpenAI(
    model="Qwen/Qwen2-VL-7B-Instruct-AWQ",
    openai_api_base=VISION_API_BASE,
    openai_api_key=API_KEY,
    max_tokens=1024
)

def analyze_image(image_path, prompt="Mô tả chi tiết hình ảnh này để lập trình viên hiểu."):
    # Với vLLM local, ta có thể cần encode base64 hoặc pass URL nếu setup fileserver
    # Ở đây giả định user gửi link ảnh hoặc file path mount được
    # Để đơn giản cho demo: chỉ nhận URL ảnh public hoặc base64
    
    # (Code thực tế cần hàm convert local image to base64 data url)
    msg = HumanMessage(content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": image_path}} 
    ])
    try:
        res = llm_vision.invoke([msg])
        return res.content
    except Exception as e:
        return f"[Vision Error]: {e}"