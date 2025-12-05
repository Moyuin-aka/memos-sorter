# config.py
import os
from dotenv import load_dotenv
load_dotenv()
# Memos API 配置
# 请替换为你的 Memos 服务地址和 API Token
# 例如：MEMOS_URL = "https://demo.usememos.com"
# API Token 获取方式：登录 Memos -> 设置 -> 我的账户 -> Open API
MEMOS_URL = os.getenv("MEMOS_URL") # 示例: "http://localhost:5230"
MEMOS_API_TOKEN = os.getenv("MEMOS_API_TOKEN") # 从 Memos 设置中获取

# 内容分类标签
# 用户可以自定义这些标签
CATEGORIES = {
    "Recording": "技术记录、知识笔记、教程草稿、操作分析等偏理性的内容。",
    "Thoughts": "带有主观判断与认知输出的内容，倾向于反思、自我分析等思辨内容。",
    "Confession": "情感浓度最高的内容，偏向于私人经历、情绪波动、生活碎片等。"
}
if MEMOS_API_TOKEN is None or MEMOS_URL is None:
    raise ValueError("请确保已设置 MEMOS_URL 和 MEMOS_API_TOKEN 环境变量。")

# --- AI 模型配置 ---

# Gemini 配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-latest") # 默认模型

# OpenRouter 配置
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL_NAME = os.getenv("OPENROUTER_MODEL_NAME", "google/gemini-2.0-flash-exp:free") # 默认模型
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL")  # 可选
OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME")  # 可选

# 检查至少配置了一个 LLM Provider
if not GEMINI_API_KEY and not OPENROUTER_API_KEY:
    raise ValueError(
        "请至少配置一个 LLM Provider 的 API Key：\n"
        "  - GEMINI_API_KEY (Google Gemini)\n"
        "  - OPENROUTER_API_KEY (OpenRouter)\n"
        "请在 .env 文件中设置相应的环境变量。"
    )
