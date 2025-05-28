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
# AI 模型配置 (后续添加)
# OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
# OLLAMA_BASE_URL = "http://localhost:11434" # 本地 Ollama 服务地址
# MODEL_NAME = "llama3" # 使用的模型名称
