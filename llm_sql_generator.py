import os
import configparser
from openai import OpenAI
import json

class LLMSQLGenerator:
    """使用通义千问大模型生成SQL的类"""
    
    def __init__(self, model_name="qwen-plus", api_key=None, config_file="config.ini"):
        """
        初始化大模型客户端
        model_name: 模型名称，可选 qwen-turbo, qwen-plus, qwen-max
        api_key: API密钥，如果为None则从配置文件或环境变量获取
        config_file: 配置文件路径
        """
        self.model_name = model_name
        
        # 获取API Key的优先级：传入参数 > 配置文件 > 环境变量
        if api_key:
            self.api_key = api_key
            print(f"🔮 [Qwen] 使用传入的API Key: {self.api_key[:20]}...")
        else:
            # 尝试从配置文件读取
            try:
                config = configparser.ConfigParser()
                config.read(config_file, encoding='utf-8')
                self.api_key = config.get('api_keys', 'qwen_api_key', fallback=None)
                if self.api_key and self.api_key.strip():
                    print(f"🔮 [Qwen] 从配置文件读取API Key: {self.api_key[:20]}...")
                else:
                    # 尝试从环境变量读取
                    self.api_key = os.getenv("DASHSCOPE_API_KEY")
                    if self.api_key:
                        print(f"🔮 [Qwen] 从环境变量读取API Key: {self.api_key[:20]}...")
                    else:
                        print("❌ [Qwen] API Key 未设置")
                        raise ValueError(f"请在配置文件 {config_file} 中设置 qwen_api_key 或设置环境变量 DASHSCOPE_API_KEY")
            except Exception as e:
                print(f"🔮 [Qwen] 读取配置文件失败: {e}")
                # 尝试从环境变量读取
                self.api_key = os.getenv("DASHSCOPE_API_KEY")
                if self.api_key:
                    print(f"🔮 [Qwen] 从环境变量读取API Key: {self.api_key[:20]}...")
                else:
                    print("❌ [Qwen] API Key 未设置")
                    raise ValueError(f"请在配置文件 {config_file} 中设置 qwen_api_key 或设置环境变量 DASHSCOPE_API_KEY")
        
        # 使用兼容OpenAI的接口
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
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
            
        print(f"🧹 [Qwen] 清理后的SQL: {cleaned_sql}")
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
        try:
            # 判断是否使用上下文模式
            if conversation_manager:
                # 使用上下文对话模式
                messages = conversation_manager.get_messages_for_openai_format(schema_description, user_query)
                print("📤 [Qwen] 使用上下文对话模式")
                print("📤 [Qwen] 发送的消息数组:")
                print("-" * 60)
                for i, msg in enumerate(messages):
                    print(f"消息 {i+1} ({msg['role']}):")
                    print(msg['content'][:200] + ('...' if len(msg['content']) > 200 else ''))
                    print()
                print("-" * 60)
                
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=1000
                )
            else:
                # 使用传统单次对话模式
                prompt = self.create_sql_prompt(user_query, schema_description)
                
                print("📤 [Qwen] 使用单次对话模式")
                print("📤 [Qwen] 发送的提示词:")
                print("-" * 60)
                print(prompt)
                print("-" * 60)
                
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # 降低随机性，提高一致性
                    max_tokens=1000
                )
            
            generated_sql = completion.choices[0].message.content.strip()
            
            print("📥 [Qwen] 完整原始响应:")
            print("-" * 60)
            print(generated_sql)
            print("-" * 60)
            
            # 清理SQL响应
            cleaned_sql = self._clean_sql_response(generated_sql)
            
            # 检查是否返回错误信息
            if cleaned_sql.startswith("ERROR:"):
                return False, cleaned_sql
            
            # 基本的SQL格式检查
            if not cleaned_sql.upper().strip().startswith("SELECT"):
                return False, "ERROR: 生成的不是SELECT查询语句"
            
            return True, cleaned_sql
            
        except Exception as e:
            return False, f"ERROR: 大模型调用失败 - {str(e)}"
    
    def test_connection(self):
        """测试大模型API连接"""
        try:
            test_prompt = "请回复：连接测试成功"
            print(f"📤 [Qwen] 测试提示词: {test_prompt}")
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": test_prompt}
                ],
                max_tokens=50
            )
            
            response = completion.choices[0].message.content.strip()
            print(f"📥 [Qwen] 测试响应: {response}")
            print(f"大模型连接测试: {response}")
            return True
            
        except Exception as e:
            print(f"大模型连接失败: {e}")
            return False

if __name__ == '__main__':
    # 测试大模型连接和SQL生成
    try:
        generator = LLMSQLGenerator()
        
        # 测试连接
        if generator.test_connection():
            print("✓ 大模型连接正常")
            
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
            print("✗ 大模型连接失败")
            
    except Exception as e:
        print(f"错误: {e}")
        print("\n请确保已设置环境变量 DASHSCOPE_API_KEY")
        print("设置方法：")
        print("Windows: set DASHSCOPE_API_KEY=your_api_key")
        print("Linux/Mac: export DASHSCOPE_API_KEY=your_api_key") 