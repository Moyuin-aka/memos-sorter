import sys
import os
import threading
import time
import json
import signal

# 将项目根目录添加到 sys.path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.memos_api import fetch_all_memos
from src.sorter import convert_memos_to_markdown
from src.llm_client import classify_memos_with_gemini
from src.markdown_exporter import export_to_markdown
from config import CATEGORIES

# --- 全局变量用于线程通信 ---
g_classified_memos = None
g_api_error = None
g_user_cancelled = False
g_api_thread = None

def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    global g_user_cancelled, g_api_thread
    print("\n\n正在取消操作...")
    g_user_cancelled = True
    
    # 等待 API 线程结束（最多等待 2 秒）
    if g_api_thread and g_api_thread.is_alive():
        print("等待后台任务完成...")
        g_api_thread.join(timeout=2.0)
    
    # 确保终端状态正常
    try:
        # 重置终端光标和缓冲区
        sys.stdout.write('\r' + ' ' * 50 + '\r')
        sys.stdout.flush()
        print("操作已取消。")
    except:
        pass
    
    # 正常退出
    os._exit(0)

def main():
    """
    主函数，执行以下操作:
    1. 从 Memos API 获取所有 memos。
    2. 将 memos 转换为 Markdown 格式。
    3. 提示用户选择或输入分类。
    4. 调用 LLM 对 memos 进行分类。
    5. 打印分类结果并导出到 Markdown 文件。
    """
    global g_api_thread
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        print("开始执行 Memos Sorter...")

        # 1. 获取所有 memos
        all_memos = fetch_all_memos()

        if all_memos:
            print(f"成功获取到 {len(all_memos)} 条 memos。")

            # 2. 将 memos 转换为 Markdown
            markdown_content = convert_memos_to_markdown(all_memos)

            # 3. 提示用户选择或输入分类
            user_categories = get_user_categories()

            # 4. 调用 LLM 进行分类 (带加载动画)
            print("\n正在调用 Gemini API 进行分类... (按 Ctrl+C 取消)")
            
            g_api_thread = threading.Thread(target=classify_worker, args=(markdown_content, user_categories))
            g_api_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            g_api_thread.start()

            loading_animation(g_api_thread)

            # 5. 打印并导出结果
            if g_user_cancelled:
                print("\n操作已取消。")
                return
            elif g_api_error:
                print(f"\n分类失败: {g_api_error}")
            elif g_classified_memos:
                print("\n--- 分类结果 ---")
                for category, memos in g_classified_memos.items():
                    print(f"\n## {category}")
                    for memo in memos:
                        print(f"- {memo}")
                
                # 导出到 Markdown 文件
                export_to_markdown(g_classified_memos)

            else:
                print("\n分类失败。未能从 API 获取有效结果。")

        else:
            print("获取 memos 失败，程序退出。请检查配置和网络连接。")

    except KeyboardInterrupt:
        # 这个异常现在由 signal_handler 处理
        pass
    except Exception as e:
        print(f"\n程序运行出错: {e}")
    finally:
        # 确保终端状态正常
        try:
            sys.stdout.write('\r' + ' ' * 50 + '\r')
            sys.stdout.flush()
        except:
            pass

def get_user_categories() -> dict:
    """获取用户的分类选择。"""
    try:
        print("\n--- 分类选项 ---")
        for name, desc in CATEGORIES.items():
            print(f"- {name}: {desc}")
        
        print("\n您可以直接使用以上预设分类，或输入自定义分类。")
        print("自定义分类请使用 JSON 格式，例如：")
        print('{"Life": "生活中的点滴记录", "Work": "工作相关的内容"}')
        
        user_input = input("请输入您的分类选择（留空使用预设分类）：")

        if not user_input.strip():
            return CATEGORIES
        
        try:
            return json.loads(user_input)
        except json.JSONDecodeError:
            print("无效的 JSON 格式，将使用预设分类。")
            return CATEGORIES
    except KeyboardInterrupt:
        # 如果在输入时按 Ctrl+C，直接触发信号处理
        signal_handler(signal.SIGINT, None)
        return CATEGORIES

def classify_worker(markdown_content, user_categories):
    """在工作线程中调用 Gemini API。"""
    global g_classified_memos, g_api_error, g_user_cancelled
    try:
        if not g_user_cancelled:
            g_classified_memos = classify_memos_with_gemini(markdown_content, user_categories)
    except Exception as e:
        if not g_user_cancelled:
            g_api_error = str(e)

def loading_animation(target_thread):
    """显示加载动画直到目标线程完成或用户取消。"""
    global g_user_cancelled
    chars = "/—\\|"
    idx = 0
    
    try:
        while target_thread.is_alive() and not g_user_cancelled:
            sys.stdout.write(f'\r{chars[idx % len(chars)]} 正在处理...')
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
    except KeyboardInterrupt:
        # 由 signal_handler 处理
        pass
    finally:
        # 清理输出行
        try:
            sys.stdout.write('\r' + ' ' * 30 + '\r')
            sys.stdout.flush()
        except:
            pass

if __name__ == "__main__":
    main()
