from typing import Dict, List, Optional
from src.llm_providers import get_available_provider
"""
LLM 客户端模块
提供统一的接口来调用 LLM 服务进行 memos 分类
"""

def classify_memos(markdown_content: str,
                               categories: Dict[str, str]) -> Optional[Dict[str, List[str]]]:
    """
    对 memos 内容进行分类    
    Args:
        markdown_content: Memos 的 markdown 内容
        categories: 分类定义，格式为 {分类名: 分类描述}
        
    Returns:
        分类结果，格式为 {分类名: [memo列表]}，失败返回 None
    """
    try:
        provider = get_available_provider()
        return provider.classify_memos(markdown_content, categories)
    except ValueError as e:
        print(f"错误: {e}")
        return None

