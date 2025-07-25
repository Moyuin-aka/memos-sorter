# Memos Sorter

Memos Sorter 是一个 Python 项目，用于从 [Memos](https://github.com/usememos/memos) 获取用户的 memos 内容，
利用 LLM 对其进行分析和分类，并最终输出为结构化的 Markdown 文件。

## 开发进度
还是期末周的学生，这个小玩具几乎从0开始学起。我慢慢来，在写小玩具中感受一下 vibe coding 的魅力🤩。
- [x] 实现基本项目框架
- [x] 处理好 memos 的调用
- [x] 加入 LLM 的调用
- [x] 处理 markdown 文件输出

## 注意事项
- 因为 AI studio 的 API_KEY 的申请是免费的，所以本程序目前只实现了对于 gemini api 调用的实现。如果要使用接入 OpenAI 的 ChatGPT，Anthropic 的 Claude，Deepseek 等，可能需要你的协助。
- 这个脚本只是 vibe coding 的小玩具，也许会有很多 bug，望谅解。
- 欢迎来提 issue 和 pr 👏。

## 快速开始
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（创建.env文件）
cp .env.example .env
# 编辑.env填写您的Memos和AI配置

# 3. 运行 Memos Sorter
python main.py
```

## 故障排除

### LLM API 调用问题

**问题：等待十几分钟无响应或超时**
- 检查网络连接是否正常
- 如果使用代理，请确保代理设置正确或尝试关闭代理
- Gemini API 在某些地区可能访问受限，建议使用稳定的网络环境
- 可以按 `Ctrl+C` 取消当前操作后重试

**问题：API 密钥错误**
- 确认 `.env` 文件中的 `YOUR_GEMINI_API_KEY` 是否正确填写
- 检查 API 密钥是否已过期或被撤销
- 访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 重新获取密钥

**问题：403 Forbidden 或地区限制**
- Gemini API 在某些地区不可用，可能需要使用 VPN
- 确认 API 密钥的使用配额是否已用完

### Memos API 调用问题

**问题：无法连接到 Memos 服务**
- 确认 `YOUR_MEMOS_URL` 格式正确（如：`http://localhost:5230` 或 `https://your-domain.com`）
- 检查 Memos 服务是否正在运行
- 确认网络能够访问指定的 Memos 地址

**问题：401 Unauthorized**
- 检查 `YOUR_MEMOS_API_KEY` 是否正确
- 确认 Token 是否有足够的权限读取 memos
- 在 Memos 设置中重新生成 API Token

### 其他问题

**问题：程序运行出错**
- 确认已正确安装所有依赖：`pip install -r requirements.txt`
- 检查 Python 版本是否为 3.8+
- 确认 `.env` 文件位于项目根目录且格式正确

**问题：分类结果不理想**
- 尝试使用自定义分类标签，提供更详细的分类描述
- 检查 memos 内容是否过短或缺乏上下文
- 大模型的分类结果可能存在一定随机性，可以多次尝试