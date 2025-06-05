from tabulate import tabulate
import json
import csv
import io

class ResultFormatter:
    """查询结果格式化器，支持多种输出格式"""
    
    def __init__(self):
        self.supported_formats = ['table', 'json', 'csv', 'simple']
    
    def format_result(self, column_names, rows, format_type='table', max_width=50):
        """
        格式化查询结果
        
        Args:
            column_names: 列名列表
            rows: 数据行列表
            format_type: 输出格式 ('table', 'json', 'csv', 'simple')
            max_width: 单元格最大宽度
            
        Returns:
            str: 格式化后的结果字符串
        """
        if not rows:
            return "查询结果为空"
        
        if format_type not in self.supported_formats:
            format_type = 'table'
        
        # 处理过长的内容
        processed_rows = self._truncate_long_content(rows, max_width)
        
        if format_type == 'table':
            return self._format_as_table(column_names, processed_rows)
        elif format_type == 'json':
            return self._format_as_json(column_names, rows)
        elif format_type == 'csv':
            return self._format_as_csv(column_names, rows)
        elif format_type == 'simple':
            return self._format_as_simple(column_names, processed_rows)
        
        return str(rows)
    
    def _format_as_table(self, column_names, rows):
        """格式化为表格"""
        try:
            # 使用tabulate创建漂亮的表格
            table = tabulate(
                rows, 
                headers=column_names, 
                tablefmt='grid',
                numalign='right',
                stralign='left'
            )
            return table
        except Exception as e:
            return f"表格格式化失败: {e}\n原始数据:\n{rows}"
    
    def _format_as_json(self, column_names, rows):
        """格式化为JSON"""
        try:
            # 将结果转换为字典列表
            result_list = []
            for row in rows:
                row_dict = {}
                for i, col_name in enumerate(column_names):
                    # 处理可能的None值和特殊类型
                    value = row[i] if i < len(row) else None
                    if value is not None:
                        # 转换datetime等特殊类型为字符串
                        if hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        elif hasattr(value, '__str__') and not isinstance(value, (int, float, bool)):
                            value = str(value)
                    row_dict[col_name] = value
                result_list.append(row_dict)
            
            return json.dumps(result_list, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"JSON格式化失败: {e}"
    
    def _format_as_csv(self, column_names, rows):
        """格式化为CSV"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow(column_names)
            
            # 写入数据行
            for row in rows:
                # 处理可能的None值和特殊类型
                processed_row = []
                for value in row:
                    if value is None:
                        processed_row.append('')
                    elif hasattr(value, 'isoformat'):
                        processed_row.append(value.isoformat())
                    else:
                        processed_row.append(str(value))
                writer.writerow(processed_row)
            
            csv_content = output.getvalue()
            output.close()
            return csv_content
        except Exception as e:
            return f"CSV格式化失败: {e}"
    
    def _format_as_simple(self, column_names, rows):
        """简单格式化"""
        try:
            result = []
            
            # 添加表头
            header = " | ".join(column_names)
            result.append(header)
            result.append("-" * len(header))
            
            # 添加数据行
            for row in rows:
                row_str = " | ".join(str(value) if value is not None else 'NULL' for value in row)
                result.append(row_str)
            
            return "\n".join(result)
        except Exception as e:
            return f"简单格式化失败: {e}"
    
    def _truncate_long_content(self, rows, max_width):
        """截断过长的内容"""
        if max_width <= 0:
            return rows
        
        processed_rows = []
        for row in rows:
            processed_row = []
            for value in row:
                if value is None:
                    processed_row.append(None)
                else:
                    str_value = str(value)
                    if len(str_value) > max_width:
                        processed_row.append(str_value[:max_width-3] + "...")
                    else:
                        processed_row.append(str_value)
            processed_rows.append(processed_row)
        
        return processed_rows
    
    def get_result_summary(self, column_names, rows):
        """获取查询结果摘要"""
        if not rows:
            return "查询结果为空"
        
        summary = {
            'total_rows': len(rows),
            'total_columns': len(column_names),
            'columns': column_names
        }
        
        return f"""查询结果摘要:
- 总行数: {summary['total_rows']}
- 总列数: {summary['total_columns']}
- 列名: {', '.join(summary['columns'])}"""

class QueryResultDisplay:
    """查询结果显示器，整合SQL执行和结果格式化"""
    
    def __init__(self):
        self.formatter = ResultFormatter()
    
    def display_query_result(self, sql, column_names, rows, show_sql=True, format_type='table'):
        """
        显示完整的查询结果
        
        Args:
            sql: 执行的SQL语句
            column_names: 列名
            rows: 数据行
            show_sql: 是否显示SQL语句
            format_type: 显示格式
        """
        result_parts = []
        
        if show_sql:
            result_parts.append("=== 执行的SQL语句 ===")
            result_parts.append(sql)
            result_parts.append("")
        
        # 显示结果摘要
        summary = self.formatter.get_result_summary(column_names, rows)
        result_parts.append(summary)
        result_parts.append("")
        
        # 显示格式化结果
        if rows:
            result_parts.append("=== 查询结果 ===")
            formatted_result = self.formatter.format_result(column_names, rows, format_type)
            result_parts.append(formatted_result)
        else:
            result_parts.append("查询未返回任何结果")
        
        return "\n".join(result_parts)
    
    def display_error(self, error_message, sql=None):
        """显示错误信息"""
        error_parts = ["=== 查询出错 ==="]
        error_parts.append(f"错误信息: {error_message}")
        
        if sql:
            error_parts.append(f"SQL语句: {sql}")
        
        return "\n".join(error_parts)

if __name__ == '__main__':
    # 测试结果格式化
    formatter = ResultFormatter()
    display = QueryResultDisplay()
    
    # 测试数据
    test_columns = ['ID', '姓名', '邮箱', '年龄']
    test_rows = [
        (1, '张三', 'zhangsan@example.com', 25),
        (2, '李四', 'lisi@example.com', 30),
        (3, '王五', 'wangwu@example.com', 28),
        (4, '赵六', 'zhaoliu@example.com', 35)
    ]
    
    test_sql = "SELECT id, name, email, age FROM users WHERE age > 20"
    
    print("=== 格式化测试 ===\n")
    
    # 测试不同格式
    formats = ['table', 'json', 'csv', 'simple']
    
    for fmt in formats:
        print(f"--- {fmt.upper()} 格式 ---")
        result = formatter.format_result(test_columns, test_rows, fmt)
        print(result)
        print("\n" + "="*50 + "\n")
    
    # 测试完整显示
    print("=== 完整显示测试 ===")
    full_display = display.display_query_result(test_sql, test_columns, test_rows)
    print(full_display) 