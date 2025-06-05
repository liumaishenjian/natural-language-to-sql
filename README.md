# 自然语言转SQL查询工具

一个基于通义千问大模型的自然语言转SQL查询工具，让用户可以用中文描述查询需求，自动生成并执行SQL语句。

## 功能特性

- 🤖 **智能SQL生成**: 使用阿里云通义千问大模型，支持复杂的自然语言理解
- 🛡️ **安全保障**: 多层安全检查，只允许SELECT查询，防止数据泄露和破坏
- 📊 **多格式输出**: 支持表格、JSON、CSV等多种结果显示格式
- 🔄 **交互式界面**: 命令行交互模式，支持连续查询
- 📝 **智能提示**: 自动读取数据库结构，为大模型提供上下文
- 🌐 **双模式支持**: 支持在线API和本地Ollama大模型

## 项目结构

```
natural-language-to-sql/
├── main.py                    # 主程序入口
├── database_connector.py      # 数据库连接模块
├── llm_sql_generator.py      # 在线API SQL生成模块
├── ollama_sql_generator.py   # 本地Ollama SQL生成模块
├── sql_security_checker.py   # SQL安全检查模块
├── result_formatter.py       # 结果格式化模块
├── config.ini                # 数据库配置文件
├── requirements.txt          # 依赖包列表
├── test_basic.py             # 基础测试文件
├── demo_test.py              # 演示测试文件
├── security_test.py          # 安全测试文件
└── README.md                 # 项目说明文档
```

## 安装和配置

### 1. 克隆项目

```bash
git clone https://github.com/liumaishenjian/natural-language-to-sql.git
cd natural-language-to-sql
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `config.ini` 文件，填入您的MySQL数据库信息：

```ini
[mysql]
host = YOUR_MYSQL_HOST
port = YOUR_MYSQL_PORT
user = YOUR_MYSQL_USER
password = YOUR_MYSQL_PASSWORD
database = YOUR_MYSQL_DATABASE
```

### 4. 选择使用模式

#### 方式一：使用在线API（通义千问）

设置通义千问API Key环境变量：

**Windows:**
```cmd
set DASHSCOPE_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export DASHSCOPE_API_KEY=your_api_key_here
```

#### 方式二：使用本地Ollama

1. 安装Ollama: https://ollama.ai/
2. 启动Ollama服务:
```bash
ollama serve
```
3. 下载模型:
```bash
ollama pull qwen2
```

## 使用方法

### 交互式模式

**使用在线API:**
```bash
python main.py --backend qwen_api
```

**使用本地Ollama:**
```bash
python main.py --backend ollama
```

然后输入自然语言查询，例如：
- "查询所有用户信息"
- "统计每个部门的人数"  
- "查找年龄大于25岁的用户姓名和邮箱"

### 命令行模式

```bash
# 直接执行查询
python main.py --query "查询所有用户" --backend ollama

# 指定输出格式
python main.py --query "查询用户统计" --format json --backend qwen_api

# 使用不同的模型
python main.py --model qwen-max --query "复杂查询" --backend qwen_api
```

### 可用参数

- `--config`: 指定配置文件路径（默认：config.ini）
- `--backend`: 后端类型（ollama/qwen_api，默认：ollama）
- `--model`: 指定大模型（本地：qwen2等，在线：qwen-turbo/qwen-plus/qwen-max）
- `--query`: 直接执行的查询（非交互模式）
- `--format`: 结果显示格式（table/json/csv/simple，默认：table）
- `--ollama-url`: Ollama服务URL（默认：http://localhost:11434）

## 安全特性

### 多层安全检查

1. **SQL语句类型检查**: 只允许SELECT语句
2. **关键词过滤**: 阻止INSERT、UPDATE、DELETE等危险操作
3. **函数检查**: 防止使用危险的MySQL函数
4. **注入攻击检测**: 识别和阻止SQL注入模式
5. **语法解析**: 使用sqlparse进行深度语法分析

### 数据库安全建议

- 使用只读数据库账号
- 限制账号只能访问特定数据库和表
- 在生产环境中使用专门的查询数据库

## 示例查询

以下是一些示例查询，展示工具的能力：

```
基础查询：
- "显示所有用户"
- "查看用户表的结构"

条件查询：
- "查找年龄大于30的用户"
- "显示最近注册的10个用户"

聚合查询：
- "统计每个城市的用户数量"
- "计算平均年龄"

关联查询：
- "显示用户及其订单信息"
- "查找购买过产品的用户名单"
```

## 特殊命令

在交互模式下，支持以下特殊命令：

- `help` 或 `帮助`: 显示帮助信息
- `schema` 或 `结构`: 显示数据库表结构
- `models` 或 `模型`: 显示可用模型（仅Ollama）
- `exit`, `quit` 或 `退出`: 退出程序

## 测试

项目包含完整的测试文件：

```bash
# 基础功能测试（不依赖外部服务）
python test_basic.py

# 完整功能演示（模拟测试）
python demo_test.py

# 安全功能测试
python security_test.py
```

## 故障排除

### 常见问题

1. **大模型连接失败**
   - 在线API：检查DASHSCOPE_API_KEY环境变量是否正确设置
   - 本地Ollama：确保Ollama服务正在运行并已下载模型

2. **数据库连接失败**
   - 检查config.ini中的数据库配置
   - 确认数据库服务正在运行
   - 验证账号密码和网络连接

3. **SQL生成质量不佳**
   - 尝试更具体的查询描述
   - 使用更高级的模型（如qwen-max）
   - 确保数据库表结构清晰且有意义的字段名

## 开发和扩展

### 添加新功能

本项目采用模块化设计，易于扩展：

- `database_connector.py`: 添加对其他数据库的支持
- `llm_sql_generator.py`: 集成其他大模型API
- `ollama_sql_generator.py`: 支持更多本地模型
- `sql_security_checker.py`: 增强安全检查规则
- `result_formatter.py`: 添加新的输出格式

### 贡献代码

欢迎提交Issue和Pull Request来改进项目！

## 许可证

本项目采用MIT许可证开源。

## 注意事项

- 本工具仅用于数据查询，不支持数据修改操作
- 生成的SQL语句会经过安全检查，确保数据安全
- 大模型API调用可能产生费用，请注意使用量
- 建议在测试环境中充分验证后再用于生产环境
- 本地Ollama模型需要足够的计算资源，建议8GB以上内存