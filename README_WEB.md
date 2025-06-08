# 自然语言转SQL查询工具 - Web版本

## 🌟 特性

### Apple Design风格界面
- **现代化设计**: 参考Apple Design System，简洁优雅
- **响应式布局**: 完美适配桌面和移动设备
- **流畅动画**: 丝滑的交互体验
- **直观操作**: 符合用户习惯的交互设计

### 功能特性
- 🤖 **智能SQL生成**: 支持复杂的自然语言理解
- 🔮 **多模型支持**: 支持Ollama、通义千问、Google Gemini三种模型后端
- ⚙️ **可视化配置**: 前端可选择模型后端和具体模型
- 🔑 **Web端API Key设置**: 无需环境变量，直接在页面输入API Key
- 🛡️ **安全保障**: 多层安全检查，防止危险操作
- 📊 **多格式输出**: 表格、JSON、CSV等格式
- 🔄 **实时交互**: 无需刷新页面的流畅体验
- 📱 **移动友好**: 支持手机和平板访问
- 🔧 **热切换**: 无需重启即可切换模型配置

## 🚀 快速启动

### 方法一：使用批处理文件（推荐）
```bash
# Windows用户
双击运行 start_web.bat

# 或者在命令行中
start_web.bat
```

### 方法二：手动启动
```bash
# 确保依赖已安装
pip install flask flask-cors requests

# 启动服务器
python web_server.py
```

### 方法三：指定参数启动
```bash
# 使用在线API（通义千问）
python web_server.py --backend qwen_api --model qwen-plus

# 使用Google Gemini
python web_server.py --backend gemini --model gemini-1.5-flash

# 自定义端口
python web_server.py --port 8080

# 完整配置示例
python web_server.py --backend gemini --model gemini-1.5-pro --port 8080
```

### 方法四：使用Gemini专用启动脚本
```bash
# Windows用户 - Gemini版本
双击运行 start_web_gemini.bat

# 或者在命令行中
start_web_gemini.bat
```

## 🌐 访问方式

启动成功后，在浏览器中访问：
- **本地访问**: http://localhost:5000
- **局域网访问**: http://你的IP地址:5000

## 💡 使用指南

### 基本操作

1. **系统状态检查**
   - 页面顶部显示当前系统状态
   - 绿色表示正常，红色表示需要处理

2. **模型配置**
   - 选择后端类型（Ollama、通义千问、Gemini）
   - 选择具体模型
   - 直接输入API Key（推荐方式）
   - 一键应用配置

3. **快捷操作**
   - 查看数据库结构
   - 模型管理
   - 重新初始化系统

4. **自然语言查询**
   - 在查询框中输入中文描述
   - 选择结果显示格式
   - 点击"执行查询"或按Ctrl+Enter

5. **示例查询**
   - 点击预设的示例查询快速开始
   - 支持自定义查询语句

### 高级功能

- **格式切换**: 支持表格、JSON、CSV三种结果格式
- **SQL查看**: 显示AI生成的SQL语句
- **错误提示**: 详细的错误信息和解决建议
- **响应式设计**: 自动适配不同屏幕尺寸

## 🎨 界面特色

### Apple Design System元素
- **SF Pro字体**: 使用Apple官方字体系统
- **圆角设计**: 12px和16px的圆角半径
- **阴影效果**: 精致的光影层次
- **色彩系统**: 符合Apple Human Interface Guidelines
- **动画效果**: 自然流畅的过渡动画

### 交互设计
- **悬停反馈**: 按钮和卡片的悬停效果
- **加载状态**: 优雅的加载动画
- **模态弹窗**: 毛玻璃效果的弹窗设计
- **表格滚动**: 大数据量的优雅展示

## 🔧 配置说明

### 数据库配置
编辑 `config.ini` 文件：
```ini
[mysql]
host = 127.0.0.1
port = 3306
user = root
password = root
database = erp
```

### 大模型配置
- **本地Ollama**: 默认使用qwen2模型
- **通义千问API**: 需要设置DASHSCOPE_API_KEY环境变量
- **Google Gemini**: 需要设置GEMINI_API_KEY环境变量

#### 环境变量设置
```bash
# 通义千问 API Key
Windows: set DASHSCOPE_API_KEY=your_api_key
Linux/Mac: export DASHSCOPE_API_KEY=your_api_key

# Google Gemini API Key
Windows: set GEMINI_API_KEY=your_api_key
Linux/Mac: export GEMINI_API_KEY=your_api_key
```

#### 获取API Key
- **通义千问**: https://dashscope.aliyun.com/
- **Google Gemini**: https://makersuite.google.com/app/apikey

## 📱 移动端优化

- **响应式网格**: 自动调整布局
- **触摸友好**: 适合手指操作的按钮尺寸
- **滚动优化**: 流畅的滚动体验
- **键盘适配**: 移动设备键盘弹出适配

## 🛠️ 开发说明

### 技术栈
- **后端**: Flask + Python
- **前端**: HTML5 + CSS3 + JavaScript
- **设计**: Apple Design System
- **字体**: SF Pro Display
- **图标**: Font Awesome

### 项目结构
```
├── web_server.py          # Flask后端服务器
├── gemini_sql_generator.py   # Google Gemini模型生成器
├── llm_sql_generator.py   # 通义千问API生成器
├── ollama_sql_generator.py   # Ollama本地模型生成器
├── templates/
│   └── index.html         # 主页面模板（支持模型配置）
├── start_web.bat          # 默认启动脚本
├── start_web_gemini.bat   # Gemini专用启动脚本
└── README_WEB.md          # Web版本说明
```

### API接口
- `GET /api/status` - 获取系统状态
- `POST /api/query` - 执行查询
- `GET /api/schema` - 获取数据库结构
- `GET /api/models` - 获取模型信息（支持多后端）
- `POST /api/initialize` - 重新初始化（支持后端和模型参数）

## 🔐 安全特性

- **CORS保护**: 防止跨域攻击
- **SQL注入防护**: 多层安全检查
- **只读查询**: 仅允许SELECT操作
- **错误处理**: 安全的错误信息展示

## 🚨 故障排除

### 常见问题

1. **无法访问页面**
   - 检查防火墙设置
   - 确认端口5000未被占用
   - 尝试使用127.0.0.1:5000

2. **模型连接失败**
   - 确保Ollama服务正在运行
   - 检查模型是否已下载
   - 尝试重新初始化

3. **数据库连接失败**
   - 检查config.ini配置
   - 确认数据库服务状态
   - 验证用户权限

### 性能优化
- 使用生产环境WSGI服务器
- 启用静态资源缓存
- 数据库连接池优化

## 📄 许可证

MIT License - 详见原项目许可证

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**享受您的现代化SQL查询体验！** 🎉 