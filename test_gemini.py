#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Google Gemini模型集成
"""

import os
import sys

def test_gemini_connection():
    """测试Gemini连接"""
    print("🔮 测试Google Gemini模型集成")
    print("=" * 50)
    
    # 检查API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ 错误: 未设置GEMINI_API_KEY环境变量")
        print("\n🔧 请按以下步骤设置:")
        print("1. 访问 https://makersuite.google.com/app/apikey")
        print("2. 获取您的API Key")
        print("3. 设置环境变量:")
        print("   Windows: set GEMINI_API_KEY=your_api_key")
        print("   Linux/Mac: export GEMINI_API_KEY=your_api_key")
        return False
    
    print(f"✅ API Key已设置: {api_key[:10]}...")
    
    # 测试导入
    try:
        from gemini_sql_generator import GeminiSQLGenerator
        print("✅ Gemini模块导入成功")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("💡 请安装依赖: pip install google-generativeai")
        return False
    
    # 测试连接
    try:
        generator = GeminiSQLGenerator("gemini-1.5-flash")
        print("✅ Gemini客户端创建成功")
        
        if generator.test_connection():
            print("✅ Gemini API连接成功")
        else:
            print("❌ Gemini API连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False
    
    # 测试SQL生成
    print("\n🧪 测试SQL生成功能...")
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
    
    test_queries = [
        "查询所有用户的姓名和邮箱",
        "统计每个用户的订单数量",
        "查找最近一周的订单"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 测试查询 {i}: {query}")
        try:
            success, result = generator.generate_sql(query, test_schema)
            if success:
                print(f"✅ 生成成功: {result}")
            else:
                print(f"❌ 生成失败: {result}")
        except Exception as e:
            print(f"❌ 生成异常: {e}")
    
    # 测试可用模型
    print("\n📋 获取可用模型...")
    try:
        models = generator.get_available_models()
        print(f"✅ 找到 {len(models)} 个可用模型:")
        for model in models[:5]:  # 只显示前5个
            print(f"   - {model}")
        if len(models) > 5:
            print(f"   ... 还有 {len(models) - 5} 个模型")
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
    
    print("\n🎉 Gemini集成测试完成！")
    return True

def test_web_integration():
    """测试Web集成"""
    print("\n🌐 测试Web服务器集成")
    print("=" * 30)
    
    try:
        from main import NaturalLanguageToSQL
        
        # 测试使用Gemini后端创建工具
        tool = NaturalLanguageToSQL(
            config_file='config.ini',
            llm_backend='gemini',
            model_name='gemini-1.5-flash'
        )
        print("✅ 主工具类创建成功")
        
        # 测试初始化（不连接数据库，只测试AI模型）
        if tool.sql_generator.test_connection():
            print("✅ Web集成测试通过")
            return True
        else:
            print("❌ Web集成测试失败")
            return False
            
    except Exception as e:
        print(f"❌ Web集成测试异常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Gemini模型集成测试套件")
    print("=" * 60)
    
    # 测试基本连接
    basic_test = test_gemini_connection()
    
    if basic_test:
        # 测试Web集成
        web_test = test_web_integration()
        
        if web_test:
            print("\n🎊 所有测试通过！可以开始使用Gemini模型了")
            print("\n🚀 启动建议:")
            print("1. 使用命令行: python main.py --backend gemini")
            print("2. 使用Web界面: python web_server.py --backend gemini")
            print("3. 使用专用脚本: start_web_gemini.bat")
        else:
            print("\n⚠️  Web集成测试失败，但基本功能正常")
    else:
        print("\n❌ 基本测试失败，请检查配置")
        sys.exit(1) 