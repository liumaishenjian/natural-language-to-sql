import os
from openai import OpenAI
import json

class LLMSQLGenerator:
    """使用通义千问大模型生成SQL的类"""
    
    def __init__(self, model_name="qwen-plus"):
        """
        初始化大模型客户端
        model_name: 模型名称，可选 qwen-turbo, qwen-plus, qwen-max
        """
        self.model_name = model_name
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not self.api_key:
            raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
        
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
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 降低随机性，提高一致性
                max_tokens=1000
            )
            
            generated_sql = completion.choices[0].message.content.strip()
            
            # 检查是否返回错误信息
            if generated_sql.startswith("ERROR:"):
                return False, generated_sql
            
            # 基本的SQL格式检查
            if not generated_sql.upper().strip().startswith("SELECT"):
                return False, "ERROR: 生成的不是SELECT查询语句"
            
            return True, generated_sql
            
        except Exception as e:
            return False, f"ERROR: 大模型调用失败 - {str(e)}"
    
    def test_connection(self):
        """测试大模型API连接"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": "请回复：连接测试成功"}
                ],
                max_tokens=50
            )
            
            response = completion.choices[0].message.content.strip()
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