# Memos Sorter

Memos Sorter 是一个 Python 脚本，用于从 [Memos](https://github.com/usememos/memos) 获取用户的 memos 内容，利用 LLM 对其进行分析和分类，并最终输出为结构化的 Markdown 文件。

## 注意事项
- 本项目现支持2种 LLM 提供商，您须选择一个：
  - 使用 **Google Gemini**（推荐用于稳定性）
  - 使用 **OpenRouter**（支持多种模型，包括免费模型）
  - 程序会自动检测并选择您配置的 API
- 这个脚本只是 vibe coding 的小玩具，也许会有很多 bug，望谅解。
- 欢迎来提 issue 和 pr 👋。

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


## 配置说明

### LLM 提供商配置

本项目支持以下 LLM 提供商（至少配置其中一个）：

#### Google Gemini
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取 API Key
2. 在 `.env` 中设置：
   ```bash
   GEMINI_API_KEY="your_api_key_here"
   GEMINI_MODEL_NAME="gemini-2.5-flash-latest"  # 可选
   ```

#### OpenRouter
1. 访问 [OpenRouter](https://openrouter.ai/) 注册并获取 API Key
2. 在 `.env` 中设置：
   ```bash
   OPENROUTER_API_KEY="sk-or-v1-xxx"
   OPENROUTER_MODEL_NAME="google/gemini-2.0-flash-exp:free"  # 可选，推荐使用免费模型
   ```

**自动选择逻辑**：程序会按照以下优先级自动选择可用的 LLM：
1. OpenRouter（如果配置）
2. Gemini（如果配置）

## 故障排除

### LLM API 调用问题

**问题：等待十几分钟无响应或超时**
- 检查网络连接是否正常
- 如果使用代理，请确保代理设置正确或尝试关闭代理
- Gemini API 在某些地区可能访问受限，建议使用稳定的网络环境
- 可以按 `Ctrl+C` 取消当前操作后重试

**问题：API 密钥错误**
- 确认 `.env` 文件中的 API Key 是否正确填写
- 对于 Gemini：检查 `GEMINI_API_KEY` 并访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 重新获取
- 对于 OpenRouter：检查 `OPENROUTER_API_KEY` 并访问 [OpenRouter](https://openrouter.ai/keys) 查看密钥

**问题：429 Too Many Requests**
- 免费 API 配额已用完或达到速率限制
- 对于 OpenRouter：可以切换到其他免费模型或升级账户
- 对于 Gemini：等待配额重置或使用 OpenRouter 作为备选

**问题：403 Forbidden 或地区限制**
- Gemini API 在某些地区不可用，可能需要使用 VPN
- 建议尝试使用 OpenRouter 作为替代方案

### Memos API 调用问题

**问题：无法连接到 Memos 服务**
- 确认 `MEMOS_URL` 格式正确（如：`http://localhost:5230` 或 `https://your-domain.com`）
- 检查 Memos 服务是否正在运行
- 确认网络能够访问指定的 Memos 地址

**问题：401 Unauthorized**
- 检查 `MEMOS_API_TOKEN` 是否正确
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