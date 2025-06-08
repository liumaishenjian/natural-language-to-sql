#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web API的API Key设置功能
"""

import requests
import json
import time

def test_web_api_key():
    """测试Web API的API Key功能"""
    print("🌐 测试Web API的API Key设置功能")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # 测试API Key设置
    test_data = {
        "backend": "gemini",
        "model": "gemini-1.5-flash",
        "api_key": "test_fake_api_key_for_testing"
    }
    
    print("📝 测试数据:")
    print(f"  - 后端: {test_data['backend']}")
    print(f"  - 模型: {test_data['model']}")
    print(f"  - API Key: {test_data['api_key'][:10]}...")
    
    try:
        print("\n🔄 发送初始化请求...")
        response = requests.post(
            f"{base_url}/api/initialize",
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=10
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 请求成功发送")
            print(f"📊 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                print("🎉 初始化成功!")
            else:
                print(f"⚠️  初始化失败: {data.get('message', '未知错误')}")
                print("💡 这可能是因为使用了测试API Key")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保Web服务器正在运行")
        print("💡 启动命令: python web_server.py")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_different_backends():
    """测试不同后端的API Key设置"""
    print("\n🔄 测试不同后端的API Key设置")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    test_cases = [
        {
            "name": "通义千问",
            "backend": "qwen_api",
            "model": "qwen-plus",
            "api_key": "test_qwen_api_key"
        },
        {
            "name": "Google Gemini",
            "backend": "gemini", 
            "model": "gemini-1.5-flash",
            "api_key": "test_gemini_api_key"
        },
        {
            "name": "Ollama (无需API Key)",
            "backend": "ollama",
            "model": "qwen2",
            "api_key": None
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 测试 {case['name']}:")
        
        request_data = {
            "backend": case["backend"],
            "model": case["model"]
        }
        
        if case["api_key"]:
            request_data["api_key"] = case["api_key"]
        
        try:
            response = requests.post(
                f"{base_url}/api/initialize",
                headers={'Content-Type': 'application/json'},
                json=request_data,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                status = "✅ 成功" if data.get('success') else "⚠️  失败"
                print(f"  状态: {status}")
                print(f"  消息: {data.get('message', '无消息')}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        
        time.sleep(1)  # 避免请求过于频繁

if __name__ == "__main__":
    print("🧪 Web API Key 设置功能测试")
    print("=" * 60)
    print("⚠️  注意: 此测试使用虚假API Key，主要测试数据传输功能")
    print("🚀 请确保Web服务器正在运行: python web_server.py")
    print()
    
    # 基本API Key测试
    test_web_api_key()
    
    # 不同后端测试
    test_different_backends()
    
    print("\n🎊 测试完成!")
    print("\n💡 使用建议:")
    print("1. 在Web界面中输入真实的API Key")
    print("2. 选择合适的模型后端")
    print("3. 点击'应用配置并初始化'")
    print("4. 开始使用自然语言查询功能") 