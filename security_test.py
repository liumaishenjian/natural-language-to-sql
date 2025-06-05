#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL安全检查功能测试
"""

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

def test_security_features():
    """测试安全功能"""
    print("=== SQL安全检查功能测试 ===\n")
    
    checker = SQLSecurityChecker()
    
    # 安全的SELECT查询
    safe_queries = [
        'SELECT * FROM users',
        'SELECT name, email FROM users WHERE age > 25',
        'SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id',
        'SELECT COUNT(*) FROM users GROUP BY city',
        'select * from users',  # 小写
        '   SELECT * FROM users   ',  # 带空格
    ]
    
    # 危险的SQL操作
    dangerous_queries = [
        'DELETE FROM users WHERE id = 1',
        'INSERT INTO users (name, email) VALUES ("hacker", "hack@evil.com")',
        'UPDATE users SET password = "hacked" WHERE id = 1',
        'DROP TABLE users',
        'CREATE TABLE malicious (id int)',
        'SELECT * FROM users; DROP TABLE users;--',
        '',  # 空查询
    ]
    
    print("1. 测试安全查询 (应该通过):")
    passed_safe = 0
    for i, sql in enumerate(safe_queries, 1):
        is_safe, message = checker.is_safe_sql(sql)
        status = "✅" if is_safe else "❌"
        print(f"  {i}. {status} {sql if sql else '(空查询)'} - {message}")
        if is_safe:
            passed_safe += 1
    
    print(f"\n安全查询通过率: {passed_safe}/{len(safe_queries)} ({passed_safe/len(safe_queries)*100:.1f}%)")
    
    print("\n2. 测试危险查询 (应该被阻止):")
    blocked_dangerous = 0
    for i, sql in enumerate(dangerous_queries, 1):
        is_safe, message = checker.is_safe_sql(sql)
        status = "✅" if not is_safe else "❌"  # 危险查询被阻止才是正确的
        print(f"  {i}. {status} {sql if sql else '(空查询)'} - {message}")
        if not is_safe:
            blocked_dangerous += 1
    
    print(f"\n危险查询阻止率: {blocked_dangerous}/{len(dangerous_queries)} ({blocked_dangerous/len(dangerous_queries)*100:.1f}%)")
    
    total_correct = passed_safe + blocked_dangerous
    total_tests = len(safe_queries) + len(dangerous_queries)
    
    print(f"\n=== 总体测试结果 ===")
    print(f"总测试: {total_tests}")
    print(f"正确: {total_correct}")
    print(f"准确率: {total_correct/total_tests*100:.1f}%")
    
    if total_correct == total_tests:
        print("🎉 所有安全检查测试都通过了！")
    else:
        print(f"⚠️ 有 {total_tests - total_correct} 个测试未通过")

if __name__ == '__main__':
    test_security_features() 