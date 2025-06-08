#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用本地Ollama大模型生成SQL的模块
支持qwen2等本地部署的大模型
"""

import requests
import json
import time

class OllamaLLMGenerator:
    """使用本地Ollama大模型生成SQL的类"""
    
    def __init__(self, model_name="qwen2", api_url="http://localhost:11434"):
        """
        初始化Ollama客户端
        
        Args:
            model_name: 模型名称，如 qwen2, llama3, mistral 等
            api_url: Ollama API的基础URL
        """
        self.model_name = model_name
        self.api_url = f"{api_url}/api/generate"
        self.available_models = None
        
    def test_connection(self, max_retries=3, retry_delay=2):
        """测试与Ollama的连接
        
        Args:
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
        """
        for attempt in range(max_retries):
            try:
                # 1. 首先检查Ollama服务是否在运行
                health_check = requests.get(
                    "http://localhost:11434/",
                    timeout=5
                )
                if health_check.status_code != 200:
                    print(f"⚠️ Ollama服务未正常运行 (状态码: {health_check.status_code})")
                    if attempt < max_retries - 1:
                        print(f"🔄 {attempt + 1}/{max_retries} 次重试中...")
                        time.sleep(retry_delay)
                        continue
                    return False
                
                print("✅ Ollama服务连接成功")
                
                # 2. 获取可用模型列表
                models = self.get_available_models()
                if not models:
                    print("⚠️ 无法获取模型列表")
                    if attempt < max_retries - 1:
                        print(f"🔄 {attempt + 1}/{max_retries} 次重试中...")
                        time.sleep(retry_delay)
                        continue
                    return False
                
                print(f"📋 可用模型: {', '.join(models)}")
                
                # 3. 检查指定模型是否可用
                model_available = False
                for model in models:
                    if self.model_name in model:
                        model_available = True
                        break
                
                if not model_available:
                    print(f"⚠️ 模型 '{self.model_name}' 未找到")
                    print(f"💡 可用模型: {', '.join(models)}")
                    return False
                
                print(f"✅ 模型 '{self.model_name}' 可用")
                
                # 4. 测试模型响应
                test_prompt = "请回复：连接测试成功"
                print(f"📤 [Ollama] 测试提示词: {test_prompt}")
                
                test_response = self._call_ollama(
                    test_prompt,
                    timeout=10
                )
                
                if test_response and "连接测试成功" in test_response:
                    print(f"📥 [Ollama] 测试响应: {test_response}")
                    return True
                else:
                    print("⚠️ 模型响应测试失败")
                    if attempt < max_retries - 1:
                        print(f"🔄 {attempt + 1}/{max_retries} 次重试中...")
                        time.sleep(retry_delay)
                        continue
                    return False
                    
            except requests.exceptions.ConnectionError:
                print("⚠️ 无法连接到Ollama服务")
                print("💡 请确保Ollama服务正在运行: ollama serve")
                if attempt < max_retries - 1:
                    print(f"🔄 {attempt + 1}/{max_retries} 次重试中...")
                    time.sleep(retry_delay)
                    continue
                return False
                
            except requests.exceptions.Timeout:
                print("⚠️ 连接超时")
                if attempt < max_retries - 1:
                    print(f"🔄 {attempt + 1}/{max_retries} 次重试中...")
                    time.sleep(retry_delay)
                    continue
                return False
                
            except Exception as e:
                print(f"⚠️ 连接测试失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"🔄 {attempt + 1}/{max_retries} 次重试中...")
                    time.sleep(retry_delay)
                    continue
                return False
        
        return False
    
    def get_available_models(self):
        """获取可用的模型列表"""
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models_data = response.json().get('models', [])
                # 提取模型名称
                model_names = [model.get('name', '') for model in models_data if model.get('name')]
                self.available_models = model_names
                return model_names
            return []
        except Exception as e:
            print(f"⚠️ 获取模型列表失败: {str(e)}")
            return []
    
    def _call_ollama(self, prompt, timeout=30):
        """调用Ollama API
        
        Args:
            prompt: 提示词
            timeout: 超时时间（秒）
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"⚠️ API调用失败 (状态码: {response.status_code})")
                return None
                
        except requests.exceptions.Timeout:
            print(f"⚠️ API调用超时 (>{timeout}秒)")
            return None
            
        except Exception as e:
            print(f"⚠️ API调用错误: {str(e)}")
            return None
    
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
5. 只返回SQL语句，不要包含其他解释文字或markdown格式
6. 如果无法理解用户查询或数据库中没有相关表，请返回"ERROR: 无法生成对应的SQL查询"

用户查询: {user_query}

请生成对应的SQL查询语句："""
        
        return prompt
    
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
        try:
            # 判断是否使用上下文模式
            if conversation_manager:
                # Ollama使用上下文提示词模式
                prompt = conversation_manager.get_context_for_prompt(schema_description, user_query)
                print("📤 [Ollama] 使用上下文对话模式")
                print("📤 [Ollama] 发送的提示词（含历史上下文）:")
            else:
                # 使用传统单次对话模式
                prompt = self.create_sql_prompt(user_query, schema_description)
                print("📤 [Ollama] 使用单次对话模式")
                print("📤 [Ollama] 发送的提示词:")
            
            print("-" * 60)
            print(prompt)
            print("-" * 60)
            
            print(f"🤖 正在调用本地模型 {self.model_name} 生成SQL...")
            generated_response = self._call_ollama(prompt)
            
            if not generated_response:
                return False, "ERROR: 本地模型调用失败"
            
            print("📥 [Ollama] 完整原始响应:")
            print("-" * 60)
            print(generated_response)
            print("-" * 60)
            
            # 清理响应，提取SQL语句
            generated_sql = self._extract_sql_from_response(generated_response)
            
            # 检查是否返回错误信息
            if generated_sql.startswith("ERROR:"):
                return False, generated_sql
            
            # 基本的SQL格式检查
            if not generated_sql.upper().strip().startswith("SELECT"):
                return False, "ERROR: 生成的不是SELECT查询语句"
            
            return True, generated_sql
            
        except Exception as e:
            return False, f"ERROR: 本地模型调用失败 - {str(e)}"
    
    def _extract_sql_from_response(self, response):
        """从模型响应中提取SQL语句"""
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
        
        # 如果没有代码块，尝试查找SELECT语句
        if not cleaned_sql.upper().startswith('SELECT'):
            lines = cleaned_sql.split('\n')
            for line in lines:
                line = line.strip()
                if line.upper().startswith('SELECT'):
                    cleaned_sql = line
                    break
        
        # 移除常见的前缀词
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
            
        print(f"🧹 [Ollama] 清理后的SQL: {cleaned_sql}")
        return cleaned_sql

def test_ollama_generator():
    """测试Ollama生成器"""
    print("=== 测试本地Ollama大模型 ===\n")
    
    # 创建生成器
    generator = OllamaLLMGenerator("qwen2")
    
    # 测试连接
    if not generator.test_connection():
        print("\n❌ Ollama连接失败")
        print("\n🔧 解决方案:")
        print("1. 确保Ollama已安装: https://ollama.ai/")
        print("2. 启动Ollama服务: ollama serve")
        print("3. 下载模型: ollama pull qwen2")
        return False
    
    # 测试SQL生成
    test_schema = """
表名: users
字段信息:
  - id (int) PRI NO
  - name (varchar(100))  NO
  - email (varchar(100))  NO
  - age (int)  YES
  - city (varchar(50))  YES

表名: orders
字段信息:
  - id (int) PRI NO
  - user_id (int) MUL NO
  - product_name (varchar(200))  NO
  - amount (decimal(10,2))  NO
  - created_at (datetime)  NO
"""
    
    test_queries = [
        "查询所有用户的姓名和邮箱",
        "查找年龄大于25岁的用户",
        "统计每个城市的用户数量"
    ]
    
    print(f"\n🧪 测试SQL生成功能:")
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试 {i}: {query} ---")
        success, result = generator.generate_sql(query, test_schema)
        
        if success:
            print(f"✅ 生成成功: {result}")
        else:
            print(f"❌ 生成失败: {result}")
    
    return True

if __name__ == '__main__':
    test_ollama_generator() 