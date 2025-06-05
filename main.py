#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自然语言转SQL查询工具
主程序入口，整合所有功能模块
支持在线API和本地Ollama大模型
"""

import os
import sys
import argparse
from database_connector import DatabaseConnector
from sql_security_checker import SQLSecurityChecker
from result_formatter import QueryResultDisplay

class NaturalLanguageToSQL:
    """自然语言转SQL查询工具主类"""
    
    def __init__(self, config_file='config.ini', llm_backend='ollama', model_name='qwen2', ollama_url="http://localhost:11434"):
        """
        初始化工具
        
        Args:
            config_file: 数据库配置文件路径
            llm_backend: 大模型后端 ('ollama' 或 'qwen_api')
            model_name: 模型名称
            ollama_url: Ollama服务URL
        """
        self.config_file = config_file
        self.llm_backend = llm_backend
        self.model_name = model_name
        self.ollama_url = ollama_url
        
        # 初始化各个模块
        try:
            self.db_connector = DatabaseConnector(config_file)
            self.security_checker = SQLSecurityChecker()
            self.result_display = QueryResultDisplay()
            
            # 根据后端类型初始化大模型生成器
            if llm_backend == 'ollama':
                from ollama_sql_generator import OllamaLLMGenerator
                self.sql_generator = OllamaLLMGenerator(model_name, ollama_url)
                print(f"🤖 使用本地Ollama模型: {model_name}")
            else:  # qwen_api
                from llm_sql_generator import LLMSQLGenerator
                self.sql_generator = LLMSQLGenerator(model_name)
                print(f"🌐 使用在线API模型: {model_name}")
            
            # 数据库schema缓存
            self.schema_description = None
            
        except Exception as e:
            print(f"初始化失败: {e}")
            sys.exit(1)
    
    def initialize(self):
        """初始化连接和获取数据库结构"""
        print("正在初始化...")
        
        # 测试大模型连接
        print("1. 检查大模型连接...")
        if not self.sql_generator.test_connection():
            if self.llm_backend == 'ollama':
                print("✗ 本地Ollama模型连接失败")
                print("\n🔧 解决方案:")
                print("1. 确保Ollama已安装并运行: ollama serve")
                print("2. 下载模型: ollama pull qwen2")
                print("3. 或者使用在线API: python main.py --backend qwen_api")
            else:
                print("✗ 在线API连接失败，请检查API Key设置")
                print("💡 或者尝试本地模型: python main.py --backend ollama")
            return False
        print("✓ 大模型连接正常")
        
        # 连接数据库
        print("2. 连接数据库...")
        if not self.db_connector.connect():
            print("✗ 数据库连接失败，请检查配置文件")
            return False
        print("✓ 数据库连接成功")
        
        # 获取数据库结构
        print("3. 读取数据库结构...")
        try:
            self.schema_description = self.db_connector.get_schema_description()
            tables = self.db_connector.get_all_tables()
            print(f"✓ 成功读取 {len(tables)} 个表的结构信息")
        except Exception as e:
            print(f"✗ 读取数据库结构失败: {e}")
            return False
        
        print("初始化完成！\n")
        return True
    
    def process_query(self, user_query, format_type='table', show_sql=True):
        """
        处理用户的自然语言查询
        
        Args:
            user_query: 用户的自然语言查询
            format_type: 结果显示格式
            show_sql: 是否显示生成的SQL
            
        Returns:
            str: 处理结果
        """
        try:
            # 1. 生成SQL
            print("正在生成SQL语句...")
            success, sql_or_error = self.sql_generator.generate_sql(
                user_query, self.schema_description
            )
            
            if not success:
                return self.result_display.display_error(sql_or_error)
            
            generated_sql = sql_or_error
            print(f"生成的SQL: {generated_sql}")
            
            # 2. 安全检查
            print("正在进行安全检查...")
            is_safe, safety_message = self.security_checker.is_safe_sql(generated_sql)
            
            if not is_safe:
                return self.result_display.display_error(
                    f"安全检查失败: {safety_message}", generated_sql
                )
            print("✓ 安全检查通过")
            
            # 3. 执行SQL
            print("正在执行查询...")
            column_names, rows = self.db_connector.execute_query(generated_sql)
            
            # 4. 格式化并返回结果
            return self.result_display.display_query_result(
                generated_sql, column_names, rows, show_sql, format_type
            )
            
        except Exception as e:
            return self.result_display.display_error(f"查询处理过程中发生错误: {e}")
    
    def interactive_mode(self):
        """交互式命令行模式"""
        print("=== 自然语言转SQL查询工具 ===")
        print(f"当前使用: {'本地Ollama模型' if self.llm_backend == 'ollama' else '在线API'} - {self.model_name}")
        print("输入 'exit' 或 'quit' 退出程序")
        print("输入 'help' 查看帮助信息")
        print("输入 'schema' 查看数据库结构")
        print("输入 'models' 查看可用模型（仅Ollama）")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n请输入您的查询需求: ").strip()
                
                if not user_input:
                    continue
                
                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("感谢使用！再见！")
                    break
                elif user_input.lower() in ['help', '帮助']:
                    self._show_help()
                    continue
                elif user_input.lower() in ['schema', '结构']:
                    print("\n当前数据库结构:")
                    print(self.schema_description)
                    continue
                elif user_input.lower() in ['models', '模型']:
                    self._show_available_models()
                    continue
                
                # 处理查询
                print("\n" + "="*50)
                result = self.process_query(user_input)
                print(result)
                print("="*50)
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"\n处理查询时发生错误: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = f"""
=== 帮助信息 ===

🤖 当前配置: {'本地Ollama模型' if self.llm_backend == 'ollama' else '在线API'} - {self.model_name}

1. 基本使用：
   - 直接输入自然语言查询需求，如："查询所有用户信息"
   - 支持复杂查询，如："查询年龄大于25岁的用户姓名和邮箱"

2. 特殊命令：
   - help / 帮助: 显示此帮助信息
   - schema / 结构: 显示数据库表结构
   - models / 模型: 显示可用模型（仅Ollama）
   - exit / quit / 退出: 退出程序

3. 查询示例：
   - "查询所有用户"
   - "统计每个部门的人数"
   - "查找最近一周的订单"
   - "显示销售额最高的产品"

4. 注意事项：
   - 只支持SELECT查询，不支持增删改操作
   - 查询会经过安全检查，确保数据安全
   - 如果查询无法理解，请尝试更具体的描述

5. 切换模型后端：
   - 本地模型: python main.py --backend ollama --model qwen2
   - 在线API: python main.py --backend qwen_api --model qwen-plus
        """
        print(help_text)
    
    def _show_available_models(self):
        """显示可用模型"""
        if self.llm_backend == 'ollama':
            print("\n=== Ollama可用模型 ===")
            models = self.sql_generator.get_available_models()
            if models:
                for i, model in enumerate(models, 1):
                    current = "（当前使用）" if self.model_name in model else ""
                    print(f"  {i}. {model} {current}")
            else:
                print("  暂无可用模型")
                print("  💡 下载模型: ollama pull qwen2")
        else:
            print("\n=== 在线API可用模型 ===")
            print("  1. qwen-turbo")
            print("  2. qwen-plus （推荐）")
            print("  3. qwen-max")
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'db_connector'):
            self.db_connector.disconnect()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='自然语言转SQL查询工具')
    parser.add_argument('--config', default='config.ini', help='数据库配置文件路径')
    parser.add_argument('--backend', default='ollama', choices=['ollama', 'qwen_api'],
                       help='大模型后端类型：ollama(本地) 或 qwen_api(在线)')
    parser.add_argument('--model', help='模型名称（ollama: qwen2等，qwen_api: qwen-plus等）')
    parser.add_argument('--ollama-url', default='http://localhost:11434', 
                       help='Ollama服务URL')
    parser.add_argument('--query', help='直接执行的查询（非交互模式）')
    parser.add_argument('--format', default='table', 
                       choices=['table', 'json', 'csv', 'simple'],
                       help='结果显示格式')
    
    args = parser.parse_args()
    
    # 设置默认模型名称
    if not args.model:
        if args.backend == 'ollama':
            args.model = 'qwen2'
        else:
            args.model = 'qwen-plus'
    
    # 检查配置文件
    if not os.path.exists(args.config):
        print(f"错误: 配置文件 {args.config} 不存在")
        print("请创建配置文件或使用 --config 参数指定正确的路径")
        sys.exit(1)
    
    # 检查在线API的环境变量
    if args.backend == 'qwen_api' and not os.getenv("DASHSCOPE_API_KEY"):
        print("错误: 使用在线API需要设置环境变量 DASHSCOPE_API_KEY")
        print("设置方法:")
        print("Windows: set DASHSCOPE_API_KEY=your_api_key")
        print("Linux/Mac: export DASHSCOPE_API_KEY=your_api_key")
        print("或者使用本地模型: python main.py --backend ollama")
        sys.exit(1)
    
    # 创建工具实例
    tool = NaturalLanguageToSQL(args.config, args.backend, args.model, args.ollama_url)
    
    try:
        # 初始化
        if not tool.initialize():
            print("初始化失败，程序退出")
            sys.exit(1)
        
        if args.query:
            # 非交互模式：直接执行查询
            result = tool.process_query(args.query, args.format)
            print(result)
        else:
            # 交互模式
            tool.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行错误: {e}")
    finally:
        tool.cleanup()

if __name__ == '__main__':
    main() 