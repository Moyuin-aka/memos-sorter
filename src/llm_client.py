import google.generativeai as genai
import json
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME

# 配置 Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def classify_memos_with_gemini(markdown_content: str, categories: dict) -> dict:
    """
    使用 Google Gemini API 对 Memos 内容进行分类。

    Args:
        markdown_content: 包含所有 memo 内容的 Markdown 格式的字符串。
        categories: 用户定义的分类及其描述。

    Returns:
        一个字典，键是分类名称，值是属于该分类的 memo 列表。
    """
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    # 构建分类的字符串，以便在 prompt 中使用
    categories_str = "\n".join([f"- {name}: {desc}" for name, desc in categories.items()])
    
    prompt = f"""
你是一个内容分类助手。请根据以下分类标准，将我提供的 Memos 内容逐条分类。

**分类标准:**
{categories_str}

**Memos 内容:**
{markdown_content}

请严格按照以下 JSON 格式返回结果，不要有任何多余的解释或说明：

```json
{{
  "分类1": [
    "memo 内容 1",
    "memo 内容 2"
  ],
  "分类2": [
    "memo 内容 3"
  ]
}}
```
"""

    try:
       # print("正在发送请求到 Gemini API...")
        response = model.generate_content(prompt)
        print("收到 Gemini API 响应")
        # 从返回结果中提取 JSON 部分
        # Gemini API 可能会在 JSON 前后添加 ```json 和 ```
        text_response = response.text.strip()
        json_start = text_response.find('{')
        json_end = text_response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("响应中未找到有效的 JSON 对象")

        json_str = text_response[json_start:json_end]
        
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        print(f"解析 Gemini API 响应时发生 JSON 错误: {e}")
        print(f"收到的原始响应: {response.text}")
        return None
    except Exception as e:
        print(f"调用 Gemini API 时发生错误: {e}")
        return None
