import configparser
import mysql.connector
from mysql.connector import Error

def get_db_config(config_file='config.ini'):
    """从指定的.ini文件读取数据库配置"""
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    db_config = {}
    if 'mysql' in config:
        db_config['host'] = config.get('mysql', 'host', fallback=None)
        db_config['port'] = config.getint('mysql', 'port', fallback=3306)
        db_config['user'] = config.get('mysql', 'user', fallback=None)
        db_config['password'] = config.get('mysql', 'password', fallback=None)
        db_config['database'] = config.get('mysql', 'database', fallback=None)
    
    # 验证必要参数是否存在
    if not all([db_config.get('host'), db_config.get('user'), db_config.get('database')]):
        raise ValueError("配置文件中缺少必要的数据库配置项(host, user, database)")
        
    return db_config

class DatabaseConnector:
    """数据库连接器类，负责连接MySQL并获取表结构信息"""
    
    def __init__(self, config_file='config.ini'):
        self.config = get_db_config(config_file)
        self.connection = None
        
    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            print(f"成功连接到数据库: {self.config['database']}")
            return True
        except Error as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")
    
    def get_all_tables(self):
        """获取数据库中所有表的名称"""
        if not self.connection or not self.connection.is_connected():
            raise Exception("数据库未连接")
        
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        return tables
    
    def get_table_columns(self, table_name):
        """获取指定表的所有字段信息"""
        if not self.connection or not self.connection.is_connected():
            raise Exception("数据库未连接")
        
        cursor = self.connection.cursor()
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'field': row[0],
                'type': row[1],
                'null': row[2],
                'key': row[3],
                'default': row[4],
                'extra': row[5]
            })
        cursor.close()
        return columns
    
    def get_database_schema(self):
        """获取整个数据库的表结构信息"""
        schema = {}
        tables = self.get_all_tables()
        
        for table in tables:
            columns = self.get_table_columns(table)
            schema[table] = columns
            
        return schema
    
    def get_schema_description(self):
        """获取数据库结构的文本描述，用于提供给大模型"""
        schema = self.get_database_schema()
        description = "数据库表结构信息：\n\n"
        
        for table_name, columns in schema.items():
            description += f"表名: {table_name}\n"
            description += "字段信息:\n"
            for col in columns:
                description += f"  - {col['field']} ({col['type']}) {col['key']} {col['null']}\n"
            description += "\n"
            
        return description
    
    def execute_query(self, sql):
        """执行SQL查询并返回结果"""
        if not self.connection or not self.connection.is_connected():
            raise Exception("数据库未连接")
        
        cursor = self.connection.cursor()
        cursor.execute(sql)
        
        # 获取列名
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # 获取数据
        rows = cursor.fetchall()
        cursor.close()
        
        return column_names, rows

if __name__ == '__main__':
    # 测试数据库连接和表结构读取
    try:
        db = DatabaseConnector()
        if db.connect():
            print("\n=== 数据库表列表 ===")
            tables = db.get_all_tables()
            print(f"发现 {len(tables)} 个表: {tables}")
            
            print("\n=== 数据库结构描述 ===")
            schema_desc = db.get_schema_description()
            print(schema_desc)
            
            db.disconnect()
    except Exception as e:
        print(f"错误: {e}") 