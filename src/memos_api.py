import sys
# 确保 src 目录在 sys.path 中，以便可以导入 config 模块
import os
# memos_api.py
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import requests
import json
from config import MEMOS_URL, MEMOS_API_TOKEN # 从项目根目录的 config.py 导入

def fetch_all_memos():
    """
    从 Memos API 获取所有 memos。

    Returns:
        list: 包含所有 memo 对象的列表，如果请求失败则返回 None。
              每个 memo 对象是一个字典。
    """
    if not MEMOS_URL or not MEMOS_API_TOKEN:
        print("错误：MEMOS_URL 或 MEMOS_API_TOKEN 未在配置中设置。")
        print(f"MEMOS_URL: {MEMOS_URL}")
        print(f"MEMOS_API_TOKEN: {'已设置' if MEMOS_API_TOKEN else '未设置'}")
        return None

    api_url = f"{MEMOS_URL.rstrip('/')}/api/v1/memos" # 确保 URL 末尾没有多余的斜杠
    headers = {
        "Authorization": f"Bearer {MEMOS_API_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"正在从 {api_url} 获取 memos...")

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # 如果 HTTP 请求返回了错误状态码 (4xx or 5xx), 则抛出 HTTPError 异常

        memos_data = response.json() # 将响应内容解析为 JSON
        
        # Memos API v1 返回的数据结构通常是 {"data": [...memos...]}
        # 如果你的 Memos 版本 API 直接返回列表，请调整下面这行
        if isinstance(memos_data, dict) and "memos" in memos_data:
            return memos_data["memos"]
        elif isinstance(memos_data, dict) and "data" in memos_data:
            return memos_data["data"]
        elif isinstance(memos_data, list): # 兼容直接返回列表的情况
             return memos_data
        else:
            print(f"从 API 获取到的数据格式未知: {memos_data}")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        print(f"响应内容: {response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"连接错误: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"请求超时: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求发生错误: {req_err}")
    except json.JSONDecodeError:
        print(f"无法解析 JSON 响应: {response.text}")
    
    return None

if __name__ == '__main__':
    # 这个 __main__ 块允许你直接运行 memos_api.py 来测试 fetch_all_memos 函数
    print("正在测试 fetch_all_memos()...")
    
    # 确保你的 .env 文件已正确配置 MEMOS_URL 和 MEMOS_API_TOKEN
    
    # 重新加载配置，以确保在直接运行此文件时 .env 被加载
    # (如果在项目顶层运行，config.py 已经加载了)
    # 但为了独立测试此模块，可以再次显式加载或确保 config.py 的加载逻辑在导入时执行
    # from dotenv import load_dotenv
    # load_dotenv() # 如果 config.py 中的 load_dotenv() 没有在导入时执行，则需要此行
    
    # 检查配置是否加载
    if not MEMOS_URL or not MEMOS_API_TOKEN:
        print("请先在项目根目录创建 .env 文件并配置 MEMOS_URL 和 MEMOS_API_TOKEN。")
        print("示例 .env 内容：")
        print("MEMOS_URL=\"https://memos.xxx.com\"")
        print("MEMOS_API_TOKEN=\"your_actual_token_here\"")
    else:
        all_memos = fetch_all_memos()
        if all_memos:
            print(f"成功获取到 {len(all_memos)} 条 memos:")
            for i, memo in enumerate(all_memos[:1]): # 打印前1条作为示例
                print(f"\nMemo {i+1}:")
                print(f"  ID: {memo.get('id')}")
                print(f"  内容: {memo.get('content')[:100]}...") # 打印内容的前100个字符
                print(f"  创建时间: {memo.get('createdTs')}")
        else:
            print("获取 memos 失败。请检查配置和网络连接。")
