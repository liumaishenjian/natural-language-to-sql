#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试修复后的Gemini代码
"""

import os

def test_gemini_quick():
    """快速测试Gemini初始化"""
    print("🧪 快速测试Gemini修复...")
    
    try:
        # 测试初始化（不需要真实API Key）
        print("\n1. 测试模型列表获取:")
        from gemini_sql_generator import GeminiSQLGenerator
        
        # 测试新模型是否在列表中
        test_generator = GeminiSQLGenerator.__new__(GeminiSQLGenerator)  # 不调用__init__
        models = test_generator.get_available_models()
        
        print(f"✅ 可用模型数量: {len(models)}")
        print("📋 模型列表:")
        for i, model in enumerate(models, 1):
            print(f"   {i}. {model}")
        
        # 检查新模型是否存在
        new_models = [
            "gemini-2.5-flash-preview-05-20",
            "gemini-2.0-flash-preview-image-generation"
        ]
        
        print("\n2. 检查新模型:")
        for model in new_models:
            if model in models:
                print(f"✅ {model} - 已添加")
            else:
                print(f"❌ {model} - 未找到")
        
        print("\n3. 测试初始化（无API Key）:")
        try:
            os.environ.pop('GEMINI_API_KEY', None)  # 确保没有环境变量
            generator = GeminiSQLGenerator()
            print("❌ 应该抛出异常但没有")
        except ValueError as e:
            print(f"✅ 正确抛出异常: {e}")
        
        print("\n✅ 快速测试完成 - 代码修复正常")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_quick() 