#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import google.generativeai as genai
import inspect

print("=== Google GenerativeAI 配置选项 ===")

# 查看configure方法的签名
print("configure方法签名:")
try:
    sig = inspect.signature(genai.configure)
    print(f"参数: {sig}")
    
    for param_name, param in sig.parameters.items():
        print(f"  - {param_name}: {param.annotation} = {param.default}")
except Exception as e:
    print(f"无法获取签名: {e}")

# 查看genai.configure的文档
print("\nconfigure方法文档:")
print(genai.configure.__doc__)

# 查看是否有transport或client相关的配置
print("\n查看相关属性:")
for attr in dir(genai):
    if 'transport' in attr.lower() or 'client' in attr.lower() or 'config' in attr.lower():
        print(f"  - {attr}") 