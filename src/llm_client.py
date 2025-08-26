from google import genai
from google.genai import types
import json
from typing import Dict, List, Optional
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site'
        }
    ),
                      
)

def classify_memos_with_gemini(markdown_content: str,
                               categories: Dict[str, str]) -> Optional[Dict[str, List[str]]]:
    # 1) 组织分类文本
    categories_str = "\n".join([f"- {name}: {desc}" for name, desc in categories.items()])
    category_keys = list(categories.keys())
    category_keys_str = ", ".join(category_keys)

    system_instruction = (
        "你是一个严谨的内容分类助手。"
        "只允许使用用户提供的分类键；不要新增或改写分类名；输出必须是有效 JSON。"
        "若某分类无内容，也要返回空数组。"
    )

    user_prompt = f"""请根据以下分类标准，将“Memos 内容”逐条归入对应分类：
- 只允许使用这些分类键：{category_keys_str}
- 一条 memo 不可同时属于多个分类；无内容的分类请返回空数组
- 仅返回 JSON，不要任何多余解释

【分类标准】
{categories_str}

【Memos 内容】
{markdown_content}
"""

    # 2) 用 Schema 显式声明每个属性（避免 additionalProperties）
    schema_properties = {
        name: types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
        )
        for name in category_keys
    }
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        properties=schema_properties,
        required=category_keys,              # 强制所有键都出现（可为空数组）
        property_ordering=category_keys,     # 可选：保持字段顺序一致
    )

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=response_schema,     # 关键：改成显式 properties 的 Schema
        temperature=0,
    )

    try:
        resp = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=user_prompt,
            config=config,
        )
        raw = (resp.text or "").strip()
        data = json.loads(raw)

        # 兜底：过滤未知键、补齐缺失键、统一字符串类型
        normalized = {k: [str(x) for x in data.get(k, [])] for k in category_keys}
        return normalized

    except json.JSONDecodeError as e:
        print(f"解析 JSON 失败: {e}")
        print(f"原始响应: {getattr(resp, 'text', '')}")
        return None
    except Exception as e:
        print(f"调用 Gemini API 时发生错误: {e}")
        return None
