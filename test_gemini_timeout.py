#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Gemini超时处理机制
"""

import time

def test_gemini_timeout():
    """测试Gemini的超时处理"""
    print("🧪 测试Gemini超时处理机制...")
    
    try:
        from gemini_sql_generator import GeminiSQLGenerator
        
        # 使用内置的API Key
        print("\n1. 创建Gemini生成器...")
        generator = GeminiSQLGenerator()
        
        print("\n2. 测试连接（带超时控制）...")
        start_time = time.time()
        result = generator.test_connection()
        end_time = time.time()
        
        print(f"\n⏱️ 连接测试耗时: {end_time - start_time:.2f}秒")
        
        if result:
            print("✅ 连接测试成功！")
            
            print("\n3. 测试SQL生成（带超时控制）...")
            test_schema = """
            表名: users
            字段信息:
              - id (int) PRI NO
              - name (varchar(100))  NO
              - email (varchar(100))  NO
            """
            
            start_time = time.time()
            success, sql_result = generator.generate_sql("查询所有用户", test_schema)
            end_time = time.time()
            
            print(f"\n⏱️ SQL生成耗时: {end_time - start_time:.2f}秒")
            
            if success:
                print(f"✅ SQL生成成功: {sql_result}")
            else:
                print(f"❌ SQL生成失败: {sql_result}")
                
        else:
            print("❌ 连接测试失败，跳过SQL生成测试")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_timeout() 