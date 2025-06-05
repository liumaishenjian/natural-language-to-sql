#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础功能测试，不依赖外部包
"""

import re
import os

class SimpleSQLChecker:
    """简化版SQL安全检查器"""
    
    DANGEROUS_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
        'TRUNCATE', 'GRANT', 'REVOKE', 'SET', 'EXEC', 'EXECUTE',
        'CALL', 'DECLARE', 'INTO', 'LOAD', 'OUTFILE', 'DUMPFILE'
    }
    
    def is_safe_sql(self, sql):
        """检查SQL是否安全"""
        if not sql or not sql.strip():
            return False, "SQL语句为空"
        
        sql = sql.strip()
        
        # 检查是否以SELECT开头
        if not sql.upper().startswith('SELECT'):
            return False, "只允许SELECT查询语句"
        
        # 检查危险关键词
        sql_upper = sql.upper()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return False, f"检测到危险关键词: {keyword}"
        
        return True, "SQL检查通过"

def test_sql_checker():
    """测试SQL安全检查器"""
    print("=== 测试SQL安全检查器 ===\n")
    
    checker = SimpleSQLChecker()
    
    test_cases = [
        # 安全的查询
        ("SELECT * FROM users", True),
        ("SELECT name, email FROM users WHERE age > 18", True),
        ("select id from orders", True),
        
        # 不安全的查询
        ("DELETE FROM users", False),
        ("INSERT INTO users VALUES (1, 'test')", False),
        ("UPDATE users SET name = 'hack'", False),
        ("SELECT * FROM users; DROP TABLE users;", False),
        ("", False),  # 空查询
    ]
    
    for i, (sql, expected_safe) in enumerate(test_cases, 1):
        print(f"测试 {i}: {sql if sql else '(空查询)'}")
        
        is_safe, message = checker.is_safe_sql(sql)
        status = "✓ 通过" if is_safe == expected_safe else "✗ 失败"
        print(f"结果: {status} - {message}")
        print(f"预期: {'安全' if expected_safe else '不安全'}, 实际: {'安全' if is_safe else '不安全'}")
        print("-" * 50)

def test_config_reading():
    """测试配置文件读取"""
    print("\n=== 测试配置文件读取 ===\n")
    
    try:
        # 简单的配置文件读取
        if os.path.exists('config.ini'):
            with open('config.ini', 'r', encoding='utf-8') as f:
                content = f.read()
                print("✓ 配置文件读取成功:")
                print(content)
        else:
            print("✗ 配置文件不存在")
    except Exception as e:
        print(f"✗ 配置文件读取失败: {e}")

def test_prompt_generation():
    """测试提示词生成"""
    print("\n=== 测试提示词生成 ===\n")
    
    def create_sql_prompt(user_query, schema_info):
        """创建SQL提示词"""
        prompt = f"""你是一个专业的SQL查询助手。

数据库结构信息：
{schema_info}

用户查询: {user_query}

请生成对应的MySQL SELECT查询语句："""
        return prompt
    
    # 测试数据
    test_schema = """
表名: users
字段: id (int), name (varchar), email (varchar), age (int)

表名: orders  
字段: id (int), user_id (int), amount (decimal), created_at (datetime)
"""
    
    test_query = "查询所有年龄大于25岁的用户姓名和邮箱"
    
    prompt = create_sql_prompt(test_query, test_schema)
    print("✓ 提示词生成成功:")
    print(prompt)
    print("-" * 50)

def main():
    """主测试函数"""
    print("开始基础功能测试...\n")
    
    # 测试各个模块
    test_sql_checker()
    test_config_reading() 
    test_prompt_generation()
    
    print("\n=== 测试完成 ===")
    print("注意：完整功能需要安装依赖包和配置数据库连接")

if __name__ == '__main__':
    main() 