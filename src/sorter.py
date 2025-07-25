from datetime import datetime

def convert_memos_to_markdown(memos: list[dict]) -> str:
    """
    将从 Memos API 获取的 memos 列表转换为一个 Markdown 格式的字符串。

    Args:
        memos: 包含 memo 对象的列表。

    Returns:
        一个包含所有 memo 内容的 Markdown 格式的字符串。
    """
    markdown_content = ""
    for memo in memos:
        # 提取内容
        content = memo.get("content", "")
        
        # 提取创建时间并格式化
        create_time = memo.get("createTime")
        if create_time:
            # Memos API v2 返回的是 ISO 8601 格式的字符串 (e.g., "2025-07-16T16:41:54Z")
            # The 'Z' indicates UTC, so we parse it and then format it.
            dt_object = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
            # 格式化为 "YYYY-MM-DD HH:MM:SS"
            formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        else:
            formatted_time = "未知时间"

        # 构建 Markdown 条目
        # 使用 Markdown 的引用格式 (>) 来包裹每一条 memo
        # 并在前面加上时间和分隔线
        markdown_content += f"> {content}\n\n"
        markdown_content += f"_{formatted_time}_\n"
        markdown_content += "---\n\n"
        
    return markdown_content

if __name__ == '__main__':
    # 用于测试的模拟 memos 数据
    sample_memos = [
        {
            "id": 1,
            "content": "这是第一条测试 memo。",
            "createdTs": 1672531200 # 2023-01-01 00:00:00
        },
        {
            "id": 2,
            "content": "这是第二条，带有一些 #标签 和链接 https://example.com",
            "createdTs": 1672617600 # 2023-01-02 00:00:00
        },
        {
            "id": 3,
            "content": "第三条 memo，\n包含换行符。",
            "createdTs": 1672704000 # 2023-01-03 00:00:00
        }
    ]

    # 调用函数进行转换
    markdown_output = convert_memos_to_markdown(sample_memos)

    # 打印结果
    print("--- 转换后的 Markdown ---")
    print(markdown_output)

    # 也可以将结果保存到文件
    # with open("memos_output.md", "w", encoding="utf-8") as f:
    #     f.write(markdown_output)
    # print("已将结果保存到 memos_output.md")
