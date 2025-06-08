#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Google Gemini大模型生成SQL的类
"""

import os
import configparser
import google.generativeai as genai
import json
import requests

class GeminiSQLGenerator:
    """使用Google Gemini大模型生成SQL的类"""
    
    def __init__(self, model_name="gemini-1.5-flash", api_key=None, config_file="config.ini"):
        """
        初始化Gemini客户端
        model_name: 模型名称，可选 gemini-1.5-flash, gemini-1.5-pro, gemini-pro, gemini-2.5-flash-preview-05-20, gemini-2.0-flash-preview-image-generation
        api_key: API密钥，如果为None则从配置文件或环境变量获取
        config_file: 配置文件路径
        """
        print(f"🔮 [Gemini] 开始初始化 Gemini 客户端...")
        print(f"🔮 [Gemini] 模型名称: {model_name}")
        
        self.model_name = model_name
        
        # 获取API Key的优先级：传入参数 > 配置文件 > 环境变量
        if api_key:
            self.api_key = api_key
            print(f"🔮 [Gemini] 使用传入的API Key: {self.api_key[:20]}...")
        else:
            # 尝试从配置文件读取
            try:
                config = configparser.ConfigParser()
                config.read(config_file, encoding='utf-8')
                self.api_key = config.get('api_keys', 'gemini_api_key', fallback=None)
                if self.api_key and self.api_key.strip():
                    print(f"🔮 [Gemini] 从配置文件读取API Key: {self.api_key[:20]}...")
                else:
                    # 尝试从环境变量读取
                    self.api_key = os.getenv("GEMINI_API_KEY")
                    if self.api_key:
                        print(f"🔮 [Gemini] 从环境变量读取API Key: {self.api_key[:20]}...")
                    else:
                        print("❌ [Gemini] API Key 未设置")
                        raise ValueError(f"请在配置文件 {config_file} 中设置 gemini_api_key 或设置环境变量 GEMINI_API_KEY")
            except Exception as e:
                print(f"🔮 [Gemini] 读取配置文件失败: {e}")
                # 尝试从环境变量读取
                self.api_key = os.getenv("GEMINI_API_KEY")
                if self.api_key:
                    print(f"🔮 [Gemini] 从环境变量读取API Key: {self.api_key[:20]}...")
                else:
                    print("❌ [Gemini] API Key 未设置")
                    raise ValueError(f"请在配置文件 {config_file} 中设置 gemini_api_key 或设置环境变量 GEMINI_API_KEY")
        
        try:
            print("🔮 [Gemini] 正在配置 API 密钥...")
            # 使用默认配置，不指定自定义端点
            genai.configure(api_key=self.api_key)
            print("✅ [Gemini] API 密钥配置成功")
        except Exception as e:
            print(f"❌ [Gemini] API 密钥配置失败: {e}")
            raise
        
        # 配置生成参数
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1000,
        }
        
        # 安全设置
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        
        try:
            print("🔮 [Gemini] 正在初始化生成模型...")
            # 初始化模型
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            print("✅ [Gemini] 生成模型初始化成功")
        except Exception as e:
            print(f"❌ [Gemini] 生成模型初始化失败: {e}")
            raise
    
    def create_sql_prompt(self, user_query, schema_description):
        """创建用于生成SQL的提示词"""
        prompt = f"""你是一个专业的SQL查询助手。请根据用户的自然语言查询需求，生成对应的MySQL SQL查询语句。

数据库结构信息：
{schema_description}

重要要求：
1. 只生成SELECT查询语句，不要生成INSERT、UPDATE、DELETE等修改数据的语句
2. 确保生成的SQL语法正确，适用于MySQL数据库
3. 使用反引号包围表名和字段名以避免关键字冲突
4. 如果查询涉及多表，请正确使用JOIN语句
5. 只返回SQL语句，不要包含其他解释文字
6. 如果无法理解用户查询或数据库中没有相关表，请返回"ERROR: 无法生成对应的SQL查询"

用户查询: {user_query}

请生成对应的SQL查询语句："""
        
        return prompt
    
    def _clean_sql_response(self, response):
        """清理模型响应，提取纯SQL语句"""
        cleaned_sql = response.strip()
        
        # 移除markdown代码块标记
        if "```sql" in cleaned_sql:
            # 提取SQL代码块
            parts = cleaned_sql.split("```sql")
            if len(parts) > 1:
                sql_part = parts[1].split("```")[0]
                cleaned_sql = sql_part.strip()
        elif "```" in cleaned_sql:
            # 提取一般代码块
            parts = cleaned_sql.split("```")
            if len(parts) >= 3:
                sql_part = parts[1]
                cleaned_sql = sql_part.strip()
        
        # 移除可能的其他标记
        prefixes_to_remove = [
            "根据您的查询需求，生成的SQL语句如下：",
            "SQL语句：",
            "查询语句：",
            "生成的SQL：",
            "答案：",
            "结果：",
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned_sql.startswith(prefix):
                cleaned_sql = cleaned_sql[len(prefix):].strip()
        
        # 移除末尾的分号（如果有的话，我们统一处理）
        if cleaned_sql.endswith(';'):
            cleaned_sql = cleaned_sql[:-1].strip()
            
        print(f"🧹 [Gemini] 清理后的SQL: {cleaned_sql}")
        return cleaned_sql
    
    def generate_sql(self, user_query, schema_description, conversation_manager=None):
        """
        根据用户查询和数据库结构生成SQL
        
        Args:
            user_query: 用户的自然语言查询
            schema_description: 数据库结构描述
            conversation_manager: 对话管理器（可选，用于上下文支持）
            
        Returns:
            tuple: (success: bool, sql_or_error: str)
        """
        print(f"🔮 [Gemini] 开始生成SQL...")
        print(f"🔮 [Gemini] 用户查询: {user_query}")
        try:
            import threading
            import time
            
            result = {'success': False, 'response': None, 'error': None}
            
            # 判断是否使用上下文模式
            if conversation_manager:
                # 使用上下文对话模式 (注意：Gemini目前暂用单次模式，可扩展为chat session)
                prompt = conversation_manager.get_context_for_prompt(schema_description, user_query)
                print("📤 [Gemini] 使用上下文对话模式")
                print("📤 [Gemini] 发送的提示词（含历史上下文）:")
                print("-" * 60)
                print(prompt)
                print("-" * 60)
            else:
                # 使用传统单次对话模式
                print("🔮 [Gemini] 构建提示词...")
                prompt = self.create_sql_prompt(user_query, schema_description)
                
                print("📤 [Gemini] 使用单次对话模式")
                print("📤 [Gemini] 发送的提示词:")
                print("-" * 60)
                print(prompt)
                print("-" * 60)
            
            print("🔮 [Gemini] 调用 Gemini API 生成SQL...")
            
            def make_sql_request():
                try:
                    response = self.model.generate_content(prompt)
                    result['response'] = response
                    result['success'] = True
                except Exception as e:
                    result['error'] = e
            
            # 创建线程发送请求
            request_thread = threading.Thread(target=make_sql_request)
            request_thread.daemon = True
            request_thread.start()
            
            # 等待最多20秒
            timeout = 20
            print(f"🔮 [Gemini] 等待SQL生成响应（最多{timeout}秒）...")
            
            for i in range(timeout):
                if result['success'] or result['error']:
                    break
                time.sleep(1)
                if i % 5 == 0 and i > 0:  # 每5秒打印一次状态
                    print(f"🔮 [Gemini] SQL生成中... ({i}/{timeout}秒)")
            
            if result['error']:
                raise result['error']
            elif not result['success']:
                return False, "ERROR: Gemini API请求超时，请稍后重试"
            
            response = result['response']
            print("🔮 [Gemini] 收到 API 响应，正在处理...")
            
            if not response.text:
                print("❌ [Gemini] 收到空响应")
                return False, "ERROR: Gemini模型返回空响应"
            
            generated_sql = response.text.strip()
            print("📥 [Gemini] 完整原始响应:")
            print("-" * 60)
            print(generated_sql)
            print("-" * 60)
            
            # 清理SQL响应
            cleaned_sql = self._clean_sql_response(generated_sql)
            
            # 检查是否返回错误信息
            if cleaned_sql.startswith("ERROR:"):
                print(f"❌ [Gemini] 生成错误: {cleaned_sql}")
                return False, cleaned_sql
            
            # 基本的SQL格式检查
            if not cleaned_sql.upper().strip().startswith("SELECT"):
                print(f"❌ [Gemini] SQL格式错误: {cleaned_sql}")
                return False, "ERROR: 生成的不是SELECT查询语句"
            
            print(f"✅ [Gemini] SQL生成成功: {cleaned_sql}")
            return True, cleaned_sql
            
        except Exception as e:
            print(f"❌ [Gemini] 生成异常: {e}")
            print(f"❌ [Gemini] 异常类型: {type(e).__name__}")
            return False, f"ERROR: Gemini模型调用失败 - {str(e)}"
    
    def test_connection(self):
        """测试Gemini API连接"""
        print("🔮 [Gemini] 开始测试 API 连接...")
        
        import threading
        import time
        
        result = {'success': False, 'response': None, 'error': None}
        
        def make_request():
            try:
                print("🔮 [Gemini] 发送测试请求...")
                print(f"🔮 [Gemini] 使用模型: {self.model_name}")
                print(f"🔮 [Gemini] API Key: {self.api_key[:20]}...{self.api_key[-10:]}")
                
                test_prompt = "请回复：连接测试成功"
                print(f"📤 [Gemini] 测试提示词: {test_prompt}")
                
                response = self.model.generate_content(test_prompt)
                result['response'] = response
                result['success'] = True
                print("🔮 [Gemini] 收到响应，正在处理...")
            except Exception as e:
                result['error'] = e
                print(f"🔮 [Gemini] 请求异常: {e}")
                print(f"🔮 [Gemini] 异常详情: {type(e).__name__}: {str(e)}")
        
        # 创建线程发送请求
        request_thread = threading.Thread(target=make_request)
        request_thread.daemon = True
        request_thread.start()
        
        # 等待最多15秒
        timeout = 15
        print(f"🔮 [Gemini] 等待响应（最多{timeout}秒）...")
        
        for i in range(timeout):
            if result['success'] or result['error']:
                break
            time.sleep(1)
            if i % 3 == 0:  # 每3秒打印一次状态
                print(f"🔮 [Gemini] 等待中... ({i+1}/{timeout}秒)")
        
        if result['success']:
            response = result['response']
            if response and response.text:
                text = response.text.strip()
                print(f"📥 [Gemini] 测试响应: {text}")
                print(f"✅ [Gemini] 连接测试成功")
                return True
            else:
                print("❌ [Gemini] 连接失败: 无响应内容")
                return False
        elif result['error']:
            e = result['error']
            error_str = str(e)
            print(f"❌ [Gemini] 连接测试失败: {e}")
            print(f"❌ [Gemini] 错误类型: {type(e).__name__}")
            
            # 提供具体的错误提示
            if "UNAVAILABLE" in error_str:
                print("💡 [提示] 网络连接问题，可能的原因:")
                print("   - 网络代理/防火墙阻止连接")
                print("   - 网络超时或不稳定")
                print("   - Google服务被ISP阻止")
                print("   - 请尝试: python gemini_network_test.py")
            elif "PERMISSION_DENIED" in error_str or "INVALID_ARGUMENT" in error_str:
                print("💡 [提示] API Key问题:")
                print("   - 检查API Key是否正确")
                print("   - 确认账户是否有余额")
                print("   - 获取API Key: https://makersuite.google.com/app/apikey")
            
            return False
        else:
            print(f"❌ [Gemini] 连接超时（{timeout}秒），可能的原因:")
            print("   - 网络连接不稳定")
            print("   - API服务响应缓慢")
            print("   - 防火墙阻止连接")
            print("   - 建议切换到其他后端或稍后重试")
            return False
    
    def get_available_models(self):
        """获取可用的Gemini模型列表"""
        try:
            models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    models.append(model.name)
            return models
        except Exception as e:
            print(f"获取Gemini模型列表失败: {e}")
            return [
                "gemini-1.5-flash", 
                "gemini-1.5-pro", 
                "gemini-pro",
                "gemini-2.5-flash-preview-05-20",
                "gemini-2.0-flash-preview-image-generation"
            ]

if __name__ == '__main__':
    # 测试Gemini连接和SQL生成
    try:
        generator = GeminiSQLGenerator()
        
        # 测试连接
        if generator.test_connection():
            print("✓ Gemini模型连接正常")
            
            # 测试SQL生成
            test_schema = """
            表名: users
            字段信息:
              - id (int) PRI NO
              - name (varchar(100))  NO
              - email (varchar(100))  NO
              - age (int)  YES
            
            表名: orders
            字段信息:
              - id (int) PRI NO
              - user_id (int) MUL NO
              - product_name (varchar(200))  NO
              - amount (decimal(10,2))  NO
              - created_at (datetime)  NO
            """
            
            test_query = "查询所有用户的姓名和邮箱"
            success, result = generator.generate_sql(test_query, test_schema)
            
            if success:
                print(f"\n生成的SQL: {result}")
            else:
                print(f"\n生成失败: {result}")
        else:
            print("✗ Gemini模型连接失败")
            
    except Exception as e:
        print(f"错误: {e}")
        print("\n请确保已设置环境变量 GEMINI_API_KEY")
        print("设置方法：")
        print("Windows: set GEMINI_API_KEY=your_api_key")
        print("Linux/Mac: export GEMINI_API_KEY=your_api_key")
        print("获取API Key: https://makersuite.google.com/app/apikey")

    # 测试requests连接
    resp = requests.get("https://generativelanguage.googleapis.com")
    print(resp.status_code) 