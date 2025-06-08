# Gemini API 故障排除指南

## 常见问题及解决方案

### 1. 连接超时 / 网络错误

如果遇到以下错误：
```
failed to connect to all addresses
socket is null
ServiceUnavailable: 503
```

**原因分析：**
- 网络代理设置问题
- 防火墙阻止连接
- ISP阻止Google服务
- VPN或网络不稳定

**解决方案：**

#### 方案1: 检查网络代理
```bash
# 如果使用代理，请在环境变量中设置
set HTTP_PROXY=http://proxy:port
set HTTPS_PROXY=http://proxy:port

# 或者在Python代码中设置代理
import os
os.environ['HTTP_PROXY'] = 'http://proxy:port'
os.environ['HTTPS_PROXY'] = 'http://proxy:port'
```

#### 方案2: 临时关闭VPN/防火墙
- 暂时关闭VPN连接
- 临时禁用防火墙
- 尝试使用手机热点

#### 方案3: 使用网络诊断工具
```bash
python gemini_network_test.py
```

### 2. API Key 错误

如果遇到以下错误：
```
PERMISSION_DENIED
INVALID_ARGUMENT
400 API key not valid
```

**解决方案：**
1. 确认API Key格式正确（以`AIza`开头）
2. 检查API Key是否有效
3. 确认账户余额是否充足
4. 重新生成API Key

**获取新API Key：**
1. 访问：https://makersuite.google.com/app/apikey
2. 创建新的API Key
3. 复制完整的Key（包含AIza前缀）

### 3. 模型不可用

如果遇到模型相关错误：

**可用模型列表：**
- `gemini-1.5-flash`（推荐，速度快）
- `gemini-1.5-pro`（功能强大）
- `gemini-pro`（经典版本）

### 4. 网络环境测试

运行网络诊断：
```bash
python gemini_network_test.py
```

该工具会测试：
- 基本网络连接
- Google服务可达性
- API Key有效性
- 模型响应能力

### 5. 配置建议

#### 推荐配置：
```python
# 增加超时时间
response = model.generate_content(
    prompt, 
    request_options={'timeout': 60}
)

# 设置重试机制
import time
for attempt in range(3):
    try:
        response = model.generate_content(prompt)
        break
    except Exception as e:
        if attempt == 2:
            raise
        time.sleep(2 ** attempt)
```

#### 环境变量设置：
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

### 6. 替代方案

如果Gemini无法使用，可以切换到其他后端：

```bash
# 使用Qwen API
python web_server.py --backend qwen_api --model qwen-plus

# 使用本地Ollama
python web_server.py --backend ollama --model qwen2
```

### 7. 联系支持

如果问题仍然存在：
1. 记录完整的错误信息
2. 运行诊断工具并保存结果
3. 检查网络环境和代理设置
4. 考虑使用其他AI后端作为备选方案

---

## 快速自检清单

- [ ] API Key格式正确（AIza开头）
- [ ] 网络连接正常
- [ ] 防火墙/VPN关闭测试
- [ ] 账户余额充足
- [ ] 运行过网络诊断工具
- [ ] 尝试过其他模型
- [ ] 考虑过代理设置 