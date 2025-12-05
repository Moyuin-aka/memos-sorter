from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json
import os
"""
LLM Provider 抽象层
提供统一的接口来调用不同的 LLM 服务（Gemini、OpenRouter 等）
"""

class LLMProvider(ABC):
    """LLM Provider 抽象基类"""
    
    @abstractmethod
    def classify_memos(self, markdown_content: str, 
                      categories: Dict[str, str]) -> Optional[Dict[str, List[str]]]:
        """
        对 memos 内容进行分类
        
        Args:
            markdown_content: Memos 的 markdown 内容
            categories: 分类定义，格式为 {分类名: 分类描述}
            
        Returns:
            分类结果，格式为 {分类名: [memo列表]}，失败返回 None
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        检查此 provider 是否可用（API Key 是否已配置）
        
        Returns:
            如果 API Key 已配置且有效，返回 True
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        获取 provider 的名称
        
        Returns:
            Provider 名称，如 "Gemini" 或 "OpenRouter"
        """
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini API Provider"""
    
    def __init__(self):
        from config import GEMINI_API_KEY, GEMINI_MODEL_NAME
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_MODEL_NAME
        self._client = None
        
    def _get_client(self):
        """延迟初始化 Gemini client"""
        if self._client is None and self.is_available():
            from google import genai
            from google.genai import types
            
            self._client = genai.Client(
                api_key=self.api_key,
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
        return self._client
    
    def is_available(self) -> bool:
        return self.api_key is not None and self.api_key.strip() != ""
    
    def get_name(self) -> str:
        return "Gemini"
    
    def classify_memos(self, markdown_content: str,
                      categories: Dict[str, str]) -> Optional[Dict[str, List[str]]]:
        """使用 Gemini API 对 memos 进行分类"""
        if not self.is_available():
            return None
            
        from google.genai import types
        
        # 1) 组织分类文本
        categories_str = "\n".join([f"- {name}: {desc}" for name, desc in categories.items()])
        category_keys = list(categories.keys())
        category_keys_str = ", ".join(category_keys)

        system_instruction = (
            "你是一个严谨的内容分类助手。"
            "只允许使用用户提供的分类键；不要新增或改写分类名；输出必须是有效 JSON。"
            "若某分类无内容，也要返回空数组。"
        )

        user_prompt = f"""请根据以下分类标准，将"Memos 内容"逐条归入对应分类：
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
            response_schema=response_schema,
            temperature=0,
        )

        try:
            client = self._get_client()
            resp = client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
            raw = (resp.text or "").strip()
            data = json.loads(raw)

            # 兜底：过滤未知键、补齐缺失键、统一字符串类型
            normalized = {k: [str(x) for x in data.get(k, [])] for k in category_keys}
            return normalized

        except json.JSONDecodeError as e:
            print(f"[{self.get_name()}] 解析 JSON 失败: {e}")
            print(f"原始响应: {getattr(resp, 'text', '')}")
            return None
        except Exception as e:
            print(f"[{self.get_name()}] 调用 API 时发生错误: {e}")
            return None


class OpenRouterProvider(LLMProvider):
    """OpenRouter API Provider"""
    
    def __init__(self):
        from config import (
            OPENROUTER_API_KEY, 
            OPENROUTER_MODEL_NAME,
            OPENROUTER_SITE_URL,
            OPENROUTER_SITE_NAME
        )
        self.api_key = OPENROUTER_API_KEY
        self.model_name = OPENROUTER_MODEL_NAME
        self.site_url = OPENROUTER_SITE_URL
        self.site_name = OPENROUTER_SITE_NAME
        
    def is_available(self) -> bool:
        return self.api_key is not None and self.api_key.strip() != ""
    
    def get_name(self) -> str:
        return "OpenRouter"
    
    def classify_memos(self, markdown_content: str,
                      categories: Dict[str, str]) -> Optional[Dict[str, List[str]]]:
        """使用 OpenRouter API 对 memos 进行分类"""
        if not self.is_available():
            return None
            
        import requests
        
        # 组织分类文本
        categories_str = "\n".join([f"- {name}: {desc}" for name, desc in categories.items()])
        category_keys = list(categories.keys())
        
        # 构造 JSON schema 示例
        schema_example = {k: [] for k in category_keys}
        
        system_prompt = (
            "你是一个严谨的内容分类助手。\n"
            "输出必须是有效的 JSON 格式，不要添加任何 markdown 代码块标记或其他文本。\n"
            "只允许使用用户提供的分类键；不要新增或改写分类名。\n"
            "若某分类无内容，也要返回空数组。"
        )
        
        user_prompt = f"""请根据以下分类标准，将"Memos 内容"逐条归入对应分类。

【分类标准】
{categories_str}

【输出要求】
- 输出必须是 JSON 格式，结构如下：
{json.dumps(schema_example, ensure_ascii=False, indent=2)}
- 每条 memo 只能属于一个分类
- 无内容的分类返回空数组
- 不要添加任何额外的文本或解释

【Memos 内容】
{markdown_content}
"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # 添加可选的 site 信息
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            headers["X-Title"] = self.site_name
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取响应内容
            if "choices" not in result or len(result["choices"]) == 0:
                print(f"[{self.get_name()}] 响应格式错误: 没有 choices")
                return None
                
            content = result["choices"][0]["message"]["content"].strip()
            
            # 移除可能的 markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # 解析 JSON
            data = json.loads(content)
            
            # 规范化输出
            normalized = {k: [str(x) for x in data.get(k, [])] for k in category_keys}
            return normalized
            
        except requests.exceptions.RequestException as e:
            print(f"[{self.get_name()}] HTTP 请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"[{self.get_name()}] 解析 JSON 失败: {e}")
            print(f"原始响应: {content if 'content' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"[{self.get_name()}] 调用 API 时发生错误: {e}")
            return None


def get_available_provider() -> LLMProvider:
    """
    按优先级返回第一个可用的 provider
    
    优先级顺序：
    1. OpenRouter (如果配置了 OPENROUTER_API_KEY)
    2. Gemini (如果配置了 GEMINI_API_KEY)
    
    Returns:
        第一个可用的 LLMProvider 实例
        
    Raises:
        ValueError: 如果没有任何可用的 provider
    """
    providers = [
        OpenRouterProvider(),
        GeminiProvider(),
    ]
    
    for provider in providers:
        if provider.is_available():
            print(f"使用 LLM Provider: {provider.get_name()}")
            return provider
    
    raise ValueError(
        "未配置任何可用的 LLM Provider API Key。\n"
        "请在 .env 文件中配置以下任意一个：\n"
        "  - OPENROUTER_API_KEY\n"
        "  - GEMINI_API_KEY"
    )
