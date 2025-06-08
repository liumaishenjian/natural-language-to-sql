#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试Gemini API - 不使用封装类
"""

import google.generativeai as genai
import time

def test_gemini_direct():
    """直接测试Gemini API"""
    print("🔮 直接测试Gemini API...")
    
    api_key = "AIzaSyCnjKgURS7Dfu_VyOBgpTllptrZNkNQ53g"
    
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
    
    try:
        print("1️⃣ 配置API Key...")
        genai.configure(api_key=api_key)
        print("✅ API Key配置成功")
        
        print("2️⃣ 创建模型实例...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ 模型实例创建成功")
        
        print("3️⃣ 发送简单请求...")
        start_time = time.time()
        
        response = model.generate_content("Hello, please reply with 'Connection successful'")
        
        end_time = time.time()
        print(f"⏱️ 请求耗时: {end_time - start_time:.2f}秒")
        
        if response and response.text:
            print(f"✅ 请求成功!")
            print(f"📝 响应内容: {response.text}")
            return True
        else:
            print("❌ 响应为空")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        print(f"🔍 错误类型: {type(e).__name__}")
        
        # 详细错误分析
        error_str = str(e).lower()
        if "unavailable" in error_str:
            print("💡 这是网络连接问题")
        elif "permission" in error_str or "invalid" in error_str:
            print("💡 这是API Key权限问题")
        elif "timeout" in error_str:
            print("💡 这是超时问题")
        else:
            print("💡 这是其他类型的错误")
            
        return False

def test_different_models():
    """测试不同的模型"""
    print("\n🧪 测试不同模型...")
    
    api_key = "AIzaSyCnjKgURS7Dfu_VyOBgpTllptrZNkNQ53g"
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    genai.configure(api_key=api_key)
    
    for model_name in models:
        print(f"\n📱 测试模型: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            
            if response and response.text:
                print(f"✅ {model_name} 工作正常: {response.text[:50]}...")
            else:
                print(f"❌ {model_name} 响应为空")
                
        except Exception as e:
            print(f"❌ {model_name} 失败: {e}")

if __name__ == "__main__":
    print("🚀 Gemini直接连接测试")
    print("=" * 50)
    
    # 测试基本连接
    success = test_gemini_direct()
    
    if success:
        # 如果基本连接成功，测试不同模型
        test_different_models()
    else:
        print("\n💡 建议:")
        print("1. 检查网络连接")
        print("2. 确认API Key是否正确")
        print("3. 尝试使用VPN或更换网络")
        print("4. 检查防火墙设置") 