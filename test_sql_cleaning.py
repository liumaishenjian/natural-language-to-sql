#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试大模型沟通日志输出功能和SQL清理功能
"""

from llm_sql_generator import LLMSQLGenerator

def test_qwen_cleaning():
    """测试通义千问的SQL清理功能"""
    print("🧪 测试通义千问SQL清理功能...")
    print("=" * 80)
    
    try:
        # 创建生成器（从配置文件读取API Key）
        generator = LLMSQLGenerator("qwen-plus", config_file="config.ini")
        
        print("\n1️⃣ 测试连接...")
        if generator.test_connection():
            print("\n2️⃣ 测试SQL生成和清理...")
            
            # 模拟数据库结构
            test_schema = """
表名: sys_user
字段信息:
  - id (bigint) PRI NO
  - username (varchar(50)) NO
  - real_name (varchar(100)) YES
  - email (varchar(100)) YES
"""
            
            # 测试查询
            test_query = "查询所有用户的用户名和真实姓名"
            
            print(f"\n🔍 测试查询: {test_query}")
            success, result = generator.generate_sql(test_query, test_schema)
            
            if success:
                print(f"\n✅ 生成成功！")
                print(f"🎯 最终SQL: {result}")
            else:
                print(f"\n❌ 生成失败: {result}")
        else:
            print("❌ 连接测试失败")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == '__main__':
    test_qwen_cleaning() 