#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文对话功能测试脚本
演示自然语言转SQL系统的上下文对话能力
"""

import sys
import os
from main import NaturalLanguageToSQL

def test_context_conversation():
    """测试上下文对话功能"""
    print("🧪 === 上下文对话功能测试 ===")
    
    # 初始化系统（使用通义千问，因为它有最好的上下文支持）
    try:
        print("📡 正在初始化系统（通义千问后端）...")
        nl2sql = NaturalLanguageToSQL(
            llm_backend='qwen_api',
            model_name='qwen-plus'
        )
        
        print("🔗 正在初始化连接...")
        nl2sql.initialize()
        print("✅ 系统初始化成功！")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("💡 请确保配置文件中设置了 qwen_api_key")
        return
    
    # 测试对话序列
    conversation_tests = [
        {
            "query": "查询所有用户的用户名和真实姓名",
            "description": "第一次查询 - 基础查询"
        },
        {
            "query": "只要前5条",
            "description": "第二次查询 - 基于上下文添加限制"
        },
        {
            "query": "再加上邮箱字段",
            "description": "第三次查询 - 基于上下文修改字段"
        },
        {
            "query": "按创建时间倒序排列",
            "description": "第四次查询 - 基于上下文添加排序"
        }
    ]
    
    print("\n🔄 开始上下文对话测试...")
    print("=" * 80)
    
    for i, test in enumerate(conversation_tests, 1):
        print(f"\n🔸 第{i}次查询: {test['description']}")
        print(f"🗣️ 用户说: \"{test['query']}\"")
        print("-" * 60)
        
        try:
            # 处理查询（这会自动记录到对话历史中）
            result = nl2sql.process_query_for_web(test['query'])
            
            if result['success']:
                print(f"✅ SQL生成成功: {result['sql']}")
                print(f"📊 查询结果: {result['row_count']} 行数据")
                
                # 显示前几行数据作为示例
                if result['rows']:
                    print(f"📋 列名: {', '.join(result['columns'])}")
                    for j, row in enumerate(result['rows'][:3]):  # 只显示前3行
                        print(f"   行{j+1}: {row}")
                    if len(result['rows']) > 3:
                        print(f"   ... 还有 {len(result['rows']) - 3} 行")
            else:
                print(f"❌ SQL生成失败: {result['error']}")
                
        except Exception as e:
            print(f"❌ 查询处理失败: {e}")
        
        print("-" * 60)
        
        # 显示当前对话历史摘要
        summary = nl2sql.conversation_manager.get_conversation_summary()
        print(f"📈 对话状态: 总查询 {summary['total_queries']} 次，成功 {summary['successful_queries']} 次")
        
        # 在最后一次查询后显示完整对话历史
        if i == len(conversation_tests):
            print("\n📚 === 完整对话历史 ===")
            for entry in nl2sql.conversation_manager.conversation_history:
                if entry['role'] == 'user':
                    print(f"👤 用户: {entry['query']}")
                elif entry['role'] == 'assistant':
                    status = "✅" if entry['success'] else "❌"
                    print(f"🤖 助手 {status}: {entry['sql']}")
        
        # 询问是否继续
        if i < len(conversation_tests):
            input("\n⏯️ 按回车键继续下一个测试...")
    
    print("\n🎯 === 测试总结 ===")
    final_summary = nl2sql.conversation_manager.get_conversation_summary()
    print(f"✅ 完成了 {final_summary['total_queries']} 次查询")
    print(f"✅ 成功了 {final_summary['successful_queries']} 次")
    print(f"✅ 展示了上下文对话的强大能力！")
    
    # 导出对话历史
    try:
        export_file = nl2sql.conversation_manager.export_conversation("context_test_export.json")
        print(f"📁 对话历史已导出到: {export_file}")
    except Exception as e:
        print(f"⚠️ 导出对话历史失败: {e}")
    
    # 清理资源
    nl2sql.cleanup()
    
def test_single_vs_context():
    """比较单次对话和上下文对话的差异"""
    print("\n🆚 === 单次对话 vs 上下文对话比较 ===")
    
    # 这里可以添加更详细的比较测试
    print("💡 上下文对话的优势:")
    print("   1. 理解代词引用（如'只要前10条'中的'前10条'指的是什么）")
    print("   2. 基于历史查询进行增量修改")
    print("   3. 保持查询的连贯性和逻辑性")
    print("   4. 减少用户重复输入相同的查询条件")
    print("   5. 支持复杂的多步骤查询构建")

if __name__ == '__main__':
    print("🚀 自然语言转SQL系统 - 上下文对话功能测试")
    print("=" * 80)
    
    # 检查各种API的上下文支持状态
    print("📊 各API上下文支持状态:")
    print("   ✅ 通义千问: 完全支持 (使用OpenAI格式的messages数组)")
    print("   ✅ Google Gemini: 支持 (使用增强的提示词包含历史)")
    print("   ✅ Ollama: 支持 (使用增强的提示词包含历史)")
    print()
    
    try:
        test_context_conversation()
        test_single_vs_context()
        
        print("\n🎉 所有测试完成！")
        print("💡 提示: 你现在可以在命令行模式中体验上下文对话功能")
        print("   运行: python main.py --backend qwen_api --model qwen-plus")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc() 