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
    
    def __init__(self, model_name="qwen2", base_url="http://localhost:11434"):
        """
        初始化Ollama客户端
        
        Args:
            model_name: 模型名称，如 qwen2, llama3, mistral 等
            base_url: Ollama API的基础URL
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/generate"
        self.models_url = f"{self.base_url}/api/tags"
        
    def test_connection(self):
        """测试Ollama连接和模型可用性"""
        try:
            # 检查Ollama服务是否运行
            response = requests.get(self.models_url, timeout=5)
            
            if response.status_code != 200:
                print(f"❌ Ollama服务连接失败，状态码: {response.status_code}")
                return False
            
            # 检查可用模型
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            
            print(f"✅ Ollama服务连接成功")
            print(f"📋 可用模型: {', '.join(available_models) if available_models else '无'}")
            
            # 检查指定模型是否可用
            model_available = any(self.model_name in model for model in available_models)
            
            if not model_available:
                print(f"⚠️  模型 '{self.model_name}' 未找到")
                if available_models:
                    print(f"💡 建议使用: {available_models[0]}")
                    # 自动使用第一个可用模型
                    self.model_name = available_models[0].split(':')[0]
                    print(f"🔄 自动切换到模型: {self.model_name}")
                else:
                    print("❌ 没有可用的模型，请先用 'ollama pull qwen2' 下载模型")
                    return False
            else:
                print(f"✅ 模型 '{self.model_name}' 可用")
            
            # 测试模型响应
            test_response = self._call_ollama("请回复：连接测试成功")
            if test_response:
                print(f"🎯 模型响应测试: {test_response[:50]}...")
                return True
            else:
                print("❌ 模型响应测试失败")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到Ollama服务")
            print("💡 请确保Ollama正在运行: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Ollama连接测试失败: {e}")
            return False
    
    def _call_ollama(self, prompt, max_tokens=1000):
        """调用Ollama API"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=30  # 本地模型可能较慢
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"Ollama API错误: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"调用Ollama失败: {e}")
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
    
    def generate_sql(self, user_query, schema_description):
        """
        根据用户查询和数据库结构生成SQL
        
        Args:
            user_query: 用户的自然语言查询
            schema_description: 数据库结构描述
            
        Returns:
            tuple: (success: bool, sql_or_error: str)
        """
        try:
            prompt = self.create_sql_prompt(user_query, schema_description)
            
            print(f"🤖 正在调用本地模型 {self.model_name} 生成SQL...")
            generated_response = self._call_ollama(prompt)
            
            if not generated_response:
                return False, "ERROR: 本地模型调用失败"
            
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
        # 移除可能的markdown代码块
        if "```sql" in response:
            # 提取SQL代码块
            parts = response.split("```sql")
            if len(parts) > 1:
                sql_part = parts[1].split("```")[0]
                return sql_part.strip()
        elif "```" in response:
            # 提取一般代码块
            parts = response.split("```")
            if len(parts) >= 3:
                sql_part = parts[1]
                return sql_part.strip()
        
        # 如果没有代码块，尝试查找SELECT语句
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith('SELECT'):
                return line
        
        # 如果找不到明确的SQL，返回清理后的整个响应
        cleaned = response.strip()
        
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
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        return cleaned
    
    def get_available_models(self):
        """获取Ollama中可用的模型列表"""
        try:
            response = requests.get(self.models_url, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                return [model['name'] for model in models_data.get('models', [])]
            return []
        except:
            return []

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