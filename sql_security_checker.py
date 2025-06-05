import re
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function
from sqlparse.tokens import Keyword, DML

class SQLSecurityChecker:
    """SQL安全检查器，确保只允许安全的SELECT查询"""
    
    # 危险的SQL关键词
    DANGEROUS_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
        'TRUNCATE', 'GRANT', 'REVOKE', 'SET', 'EXEC', 'EXECUTE',
        'CALL', 'DECLARE', 'INTO', 'LOAD', 'OUTFILE', 'DUMPFILE'
    }
    
    # 潜在危险的函数
    DANGEROUS_FUNCTIONS = {
        'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE', 
        'BENCHMARK', 'SLEEP', 'GET_LOCK'
    }
    
    def __init__(self):
        self.last_check_result = None
        self.last_error_details = []
    
    def is_safe_sql(self, sql):
        """
        检查SQL语句是否安全
        
        Args:
            sql: 要检查的SQL语句
            
        Returns:
            tuple: (is_safe: bool, error_message: str)
        """
        self.last_error_details = []
        
        try:
            # 基本格式检查
            if not sql or not sql.strip():
                return False, "SQL语句为空"
            
            sql = sql.strip()
            
            # 1. 检查是否以SELECT开头
            if not sql.upper().startswith('SELECT'):
                return False, "只允许SELECT查询语句"
            
            # 2. 字符串关键词检查
            sql_upper = sql.upper()
            for keyword in self.DANGEROUS_KEYWORDS:
                if keyword in sql_upper:
                    return False, f"检测到危险关键词: {keyword}"
            
            # 3. 危险函数检查
            for func in self.DANGEROUS_FUNCTIONS:
                if func in sql_upper:
                    return False, f"检测到危险函数: {func}"
            
            # 4. 使用sqlparse进行语法分析
            try:
                parsed = sqlparse.parse(sql)
                if not parsed:
                    return False, "SQL语法解析失败"
                
                # 检查解析后的语句
                for statement in parsed:
                    if not self._is_safe_statement(statement):
                        return False, "SQL语句包含不安全的操作"
                        
            except Exception as e:
                return False, f"SQL语法解析错误: {str(e)}"
            
            # 5. 注入攻击模式检查
            injection_patterns = [
                r';\s*(DROP|DELETE|UPDATE|INSERT)',
                r'UNION\s+SELECT.*--',
                r'\/\*.*\*\/',  # 注释注入
                r'--.*',        # 单行注释
                r'#.*'          # MySQL注释
            ]
            
            for pattern in injection_patterns:
                if re.search(pattern, sql_upper, re.IGNORECASE):
                    return False, f"检测到潜在的SQL注入模式"
            
            return True, "SQL检查通过"
            
        except Exception as e:
            return False, f"安全检查过程中发生错误: {str(e)}"
    
    def _is_safe_statement(self, statement):
        """检查单个SQL语句是否安全"""
        # 获取语句类型
        first_token = statement.token_first(skip_ws=True, skip_cm=True)
        if not first_token:
            return False
        
        # 确保是SELECT语句
        if first_token.ttype is Keyword and first_token.value.upper() != 'SELECT':
            return False
        
        # 检查所有token
        for token in statement.flatten():
            if token.ttype is Keyword:
                if token.value.upper() in self.DANGEROUS_KEYWORDS:
                    return False
            elif token.ttype is DML:
                if token.value.upper() != 'SELECT':
                    return False
        
        return True
    
    def sanitize_sql(self, sql):
        """
        对SQL进行基本的清理和格式化
        
        Args:
            sql: 原始SQL语句
            
        Returns:
            str: 清理后的SQL语句
        """
        if not sql:
            return sql
        
        # 移除前后空白
        sql = sql.strip()
        
        # 移除多余的分号
        sql = sql.rstrip(';')
        
        # 格式化SQL（使用sqlparse）
        try:
            formatted = sqlparse.format(sql, reindent=True, keyword_case='upper')
            return formatted
        except:
            return sql
    
    def get_security_report(self, sql):
        """
        获取详细的安全检查报告
        
        Args:
            sql: 要检查的SQL语句
            
        Returns:
            dict: 包含检查结果的详细报告
        """
        is_safe, message = self.is_safe_sql(sql)
        
        report = {
            'is_safe': is_safe,
            'message': message,
            'sql_original': sql,
            'sql_sanitized': self.sanitize_sql(sql) if sql else None,
            'checks_performed': [
                '基本格式检查',
                'SELECT语句验证',
                '危险关键词检测',
                '危险函数检测',
                'SQL语法解析',
                '注入攻击模式检测'
            ]
        }
        
        return report

# 便捷函数
def check_sql_safety(sql):
    """快速检查SQL安全性的便捷函数"""
    checker = SQLSecurityChecker()
    return checker.is_safe_sql(sql)

if __name__ == '__main__':
    # 测试SQL安全检查
    checker = SQLSecurityChecker()
    
    # 测试用例
    test_cases = [
        # 安全的查询
        "SELECT * FROM users",
        "SELECT name, email FROM users WHERE age > 18",
        "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id",
        
        # 不安全的查询
        "DELETE FROM users",
        "SELECT * FROM users; DROP TABLE users;",
        "INSERT INTO users VALUES (1, 'test')",
        "UPDATE users SET name = 'hacker'",
        "SELECT * FROM users UNION SELECT * FROM admin_users",
        "",  # 空查询
    ]
    
    print("=== SQL安全检查测试 ===\n")
    
    for i, sql in enumerate(test_cases, 1):
        print(f"测试 {i}: {sql if sql else '(空查询)'}")
        
        is_safe, message = checker.is_safe_sql(sql)
        status = "✓ 通过" if is_safe else "✗ 失败"
        print(f"结果: {status} - {message}")
        
        if sql:
            sanitized = checker.sanitize_sql(sql)
            if sanitized != sql:
                print(f"格式化后: {sanitized}")
        
        print("-" * 50) 