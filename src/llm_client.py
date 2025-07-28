# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Dict, List

# 新 SDK
from google import genai
from google.genai import types

from config import YOUR_GEMINI_API_KEY, GEMINI_MODEL_NAME


# 建议：全局复用一个 Client（线程安全场景下可自行封装）
client = genai.Client(api_key=YOUR_GEMINI_API_KEY)


def classify_memos_with_gemini(markdown_content: str,
                               categories: Dict[str, str]) -> Dict[str, List[str]]:
    """
    使用 Google GenAI SDK（google-genai）对 Memos 内容进行分类。
    返回: {分类名: [memo, ...]}
    """
    # 供提示词使用的“分类标准”文本
    categories_str = "\n".join([f"- {name}: {desc}" for name, desc in categories.items()])
    category_keys_str = ", ".join(categories.keys())

    # 系统指令：约束角色与风格
    system_instruction = (
        "你是一个严谨的内容分类助手。"
        "只允许使用用户提供的分类键；不要新增或改写分类名；输出必须是有效 JSON。"
        "若某分类无内容，也要返回空数组。"
    )

    # 用户内容：任务与数据
    user_prompt = f"""请根据以下分类标准，将“Memos 内容”逐条归入对应分类。
- 只允许使用这些分类键：{category_keys_str}
- 一条 memo 可同时属于多个分类；无内容的分类请返回空数组
- 仅返回 JSON，不要任何多余解释或 Markdown 围栏

【分类标准】
{categories_str}

【Memos 内容】
{markdown_content}
"""

    # 使用“结构化输出”：强制返回 JSON，且 schema 为 dict[str, list[str]]
    # 说明：google-genai 在 Python 中支持用类型注解声明 schema，
    # 这里用 dict[str, list[str]] 代表“任意字符串键 -> 字符串数组”的映射。
    # （模型仍会被上面的提示词约束，只使用给定分类键）
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=dict[str, list[str]],  # 动态键，值为字符串列表
        temperature=0,  # 分类任务建议降低随机性
    )

    resp = None
    try:
        resp = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=user_prompt,
            config=config,
        )

        raw = (resp.text or "").strip()  # 新 SDK 的文本在 resp.text
        data = json.loads(raw)

        # 兜底：确保所有分类键都存在；只保留允许的分类键；值统一成字符串
        normalized: Dict[str, List[str]] = {
            k: [str(x) for x in v] for k, v in data.items() if k in categories
        }
        for k in categories:
            normalized.setdefault(k, [])
        return normalized

    except json.JSONDecodeError as e:
        print(f"解析 JSON 失败: {e}")
        print(f"原始响应: {getattr(resp, 'text', '')}")
        return None
    except Exception as e:
        print(f"调用 Gemini API 时发生错误: {e}")
        return None
