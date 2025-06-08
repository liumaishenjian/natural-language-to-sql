# 🚀 自然语言转SQL查询工具

一个现代化的Web应用，支持通过自然语言描述来生成SQL查询语句，同时支持直接SQL查询执行。基于AI大模型，提供智能、高效的数据库查询解决方案。

![主界面截图](docs/screenshot.png)

## ✨ 功能特性

### 🧠 智能查询
- **自然语言转SQL**: 使用自然语言描述查询需求，AI自动生成对应的SQL语句
- **直接SQL查询**: 支持直接输入和执行SQL语句
- **上下文对话**: 支持多轮对话，理解前后文语境
- **安全检查**: 自动进行SQL注入防护和安全性验证

### 🤖 多模型支持
- **Ollama本地模型**: 支持qwen2、llama2、codellama、mistral等本地模型
- **通义千问API**: 支持qwen-turbo、qwen-plus、qwen-max等在线模型
- **Google Gemini**: 支持gemini-1.5-flash、gemini-1.5-pro等模型
- **模型热切换**: 无需重启即可切换不同的AI模型

### 🗄️ 数据库支持
- **MySQL**: 完整支持MySQL数据库连接和查询
- **PostgreSQL**: 支持PostgreSQL数据库（预留接口）
- **SQLite**: 支持轻量级SQLite数据库（预留接口）
- **SQL Server**: 支持Microsoft SQL Server（预留接口）

### 🎨 现代化界面
- **三列布局**: 系统状态、快捷操作、示例查询分列显示
- **响应式设计**: 自适应不同屏幕尺寸
- **Apple Design风格**: 现代化的视觉设计
- **实时状态**: 实时显示系统连接状态和运行情况

### ⚙️ 配置管理
- **可视化配置**: 通过Web界面配置数据库连接和API密钥
- **配置持久化**: 所有配置自动保存到`config.ini`文件
- **表结构选择**: 可选择特定表进行查询，提高AI生成准确度
- **多格式输出**: 支持表格、JSON、CSV等多种结果格式

## 🛠️ 技术栈

### 后端
- **Python 3.8+**: 核心开发语言
- **Flask**: Web框架
- **MySQL Connector**: 数据库连接驱动
- **Requests**: HTTP客户端库
- **ConfigParser**: 配置文件管理

### 前端
- **HTML5 + CSS3**: 现代化Web标准
- **JavaScript (ES6+)**: 交互逻辑实现
- **Font Awesome**: 图标库
- **Responsive Design**: 响应式布局

### AI集成
- **Ollama**: 本地大模型运行环境
- **通义千问API**: 阿里云大模型服务
- **Google Gemini API**: 谷歌大模型服务

## 📦 安装部署

### 环境要求
- Python 3.8 或更高版本
- MySQL 5.7+ 或 8.0+
- 8GB+ 内存（使用本地模型时）

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/sql-query-tool.git
cd sql-query-tool
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装Ollama（可选，用于本地模型）
```bash
# Windows/Mac/Linux
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull qwen2
ollama serve
```

### 4. 配置数据库
编辑 `config.ini` 文件：
```ini
[mysql]
host = 127.0.0.1
port = 3306
user = root
password = your_password
database = your_database

[api_keys]
# 通义千问API Key (可选)
qwen_api_key = sk-your_qwen_key
# Google Gemini API Key (可选)
gemini_api_key = your_gemini_key
```

### 5. 启动服务
```bash
python web_server.py
```

访问 `http://localhost:5000` 即可使用！

## 🔧 配置说明

### 数据库配置
支持通过Web界面或配置文件设置数据库连接：

**MySQL示例**:
- 主机: `localhost`
- 端口: `3306`
- 用户名: `root`
- 密码: `your_password`
- 数据库: `your_database`

### API密钥配置
根据使用的AI模型配置相应的API密钥：

**通义千问**:
1. 访问 [阿里云DashScope](https://dashscope.aliyun.com/)
2. 获取API Key
3. 在配置页面输入或写入config.ini

**Google Gemini**:
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 获取API Key
3. 在配置页面输入或写入config.ini

## 📖 使用指南

### 基础查询
1. **自然语言查询**:
   - 输入: "查询所有用户信息"
   - 生成: `SELECT * FROM sys_user`

2. **复杂查询**:
   - 输入: "统计每个部门的人数"
   - 生成: `SELECT dept_name, COUNT(*) FROM users GROUP BY dept_id`

### 高级功能
1. **表结构选择**: 点击"选择表结构"按钮，选择相关表以提高查询准确度
2. **结果格式**: 选择表格、JSON或CSV格式输出
3. **模型切换**: 在快捷操作区域切换不同的AI模型
4. **SQL模式**: 切换到SQL查询模式直接执行SQL语句

### 示例查询
- `查询所有用户信息`
- `统计每个部门的人数`
- `查找最近一周的订单`
- `显示销售额最高的产品`
- `查询库存不足的商品`
- `显示月销售趋势`

## 🔌 API文档

### 查询接口
```bash
POST /api/query
Content-Type: application/json

{
    "query": "查询所有用户信息",
    "mode": "natural_language"
}
```

### 直接SQL执行
```bash
POST /api/execute-sql
Content-Type: application/json

{
    "sql": "SELECT * FROM users LIMIT 10"
}
```

### 系统状态
```bash
GET /api/status
```

### 配置管理
```bash
# 保存数据库配置
POST /api/save-db-config

# 保存模型配置
POST /api/save-model-config

# 获取配置
GET /api/get-db-config
GET /api/get-model-config
```

## 🚨 故障排除

### 常见问题

**1. Ollama连接失败**
```bash
# 检查Ollama服务状态
ollama list

# 重启Ollama服务
ollama serve

# 重新下载模型
ollama pull qwen2
```

**2. 数据库连接失败**
- 检查MySQL服务是否运行
- 验证用户名密码是否正确
- 确认数据库名称存在
- 检查防火墙设置

**3. API调用失败**
- 验证API Key是否正确
- 检查网络连接
- 确认API配额是否充足

**4. 前端页面异常**
- 清除浏览器缓存
- 检查浏览器控制台错误信息
- 确认服务器正常运行

### 日志分析
查看服务器终端输出的详细日志信息：
- `✅` 表示操作成功
- `⚠️` 表示警告信息
- `❌` 表示错误信息
- `🔄` 表示正在处理

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
1. Fork项目仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 提交Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串
- 确保代码测试覆盖率

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Ollama](https://ollama.com/) - 本地大模型运行环境
- [阿里云通义千问](https://dashscope.aliyun.com/) - 在线AI模型服务
- [Google Gemini](https://ai.google.dev/) - 谷歌AI模型服务
- [Flask](https://flask.palletsprojects.com/) - Python Web框架
- [Font Awesome](https://fontawesome.com/) - 图标库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/sql-query-tool/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/yourusername/sql-query-tool/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！ 