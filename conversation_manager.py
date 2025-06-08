#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话上下文管理器
管理与AI的对话历史，支持上下文相关的SQL生成
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class ConversationManager:
    """对话上下文管理器"""
    
    def __init__(self, max_history=10):
        """
        初始化对话管理器
        
        Args:
            max_history: 保留的最大对话轮数
        """
        self.max_history = max_history
        self.conversation_history = []
        self.session_start = datetime.now()
        
    def add_user_query(self, query: str, sql_result: Optional[str] = None):
        """
        添加用户查询到对话历史
        
        Args:
            query: 用户的自然语言查询
            sql_result: 生成的SQL语句（可选）
        """
        entry = {
            "role": "user",
            "query": query,
            "sql": sql_result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(entry)
        
        # 保持历史记录在限制范围内
        if len(self.conversation_history) > self.max_history * 2:  # *2因为包含user和assistant
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def add_assistant_response(self, sql: str, success: bool, error_msg: Optional[str] = None):
        """
        添加助手响应到对话历史
        
        Args:
            sql: 生成的SQL语句
            success: 是否成功
            error_msg: 错误信息（如果有）
        """
        entry = {
            "role": "assistant", 
            "sql": sql,
            "success": success,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(entry)
    
    def get_context_for_prompt(self, schema_description: str, current_query: str) -> str:
        """
        构建包含上下文的提示词
        
        Args:
            schema_description: 数据库结构描述
            current_query: 当前查询
            
        Returns:
            完整的提示词
        """
        base_prompt = f"""你是一个专业的SQL查询助手。请根据用户的自然语言查询需求，生成对应的MySQL SQL查询语句。

数据库结构信息：
{schema_description}

重要要求：
1. 只生成SELECT查询语句，不要生成INSERT、UPDATE、DELETE等修改数据的语句
2. 确保生成的SQL语法正确，适用于MySQL数据库
3. 使用反引号包围表名和字段名以避免关键字冲突
4. 如果查询涉及多表，请正确使用JOIN语句
5. 只返回SQL语句，不要包含其他解释文字
6. 如果无法理解用户查询或数据库中没有相关表，请返回"ERROR: 无法生成对应的SQL查询"
7. 注意参考对话历史，理解用户可能的关联需求"""

        # 添加对话历史上下文
        if self.conversation_history:
            base_prompt += "\n\n对话历史上下文："
            
            recent_history = self.conversation_history[-6:]  # 最近3轮对话
            for entry in recent_history:
                if entry["role"] == "user":
                    base_prompt += f"\n用户: {entry['query']}"
                    if entry.get("sql"):
                        base_prompt += f"\n生成的SQL: {entry['sql']}"
                elif entry["role"] == "assistant" and entry.get("success"):
                    base_prompt += f"\n助手返回SQL: {entry['sql']}"
        
        base_prompt += f"\n\n当前用户查询: {current_query}\n\n请生成对应的SQL查询语句："
        
        return base_prompt
    
    def get_messages_for_openai_format(self, schema_description: str, current_query: str) -> List[Dict]:
        """
        构建OpenAI格式的messages数组（用于通义千问和Gemini）
        
        Args:
            schema_description: 数据库结构描述
            current_query: 当前查询
            
        Returns:
            messages数组
        """
        messages = []
        
        # 系统提示词
        system_prompt = f"""你是一个专业的SQL查询助手。请根据用户的自然语言查询需求，生成对应的MySQL SQL查询语句。

数据库结构信息：
{schema_description}

重要要求：
1. 只生成SELECT查询语句，不要生成INSERT、UPDATE、DELETE等修改数据的语句
2. 确保生成的SQL语法正确，适用于MySQL数据库
3. 使用反引号包围表名和字段名以避免关键字冲突
4. 如果查询涉及多表，请正确使用JOIN语句
5. 只返回SQL语句，不要包含其他解释文字
6. 如果无法理解用户查询或数据库中没有相关表，请返回"ERROR: 无法生成对应的SQL查询"
7. 注意参考对话历史，理解用户可能的关联需求和上下文"""

        messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史对话
        recent_history = self.conversation_history[-8:]  # 最近4轮对话
        for entry in recent_history:
            if entry["role"] == "user":
                messages.append({"role": "user", "content": entry["query"]})
            elif entry["role"] == "assistant" and entry.get("success") and entry.get("sql"):
                messages.append({"role": "assistant", "content": entry["sql"]})
        
        # 添加当前查询
        messages.append({"role": "user", "content": current_query})
        
        return messages
    
    def get_conversation_summary(self) -> Dict:
        """
        获取对话摘要信息
        
        Returns:
            对话摘要字典
        """
        return {
            "session_start": self.session_start.isoformat(),
            "total_queries": len([entry for entry in self.conversation_history if entry["role"] == "user"]),
            "successful_queries": len([entry for entry in self.conversation_history 
                                     if entry["role"] == "assistant" and entry.get("success")]),
            "recent_queries": [entry["query"] for entry in self.conversation_history[-6:] 
                             if entry["role"] == "user"]
        }
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        self.session_start = datetime.now()
        print("🗑️ 对话历史已清空")
    
    def export_conversation(self, filename: str = None) -> str:
        """
        导出对话历史到JSON文件
        
        Args:
            filename: 文件名，如果为None则自动生成
            
        Returns:
            导出的文件路径
        """
        if filename is None:
            filename = f"conversation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "session_info": {
                "start_time": self.session_start.isoformat(),
                "export_time": datetime.now().isoformat(),
                "total_entries": len(self.conversation_history)
            },
            "conversation": self.conversation_history,
            "summary": self.get_conversation_summary()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return filename

if __name__ == '__main__':
    # 测试对话管理器
    manager = ConversationManager()
    
    # 模拟对话
    manager.add_user_query("查询所有用户")
    manager.add_assistant_response("SELECT * FROM `sys_user`", True)
    
    manager.add_user_query("只要前10条")
    manager.add_assistant_response("SELECT * FROM `sys_user` LIMIT 10", True)
    
    # 显示摘要
    print("对话摘要:", manager.get_conversation_summary())
    
    # 测试上下文提示词
    schema = "表名: sys_user\n字段: id, username, email"
    print("\n上下文提示词:")
    print(manager.get_context_for_prompt(schema, "再加上邮箱字段")) 