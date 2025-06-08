# Google Gemini 模型集成指南

## 🔮 概述

本项目现已支持 Google Gemini 模型作为 SQL 生成后端，提供强大的自然语言理解能力。

## 🚀 快速开始

### 1. 获取 API Key

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录您的 Google 账户
3. 创建新的 API Key
4. 复制生成的 API Key

### 2. 设置API Key

**方式一：在Web界面设置（推荐）**
1. 启动Web服务器
2. 在浏览器中打开网页
3. 在"模型配置"区域直接输入API Key
4. 无需设置环境变量，即用即设

**方式二：设置环境变量**

**Windows:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY=your_api_key_here
```

**永久设置（可选）:**
- Windows: 在系统环境变量中添加 `GEMINI_API_KEY`
- Linux/Mac: 在 `~/.bashrc` 或 `~/.zshrc` 中添加 export 语句

### 3. 安装依赖

```bash
pip install google-generativeai
```

或安装完整依赖：
```bash
pip install -r requirements.txt
```

### 4. 测试连接

```bash
python test_gemini.py
```

## 🎯 使用方式

### 命令行模式

```bash
# 使用默认 Gemini 模型
python main.py --backend gemini

# 指定具体模型
python main.py --backend gemini --model gemini-1.5-pro

# 直接执行查询
python main.py --backend gemini --query "查询所有用户信息"
```

### Web 界面模式

```bash
# 方式一：使用专用启动脚本
start_web_gemini.bat

# 方式二：命令行启动
python web_server.py --backend gemini --model gemini-1.5-flash

# 方式三：自定义端口
python web_server.py --backend gemini --port 8080
```

### Web 界面配置

1. 访问 http://localhost:5000
2. 在"快捷操作"区域找到"模型配置"
3. 选择 "Google Gemini" 作为后端类型
4. 选择具体的 Gemini 模型
5. **（推荐）在 API Key 输入框中输入您的 Gemini API Key**
   - 如果不输入，系统会尝试使用环境变量 `GEMINI_API_KEY`
   - 点击眼睛图标可以切换密码可见性
   - 点击"获取API Key"链接可以直接跳转到申请页面
6. 点击"应用配置并初始化"

## 🤖 可用模型

- `gemini-1.5-flash` - 快速响应，适合日常查询
- `gemini-1.5-pro` - 高级版本，更好的理解能力
- `gemini-pro` - 经典版本，平衡性能和质量

## ⚙️ 配置选项

### 模型参数

可以通过修改 `gemini_sql_generator.py` 中的 `generation_config` 来调整：

```python
generation_config = {
    "temperature": 0.1,      # 控制随机性，越低越确定
    "top_p": 0.95,          # 核采样参数
    "top_k": 40,            # Top-K 采样
    "max_output_tokens": 1000, # 最大输出长度
}
```

### 安全设置

默认安全设置允许 SQL 生成，如需调整可修改 `safety_settings`。

## 🔍 故障排除

### 常见问题

**1. API Key 错误**
```
ERROR: 请设置环境变量 GEMINI_API_KEY
```
**解决:** 确认已正确设置环境变量并重启终端

**2. 网络连接问题**
```
ERROR: Gemini模型调用失败 - [网络错误]
```
**解决:** 检查网络连接，确认可以访问 Google 服务

**3. 依赖包缺失**
```
ImportError: No module named 'google.generativeai'
```
**解决:** 安装依赖 `pip install google-generativeai`

**4. 模型返回空响应**
```
ERROR: Gemini模型返回空响应
```
**解决:** 尝试更换模型版本或检查 API 配额

### 调试模式

启用详细日志：
```bash
python main.py --backend gemini --query "测试查询" -v
```

## 📊 性能对比

| 特性 | Ollama (本地) | 通义千问 API | Gemini API |
|------|---------------|--------------|------------|
| 响应速度 | 快 | 中等 | 快 |
| 理解能力 | 中等 | 强 | 很强 |
| 成本 | 免费 | 付费 | 付费 |
| 隐私性 | 最高 | 中等 | 中等 |
| 网络要求 | 无 | 需要 | 需要 |

## 🔐 安全注意事项

1. **API Key 保护**: 不要在代码中硬编码 API Key
2. **网络安全**: 使用 HTTPS 连接
3. **数据隐私**: 查询内容会发送到 Google 服务器
4. **访问控制**: 仅在受信任的环境中使用

## 💰 成本控制

- Gemini API 有免费配额，超出后按使用量计费
- 建议在 Google Cloud Console 中设置预算警报
- 对于频繁使用，考虑使用本地 Ollama 模型

## 🆘 获取帮助

1. 查看 [Google AI 文档](https://ai.google.dev/)
2. 检查项目 Issues
3. 运行测试脚本排查问题：`python test_gemini.py`

---

**enjoy your Gemini-powered SQL experience!** 🎉 