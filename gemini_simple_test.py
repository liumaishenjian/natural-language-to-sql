#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Gemini测试 - 排查网络问题
"""

import os
import requests
import google.generativeai as genai

def test_network():
    """测试网络连接"""
    print("🌐 测试网络连接...")
    
    urls = [
        "https://www.google.com",
        "https://generativelanguage.googleapis.com",
        "https://ai.google.dev"
    ]
    
    for url in urls:
        try:
            print(f"  测试 {url}...")
            response = requests.get(url, timeout=5)
            print(f"  ✅ {url} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url} - 失败: {e}")

def test_gemini_direct():
    """直接测试Gemini API"""
    print("\n🔮 直接测试Gemini API...")
    
    api_key = "AIzaSyCnjKgURS7Dfu_VyOBgpTllptrZNkNQ53g"
    
    try:
        print("  配置API...")
        genai.configure(api_key=api_key)
        
        print("  创建模型...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("  发送简单请求...")
        response = model.generate_content("Hello")
        
        if response.text:
            print(f"  ✅ 成功: {response.text[:50]}...")
        else:
            print("  ❌ 空响应")
            
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print(f"  错误类型: {type(e).__name__}")

def test_with_proxy():
    """测试代理设置"""
    print("\n🔧 测试代理设置...")
    
    # 尝试设置代理环境变量
    proxy_configs = [
        {},  # 无代理
        {"http_proxy": "127.0.0.1:7890", "https_proxy": "127.0.0.1:7890"},  # 常见代理端口
        {"http_proxy": "127.0.0.1:8080", "https_proxy": "127.0.0.1:8080"},
    ]
    
    for i, proxy in enumerate(proxy_configs):
        print(f"  配置 {i+1}: {proxy if proxy else '无代理'}")
        
        # 临时设置环境变量
        for key, value in proxy.items():
            os.environ[key] = value
        
        try:
            response = requests.get("https://www.google.com", timeout=3)
            print(f"    ✅ 代理配置 {i+1} 可用")
            break
        except Exception as e:
            print(f"    ❌ 代理配置 {i+1} 失败: {e}")
        finally:
            # 清理环境变量
            for key in proxy.keys():
                os.environ.pop(key, None)

if __name__ == "__main__":
    print("🔍 Gemini网络连接诊断")
    print("=" * 40)
    
    test_network()
    test_gemini_direct()
    test_with_proxy()
    
    print("\n💡 建议:")
    print("1. 如果网络测试都失败，检查网络连接")
    print("2. 如果只有Gemini失败，可能需要代理")
    print("3. 考虑暂时使用其他AI后端")
    print("4. 检查防火墙设置") 