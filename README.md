# Memos Sorter

Memos Sorter 是一个 Python 项目，用于从 [Memos](https://github.com/usememos/memos) 获取用户的 memos 内容，
利用 AI (如 OpenAI API 或本地 Ollama 模型) 对其进行分析和分类，并最终输出为结构化的 Markdown 文件。

## 开发进度
还是期末周的学生，这个小玩具几乎从0开始学起。慢慢来，期末考试后就有好玩的东西了。
- [x] 实现基本项目框架
- [ ] 处理好 memos 的调用
- [ ] 加入 LLM 的调用
- [ ] 处理 markdown 文件输出


## 预想功能

- 通过 Memos API 获取 Memos 数据。
- 将 Memos 数据转换为 Python 对象。
- 调用 AI 模型对 Memos 内容进行分类。
- 将分类后的 Memos 生成 Markdown 文件s
- 提供命令行界面进行交互。

## 快速开始
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（创建.env文件）
cp .env.example .env
# 编辑.env填写您的Memos和AI配置

# 3. 运行 Memos Sorter
python main.py