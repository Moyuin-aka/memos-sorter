from datetime import datetime
import os

def export_to_markdown(classified_memos: dict, output_filename: str = None):
    """
    将分类后的 memos 导出为 Markdown 文件，并存放在 'memos-sorted' 文件夹中。

    Args:
        classified_memos: 一个字典，键是分类名称，值是属于该分类的 memo 内容列表。
        output_filename: (可选) 输出的 Markdown 文件名。如果未提供，
                         将根据当前时间生成一个文件名。
    """
    output_dir = "memos-sorted"
    os.makedirs(output_dir, exist_ok=True)

    if not output_filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"memos_sorted_{timestamp}.md"

    output_path = os.path.join(output_dir, output_filename)

    print(f"正在将分类结果导出到文件: {output_path}")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Memos 分类整理\n\n")
            f.write(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

            for category, memos in classified_memos.items():
                f.write(f"## {category}\n\n")
                
                if not memos:
                    f.write("此分类下没有内容。\n\n")
                    continue

                for memo in memos:
                    formatted_memo = memo.replace("\n", "  \n")
                    f.write(f"- {formatted_memo}\n")
                
                f.write("\n")
        
        print(f"\n成功将分类结果保存到文件: {output_path}")

    except IOError as e:
        print(f"写入文件时发生错误: {e}")
    except Exception as e:
        print(f"导出为 Markdown 时发生未知错误: {e}")
