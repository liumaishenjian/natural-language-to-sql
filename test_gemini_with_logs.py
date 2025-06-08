#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Gemini日志和错误处理
"""

import os
import sys

def test_gemini_initialization():
    """测试Gemini初始化过程"""
    print("🧪 测试Gemini初始化过程...")
    
    try:
        # 测试无API Key的情况
        print("\n1. 测试无API Key的情况:")
        os.environ.pop('GEMINI_API_KEY', None)  # 确保没有环境变量
        
        from gemini_sql_generator import GeminiSQLGenerator
        try:
            generator = GeminiSQLGenerator()
            print("❌ 应该抛出异常但没有")
        except ValueError as e:
            print(f"✅ 正确抛出异常: {e}")
        
        # 测试有API Key但网络问题的情况
        print("\n2. 测试API Key设置但可能网络问题:")
        test_api_key = "AIzaSyCD69vPZlXX0mhQ6escNqFpGHdxqdEZrWQ"  # 测试Key
        try:
            generator = GeminiSQLGenerator(api_key=test_api_key)
            print("✅ 初始化成功")
            
            # 测试连接
            print("\n3. 测试连接:")
            result = generator.test_connection()
            if result:
                print("✅ 连接测试成功")
            else:
                print("❌ 连接测试失败（这是预期的，因为可能是测试Key）")
                
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")

def test_main_initialization():
    """测试main.py的初始化"""
    print("\n🧪 测试main.py的初始化过程...")
    
    try:
        from main import NaturalLanguageToSQL
        
        print("\n1. 测试Gemini后端初始化:")
        test_api_key = "AIzaSyCD69vPZlXX0mhQ6escNqFpGHdxqdEZrWQ"
        
        sql_tool = NaturalLanguageToSQL(
            config_file='config.ini',
            llm_backend='gemini',
            model_name='gemini-1.5-flash',
            api_key=test_api_key
        )
        
        print("✅ NaturalLanguageToSQL实例创建成功")
        
        # 不运行完整初始化，因为需要数据库连接
        print("ℹ️  跳过完整初始化（需要数据库连接）")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🔍 Gemini日志和错误处理测试")
    print("=" * 50)
    
    test_gemini_initialization()
    test_main_initialization()
    
    print("\n" + "=" * 50)
    print("🔍 测试完成！")
    print("\n💡 如果看到详细的日志输出和友好的错误提示，")
    print("   说明日志系统工作正常。")
    print("\n📝 查看完整的故障排除指南:")
    print("   GEMINI_TROUBLESHOOTING.md") 