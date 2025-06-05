#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自然语言转SQL工具完整演示
模拟整个工作流程，不依赖外部API和数据库
"""

import json

class MockDatabaseConnector:
    """模拟数据库连接器"""
    
    def __init__(self):
        # 模拟数据库表结构
        self.mock_schema = {
            'users': [
                {'field': 'id', 'type': 'int', 'key': 'PRI'},
                {'field': 'name', 'type': 'varchar(100)', 'key': ''},
                {'field': 'email', 'type': 'varchar(100)', 'key': ''},
                {'field': 'age', 'type': 'int', 'key': ''},
                {'field': 'city', 'type': 'varchar(50)', 'key': ''}
            ],
            'orders': [
                {'field': 'id', 'type': 'int', 'key': 'PRI'},
                {'field': 'user_id', 'type': 'int', 'key': 'MUL'},
                {'field': 'product_name', 'type': 'varchar(200)', 'key': ''},
                {'field': 'amount', 'type': 'decimal(10,2)', 'key': ''},
                {'field': 'created_at', 'type': 'datetime', 'key': ''}
            ]
        }
        
        # 模拟数据
        self.mock_data = {
            'users': [
                (1, '张三', 'zhangsan@example.com', 25, '北京'),
                (2, '李四', 'lisi@example.com', 30, '上海'),
                (3, '王五', 'wangwu@example.com', 28, '广州'),
                (4, '赵六', 'zhaoliu@example.com', 35, '深圳'),
                (5, '钱七', 'qianqi@example.com', 22, '杭州')
            ],
            'orders': [
                (1, 1, 'iPhone 15', 6999.00, '2024-01-15 10:30:00'),
                (2, 2, 'MacBook Pro', 12999.00, '2024-01-16 14:20:00'),
                (3, 1, 'iPad Air', 4599.00, '2024-01-17 09:15:00'),
                (4, 3, 'Apple Watch', 2999.00, '2024-01-18 16:45:00')
            ]
        }
    
    def get_schema_description(self):
        """获取数据库结构描述"""
        description = "数据库表结构信息：\n\n"
        
        for table_name, columns in self.mock_schema.items():
            description += f"表名: {table_name}\n"
            description += "字段信息:\n"
            for col in columns:
                description += f"  - {col['field']} ({col['type']}) {col['key']}\n"
            description += "\n"
            
        return description
    
    def execute_query(self, sql):
        """模拟执行SQL查询"""
        print(f"[模拟执行] {sql}")
        
        # 简单的SQL解析和执行模拟
        sql_upper = sql.upper().strip()
        
        if 'SELECT * FROM USERS' in sql_upper:
            columns = ['id', 'name', 'email', 'age', 'city']
            rows = self.mock_data['users']
            return columns, rows
        
        elif 'SELECT NAME, EMAIL FROM USERS' in sql_upper:
            columns = ['name', 'email']
            rows = [(row[1], row[2]) for row in self.mock_data['users']]
            return columns, rows
        
        elif 'WHERE AGE >' in sql_upper:
            # 模拟年龄筛选
            columns = ['id', 'name', 'email', 'age', 'city']
            rows = [row for row in self.mock_data['users'] if row[3] > 25]
            return columns, rows
        
        elif 'SELECT * FROM ORDERS' in sql_upper:
            columns = ['id', 'user_id', 'product_name', 'amount', 'created_at']
            rows = self.mock_data['orders']
            return columns, rows
        
        elif 'JOIN' in sql_upper:
            # 模拟关联查询
            columns = ['user_name', 'product_name', 'amount']
            rows = [
                ('张三', 'iPhone 15', 6999.00),
                ('李四', 'MacBook Pro', 12999.00),
                ('张三', 'iPad Air', 4599.00),
                ('王五', 'Apple Watch', 2999.00)
            ]
            return columns, rows
        
        else:
            # 默认返回用户表
            columns = ['id', 'name', 'email', 'age', 'city']
            rows = self.mock_data['users']
            return columns, rows

class MockLLMGenerator:
    """模拟大模型SQL生成器"""
    
    def __init__(self):
        # 预定义的查询模式和对应SQL
        self.query_patterns = {
            '所有用户': 'SELECT * FROM `users`',
            '用户信息': 'SELECT * FROM `users`',
            '用户姓名': 'SELECT `name`, `email` FROM `users`',
            '年龄大于': 'SELECT * FROM `users` WHERE `age` > 25',
            '年龄超过': 'SELECT * FROM `users` WHERE `age` > 25',
            '所有订单': 'SELECT * FROM `orders`',
            '订单信息': 'SELECT * FROM `orders`',
            '用户和订单': '''SELECT u.`name` as user_name, o.`product_name`, o.`amount` 
FROM `users` u 
JOIN `orders` o ON u.`id` = o.`user_id`''',
            '关联查询': '''SELECT u.`name` as user_name, o.`product_name`, o.`amount` 
FROM `users` u 
JOIN `orders` o ON u.`id` = o.`user_id`'''
        }
    
    def generate_sql(self, user_query, schema_description):
        """模拟生成SQL"""
        print(f"[模拟大模型] 处理查询: {user_query}")
        
        # 简单的模式匹配
        for pattern, sql in self.query_patterns.items():
            if pattern in user_query:
                print(f"[模拟大模型] 匹配模式: {pattern}")
                return True, sql
        
        # 如果没有匹配，返回默认查询
        print("[模拟大模型] 使用默认查询")
        return True, "SELECT * FROM `users`"

class SQLSecurityChecker:
    """SQL安全检查器"""
    
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
        
        if not sql.upper().startswith('SELECT'):
            return False, "只允许SELECT查询语句"
        
        sql_upper = sql.upper()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return False, f"检测到危险关键词: {keyword}"
        
        return True, "SQL检查通过"

class SimpleResultFormatter:
    """简单的结果格式化器"""
    
    def format_as_table(self, column_names, rows):
        """格式化为简单表格"""
        if not rows:
            return "查询结果为空"
        
        # 计算列宽
        col_widths = []
        for i, col_name in enumerate(column_names):
            max_width = len(str(col_name))
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)
        
        # 构建表格
        result = []
        
        # 表头
        header = "|" + "|".join(f" {col_name:<{col_widths[i]-1}}" for i, col_name in enumerate(column_names)) + "|"
        result.append(header)
        
        # 分隔线
        separator = "|" + "|".join("-" * col_widths[i] for i in range(len(column_names))) + "|"
        result.append(separator)
        
        # 数据行
        for row in rows:
            row_str = "|" + "|".join(f" {str(row[i]) if i < len(row) else '':<{col_widths[i]-1}}" for i in range(len(column_names))) + "|"
            result.append(row_str)
        
        return "\n".join(result)
    
    def display_query_result(self, sql, column_names, rows, show_sql=True):
        """显示完整查询结果"""
        result_parts = []
        
        if show_sql:
            result_parts.append("=== 执行的SQL语句 ===")
            result_parts.append(sql)
            result_parts.append("")
        
        result_parts.append(f"查询结果摘要: 返回 {len(rows)} 行，{len(column_names)} 列")
        result_parts.append("")
        
        if rows:
            result_parts.append("=== 查询结果 ===")
            table = self.format_as_table(column_names, rows)
            result_parts.append(table)
        else:
            result_parts.append("查询未返回任何结果")
        
        return "\n".join(result_parts)

def demo_complete_workflow():
    """演示完整的工作流程"""
    print("=== 自然语言转SQL查询工具演示 ===\n")
    
    # 初始化各个模块
    db_connector = MockDatabaseConnector()
    llm_generator = MockLLMGenerator()
    security_checker = SQLSecurityChecker()
    result_formatter = SimpleResultFormatter()
    
    # 获取数据库结构
    schema_description = db_connector.get_schema_description()
    print("1. 数据库结构:")
    print(schema_description)
    
    # 测试查询案例
    test_queries = [
        "查询所有用户信息",
        "显示用户姓名和邮箱",
        "查找年龄大于25岁的用户",
        "查看所有订单",
        "显示用户和订单的关联信息"
    ]
    
    for i, user_query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"测试查询 {i}: {user_query}")
        print('='*60)
        
        # 2. 生成SQL
        success, sql_or_error = llm_generator.generate_sql(user_query, schema_description)
        
        if not success:
            print(f"❌ SQL生成失败: {sql_or_error}")
            continue
        
        generated_sql = sql_or_error
        print(f"✅ 生成的SQL: {generated_sql}")
        
        # 3. 安全检查
        is_safe, safety_message = security_checker.is_safe_sql(generated_sql)
        
        if not is_safe:
            print(f"❌ 安全检查失败: {safety_message}")
            continue
        
        print(f"✅ 安全检查: {safety_message}")
        
        # 4. 执行查询
        try:
            column_names, rows = db_connector.execute_query(generated_sql)
            
            # 5. 显示结果
            result = result_formatter.display_query_result(generated_sql, column_names, rows)
            print(f"\n{result}")
            
        except Exception as e:
            print(f"❌ 查询执行失败: {e}")

if __name__ == '__main__':
    demo_complete_workflow() 