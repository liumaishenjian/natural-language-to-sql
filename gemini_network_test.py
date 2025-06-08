#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini网络连接诊断工具
用于排查Gemini API连接问题
"""

import os
import time
import requests
import socket
from urllib.parse import urlparse
import google.generativeai as genai

def test_basic_network():
    """测试基本网络连接"""
    print("🌐 [网络] 测试基本网络连接...")
    
    # 测试Google DNS
    try:
        print("🌐 [网络] 测试Google DNS (8.8.8.8)...")
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        print("✅ [网络] Google DNS连接正常")
    except Exception as e:
        print(f"❌ [网络] Google DNS连接失败: {e}")
    
    # 测试Google.com
    try:
        print("🌐 [网络] 测试Google.com...")
        response = requests.get("https://www.google.com", timeout=10)
        print(f"✅ [网络] Google.com连接正常 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ [网络] Google.com连接失败: {e}")
    
    # 测试Gemini API域名
    try:
        print("🌐 [网络] 测试generativelanguage.googleapis.com...")
        response = requests.get("https://generativelanguage.googleapis.com", timeout=10)
        print(f"✅ [网络] Gemini API域名连接正常 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ [网络] Gemini API域名连接失败: {e}")

def test_gemini_api_key(api_key):
    """测试Gemini API Key"""
    print(f"🔑 [API] 测试API Key: {api_key[:10]}...")
    
    try:
        # 配置API Key
        print("🔑 [API] 配置API Key...")
        genai.configure(api_key=api_key)
        
        # 列出可用模型（这是一个轻量级的测试）
        print("🔑 [API] 获取可用模型列表...")
        models = list(genai.list_models())
        print(f"✅ [API] API Key有效，找到 {len(models)} 个模型")
        
        # 显示前几个模型
        for i, model in enumerate(models[:3]):
            print(f"   - {model.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ [API] API Key测试失败: {e}")
        print(f"❌ [API] 错误类型: {type(e).__name__}")
        return False

def test_model_generation(api_key, model_name="gemini-1.5-flash"):
    """测试模型生成"""
    print(f"🤖 [模型] 测试模型生成: {model_name}")
    
    try:
        genai.configure(api_key=api_key)
        
        # 创建模型实例
        print("🤖 [模型] 创建模型实例...")
        model = genai.GenerativeModel(model_name)
        
        # 简单测试
        print("🤖 [模型] 发送简单测试请求...")
        response = model.generate_content("你好")
        
        if response and response.text:
            print(f"✅ [模型] 模型响应正常: {response.text[:50]}...")
            return True
        else:
            print("❌ [模型] 模型返回空响应")
            return False
            
    except Exception as e:
        print(f"❌ [模型] 模型测试失败: {e}")
        print(f"❌ [模型] 错误类型: {type(e).__name__}")
        
        # 详细错误信息
        if "UNAVAILABLE" in str(e):
            print("💡 [提示] 网络连接问题，可能是:")
            print("   - 网络代理设置问题")
            print("   - 防火墙阻止连接")
            print("   - 网络超时")
            print("   - ISP阻止Google服务")
        elif "PERMISSION_DENIED" in str(e):
            print("💡 [提示] API Key权限问题")
        elif "INVALID_ARGUMENT" in str(e):
            print("💡 [提示] API Key格式或参数错误")
        
        return False

def main():
    """主函数"""
    print("🔍 Gemini网络连接诊断工具")
    print("=" * 50)
    
    # 1. 测试基本网络
    test_basic_network()
    print()
    
    # 2. 获取API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ [配置] 未找到环境变量 GEMINI_API_KEY")
        api_key = input("请输入您的Gemini API Key: ").strip()
    
    if not api_key:
        print("❌ [配置] 未提供API Key，退出测试")
        return
    
    # 3. 测试API Key
    if test_gemini_api_key(api_key):
        print()
        # 4. 测试模型生成
        test_model_generation(api_key)
    
    print()
    print("🔍 诊断完成！")
    
    # 5. 网络代理提示
    print("\n💡 如果遇到网络问题，可以尝试:")
    print("   1. 检查网络代理设置")
    print("   2. 临时关闭防火墙/VPN")
    print("   3. 使用手机热点测试")
    print("   4. 检查API Key是否正确")
    print("   5. 确认账户是否有余额")

if __name__ == "__main__":
    main() 