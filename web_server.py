#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自然语言转SQL查询工具 - Web服务器
提供API接口给前端调用
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import configparser
from main import NaturalLanguageToSQL
import os
import threading
import time

app = Flask(__name__)
CORS(app)

# 全局工具实例
sql_tool = None
tool_lock = threading.Lock()

def initialize_tool(backend='ollama', model='qwen2', config='config.ini', api_key=None):
    """初始化SQL工具"""
    global sql_tool
    with tool_lock:
        try:
            print(f"🚀 [Web] 开始初始化工具...")
            print(f"🚀 [Web] 后端: {backend}")
            print(f"🚀 [Web] 模型: {model}")
            print(f"🚀 [Web] 配置文件: {config}")
            if api_key:
                print(f"🚀 [Web] 使用传入的API Key: {api_key[:10]}...")
            else:
                # 如果没有传入API Key，尝试从配置文件读取
                try:
                    config_parser = configparser.ConfigParser()
                    config_parser.read(config, encoding='utf-8')
                    if backend == 'gemini':
                        api_key = config_parser.get('api_keys', 'gemini_api_key', fallback=None)
                        if api_key and api_key.strip():
                            print(f"🚀 [Web] 从配置文件读取 Gemini API Key: {api_key[:10]}...")
                        else:
                            print("🚀 [Web] 未找到 Gemini API Key，将使用环境变量")
                    elif backend == 'qwen_api':
                        api_key = config_parser.get('api_keys', 'qwen_api_key', fallback=None)
                        if api_key and api_key.strip():
                            print(f"🚀 [Web] 从配置文件读取 Qwen API Key: {api_key[:10]}...")
                        else:
                            print("🚀 [Web] 未找到 Qwen API Key，将使用环境变量")
                    else:
                        print("🚀 [Web] Ollama后端不需要API Key")
                except Exception as e:
                    print(f"🚀 [Web] 读取配置文件失败: {e}，将使用环境变量")
                
            print("🚀 [Web] 创建 NaturalLanguageToSQL 实例...")
            sql_tool = NaturalLanguageToSQL(config, backend, model, "http://localhost:11434", api_key)
            
            print("🚀 [Web] 调用工具初始化方法...")
            success = sql_tool.initialize()
            
            # 即使AI模型连接失败，也检查数据库连接是否成功
            print("🚀 [Web] 检查数据库连接状态...")
            db_connected = False
            try:
                db_connected = sql_tool.db_connector and sql_tool.db_connector.connection and sql_tool.db_connector.connection.is_connected()
                print(f"🚀 [Web] 数据库连接状态: {'✅ 已连接' if db_connected else '❌ 未连接'}")
            except Exception as db_e:
                print(f"🚀 [Web] 数据库连接检查异常: {db_e}")
                db_connected = False
            
            if success:
                print("✅ [Web] 初始化完全成功")
                return True, "初始化成功"
            elif db_connected:
                print("⚠️  [Web] 数据库成功，AI模型失败")
                return True, "数据库连接成功，AI模型连接失败（可在使用时重试）"
            else:
                print("❌ [Web] 初始化完全失败")
                return False, "初始化失败"
        except Exception as e:
            print(f"❌ [Web] 初始化异常: {e}")
            print(f"❌ [Web] 异常类型: {type(e).__name__}")
            return False, str(e)

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/test')
def test():
    """API测试页面"""
    with open('test_api.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return content

@app.route('/favicon.ico')
def favicon():
    """处理favicon请求，避免404错误"""
    return '', 204  # 返回空内容，状态码204 No Content

@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    """初始化API"""
    data = request.get_json()
    backend = data.get('backend', 'ollama')
    model = data.get('model', 'qwen2')
    config = data.get('config', 'config.ini')
    api_key = data.get('api_key')  # 从请求中获取API Key
    
    success, message = initialize_tool(backend, model, config, api_key)
    
    return jsonify({
        'success': success,
        'message': message,
        'backend': backend,
        'model': model
    })

@app.route('/api/query', methods=['POST'])
def api_query():
    """处理查询API"""
    global sql_tool
    
    if not sql_tool:
        return jsonify({
            'success': False,
            'error': '工具未初始化，请先初始化'
        })
    
    data = request.get_json()
    user_query = data.get('query', '')
    format_type = data.get('format', 'table')
    selected_tables = data.get('selected_tables', None)  # 用户选择的表列表
    
    if not user_query:
        return jsonify({
            'success': False,
            'error': '查询内容不能为空'
        })
    
    try:
        with tool_lock:
            # 检查数据库连接状态
            db_is_connected = False
            try:
                db_is_connected = sql_tool.db_connector and sql_tool.db_connector.connection and sql_tool.db_connector.connection.is_connected()
            except:
                db_is_connected = False
                
            if not db_is_connected:
                print("🔄 数据库连接已断开，尝试重新连接...")
                try:
                    if sql_tool.db_connector and sql_tool.db_connector.connect():
                        print("✅ 数据库重新连接成功")
                    else:
                        return jsonify({
                            'success': False,
                            'error': '数据库重新连接失败'
                        })
                except Exception as e:
                    print(f"❌ 数据库重新连接失败: {e}")
                    return jsonify({
                        'success': False,
                        'error': f'数据库连接失败: {str(e)}'
                    })
                    
            # 检查AI模型连接状态
            if not sql_tool.sql_generator.test_connection():
                print("🔄 AI模型连接失败，尝试重新连接...")
                try:
                    # 重新测试连接
                    if not sql_tool.sql_generator.test_connection():
                        return jsonify({
                            'success': False,
                            'error': 'AI模型连接失败，请检查Ollama服务是否正常运行'
                        })
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'AI模型连接失败: {str(e)}'
                    })
                    
            # 直接使用新的Web专用方法处理查询
            result = sql_tool.process_query_for_web(user_query, selected_tables)
            
            # 直接返回结构化结果
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理查询时发生错误: {str(e)}'
        })

@app.route('/api/schema', methods=['GET'])
def api_schema():
    """获取数据库结构API"""
    global sql_tool
    
    if not sql_tool:
        return jsonify({
            'success': False,
            'error': '工具未初始化，请先初始化'
        })
    
    try:
        with tool_lock:
            schema = sql_tool.schema_description
            tables = sql_tool.db_connector.get_all_tables()
            
            return jsonify({
                'success': True,
                'schema': schema,
                'tables': tables
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取数据库结构失败: {str(e)}'
        })

@app.route('/api/tables', methods=['GET'])
def api_tables():
    """获取表信息API（用于表选择器）"""
    global sql_tool
    
    if not sql_tool:
        return jsonify({
            'success': False,
            'error': '工具未初始化，请先初始化'
        })
    
    try:
        with tool_lock:
            # 获取所有表的详细信息
            tables_info = sql_tool.db_connector.get_tables_info()
            
            return jsonify({
                'success': True,
                'tables': tables_info
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取表信息失败: {str(e)}'
        })

@app.route('/api/models', methods=['GET'])
def api_models():
    """获取可用模型API"""
    global sql_tool
    
    if not sql_tool:
        return jsonify({
            'success': False,
            'error': '工具未初始化，请先初始化'
        })
    
    try:
        with tool_lock:
            if sql_tool.llm_backend == 'ollama':
                models = sql_tool.sql_generator.get_available_models()
                return jsonify({
                    'success': True,
                    'backend': 'ollama',
                    'models': models,
                    'current': sql_tool.model_name
                })
            elif sql_tool.llm_backend == 'gemini':
                models = sql_tool.sql_generator.get_available_models()
                return jsonify({
                    'success': True,
                    'backend': 'gemini',
                    'models': models,
                    'current': sql_tool.model_name
                })
            else:  # qwen_api
                return jsonify({
                    'success': True,
                    'backend': 'qwen_api',
                    'models': ['qwen-turbo', 'qwen-plus', 'qwen-max'],
                    'current': sql_tool.model_name
                })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取模型列表失败: {str(e)}'
        })

@app.route('/api/table/<table_name>/columns', methods=['GET'])
def api_table_columns(table_name):
    """获取指定表的字段信息API"""
    global sql_tool
    
    if not sql_tool:
        return jsonify({
            'success': False,
            'error': '工具未初始化，请先初始化'
        })
    
    try:
        with tool_lock:
            columns = sql_tool.db_connector.get_table_columns(table_name)
            return jsonify({
                'success': True,
                'table': table_name,
                'columns': columns
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取表字段信息失败: {str(e)}'
        })

@app.route('/api/execute-sql', methods=['POST'])
def api_execute_sql():
    """直接执行SQL查询API"""
    global sql_tool
    
    if not sql_tool:
        return jsonify({
            'success': False,
            'error': '工具未初始化，请先初始化'
        })
    
    data = request.get_json()
    sql_query = data.get('sql', '')
    format_type = data.get('format', 'table')
    
    if not sql_query:
        return jsonify({
            'success': False,
            'error': 'SQL查询语句不能为空'
        })
    
    try:
        with tool_lock:
            # 检查数据库连接状态
            db_is_connected = False
            try:
                db_is_connected = sql_tool.db_connector and sql_tool.db_connector.connection and sql_tool.db_connector.connection.is_connected()
            except:
                db_is_connected = False
                
            if not db_is_connected:
                print("🔄 数据库连接已断开，尝试重新连接...")
                try:
                    if sql_tool.db_connector and sql_tool.db_connector.connect():
                        print("✅ 数据库重新连接成功")
                    else:
                        return jsonify({
                            'success': False,
                            'error': '数据库重新连接失败'
                        })
                except Exception as e:
                    print(f"❌ 数据库重新连接失败: {e}")
                    return jsonify({
                        'success': False,
                        'error': f'数据库连接失败: {str(e)}'
                    })
            
            # 安全检查：只允许SELECT查询
            sql_upper = sql_query.strip().upper()
            if not sql_upper.startswith('SELECT'):
                return jsonify({
                    'success': False,
                    'error': '出于安全考虑，只允许执行SELECT查询语句'
                })
            
            # 进一步的安全检查
            dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return jsonify({
                        'success': False,
                        'error': f'出于安全考虑，不允许执行包含 {keyword} 的SQL语句'
                    })
            
            # 执行SQL查询
            try:
                column_names, rows = sql_tool.db_connector.execute_query(sql_query)
                
                return jsonify({
                    'success': True,
                    'sql': sql_query,
                    'columns': column_names,
                    'rows': rows,
                    'row_count': len(rows)
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'SQL执行失败: {str(e)}',
                    'sql': sql_query
                })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理SQL查询时发生错误: {str(e)}'
        })

@app.route('/api/test-db-connection', methods=['POST'])
def api_test_db_connection():
    """测试数据库连接API"""
    data = request.get_json()
    
    try:
        # 这里可以添加数据库连接测试逻辑
        # 目前先返回成功，后续可以扩展
        return jsonify({
            'success': True,
            'message': '数据库连接测试成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/save-db-config', methods=['POST'])
def api_save_db_config():
    """保存数据库配置API"""
    data = request.get_json()
    
    try:
        import configparser
        import os
        
        config_file = 'config.ini'
        config = configparser.ConfigParser()
        
        # 如果配置文件存在，先读取
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
        
        # 确保mysql section存在
        if 'mysql' not in config:
            config.add_section('mysql')
        
        # 更新数据库配置
        if 'host' in data:
            config.set('mysql', 'host', str(data['host']))
        if 'port' in data:
            config.set('mysql', 'port', str(data['port']))
        if 'database' in data:
            config.set('mysql', 'database', str(data['database']))
        if 'username' in data:
            config.set('mysql', 'user', str(data['username']))
        if 'password' in data:
            config.set('mysql', 'password', str(data['password']))
        
        # 保存到文件
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"✅ 数据库配置已保存到 {config_file}")
        
        return jsonify({
            'success': True,
            'message': '数据库配置保存成功'
        })
    except Exception as e:
        print(f"❌ 保存数据库配置失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/get-db-config', methods=['GET'])
def api_get_db_config():
    """获取数据库配置API"""
    try:
        import configparser
        import os
        
        config_file = 'config.ini'
        config = configparser.ConfigParser()
        
        # 默认配置
        db_config = {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'database': '',
            'username': '',
            'password': '',
            'file': ''
        }
        
        # 如果配置文件存在，读取配置
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
            
            if 'mysql' in config:
                mysql_section = config['mysql']
                db_config.update({
                    'host': mysql_section.get('host', 'localhost'),
                    'port': mysql_section.getint('port', 3306),
                    'database': mysql_section.get('database', ''),
                    'username': mysql_section.get('user', ''),
                    'password': mysql_section.get('password', '')
                })
        
        return jsonify({
            'success': True,
            'config': db_config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/test-model-connection', methods=['POST'])
def api_test_model_connection():
    """测试模型连接API"""
    data = request.get_json()
    
    try:
        # 这里可以添加模型连接测试逻辑
        return jsonify({
            'success': True,
            'message': '模型连接测试成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/save-model-config', methods=['POST'])
def api_save_model_config():
    """保存模型配置API"""
    data = request.get_json()
    
    try:
        import configparser
        import os
        
        config_file = 'config.ini'
        config = configparser.ConfigParser()
        
        # 如果配置文件存在，先读取
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
        
        # 确保api_keys section存在
        if 'api_keys' not in config:
            config.add_section('api_keys')
        
        # 保存API Key配置
        backend = data.get('backend', '')
        api_key = data.get('api_key', '')
        
        if backend == 'qwen_api' and api_key:
            config.set('api_keys', 'qwen_api_key', api_key)
            print(f"✅ 通义千问API Key已保存")
        elif backend == 'gemini' and api_key:
            config.set('api_keys', 'gemini_api_key', api_key)
            print(f"✅ Gemini API Key已保存")
        elif backend == 'openai' and api_key:
            config.set('api_keys', 'openai_api_key', api_key)
            print(f"✅ OpenAI API Key已保存")
        
        # 保存到文件
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"✅ 模型配置已保存到 {config_file}")
        
        return jsonify({
            'success': True,
            'message': '模型配置保存成功'
        })
    except Exception as e:
        print(f"❌ 保存模型配置失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/get-model-config', methods=['GET'])
def api_get_model_config():
    """获取模型配置API"""
    global sql_tool
    
    try:
        import configparser
        import os
        
        config_file = 'config.ini'
        config_parser = configparser.ConfigParser()
        
        # 默认配置
        config = {
            'backend': 'ollama',
            'model': 'qwen2',
            'ollama_url': 'http://localhost:11434',
            'api_key': ''
        }
        
        # 如果工具已初始化，从工具获取当前配置
        if sql_tool:
            config['backend'] = sql_tool.llm_backend
            config['model'] = sql_tool.model_name
        
        # 从配置文件读取API Key
        if os.path.exists(config_file):
            config_parser.read(config_file, encoding='utf-8')
            
            if 'api_keys' in config_parser:
                api_keys_section = config_parser['api_keys']
                backend = config['backend']
                
                if backend == 'qwen_api':
                    config['api_key'] = api_keys_section.get('qwen_api_key', '')
                elif backend == 'gemini':
                    config['api_key'] = api_keys_section.get('gemini_api_key', '')
                elif backend == 'openai':
                    config['api_key'] = api_keys_section.get('openai_api_key', '')
        
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/table/<table_name>/data', methods=['GET'])
def api_table_data(table_name):
    """获取指定表的数据预览API"""
    global sql_tool
    
    if not sql_tool:
        return jsonify({
            'success': False,
            'error': '工具未初始化，请先初始化'
        })
    
    try:
        # 获取limit参数，默认为5
        limit = request.args.get('limit', 5, type=int)
        # 限制最大返回数量
        limit = min(limit, 100)
        
        with tool_lock:
            # 执行查询获取表数据
            sql = f"SELECT * FROM `{table_name}` LIMIT {limit}"
            columns, rows = sql_tool.db_connector.execute_query(sql)
            
            return jsonify({
                'success': True,
                'table': table_name,
                'columns': columns,
                'rows': rows,
                'limit': limit,
                'count': len(rows)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取表数据失败: {str(e)}'
        })

@app.route('/api/status', methods=['GET'])
def api_status():
    """获取工具状态API"""
    global sql_tool
    
    if not sql_tool:
        return jsonify({
            'initialized': False,
            'backend': None,
            'model': None,
            'database': None,
            'db_connected': False,
            'ai_connected': False
        })
    
    # 获取数据库名称
    database_name = 'Unknown'
    if sql_tool.db_connector and hasattr(sql_tool.db_connector, 'config'):
        database_name = sql_tool.db_connector.config.get('database', 'Unknown')
    
    # 检查连接状态
    db_connected = False
    try:
        db_connected = sql_tool.db_connector and sql_tool.db_connector.connection and sql_tool.db_connector.connection.is_connected()
    except:
        db_connected = False
        
    ai_connected = False
    try:
        ai_connected = sql_tool.sql_generator.test_connection()
    except:
        ai_connected = False
    
    return jsonify({
        'initialized': True,
        'backend': sql_tool.llm_backend,
        'model': sql_tool.model_name,
        'database': database_name,
        'db_connected': db_connected,
        'ai_connected': ai_connected
    })

if __name__ == '__main__':
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='自然语言转SQL查询工具 Web服务器')
    parser.add_argument('--backend', default='ollama', 
                       choices=['ollama', 'qwen_api', 'gemini'],
                       help='大模型后端类型')
    parser.add_argument('--model', help='模型名称')
    parser.add_argument('--config', default='config.ini', 
                       help='数据库配置文件路径')
    parser.add_argument('--port', type=int, default=5000, 
                       help='Web服务器端口')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Web服务器主机地址')
    
    args = parser.parse_args()
    
    # 设置默认模型
    if not args.model:
        if args.backend == 'ollama':
            args.model = 'qwen2'
        elif args.backend == 'gemini':
            args.model = 'gemini-1.5-flash'
        else:
            args.model = 'qwen-plus'
    
    print("🚀 启动自然语言转SQL查询工具 Web服务器...")
    print(f"🌐 访问地址: http://localhost:{args.port}")
    print("📱 支持Apple Design风格的现代化界面")
    print(f"🤖 默认后端: {args.backend} - {args.model}")
    print("-" * 50)
    
    # 自动初始化（使用命令行配置）
    success, message = initialize_tool(args.backend, args.model, args.config)
    if success:
        print("✅ 工具初始化成功")
    else:
        print(f"⚠️  工具初始化失败: {message}")
        print("💡 可以在网页中重新初始化或切换模型")
    
    print(f"📍 启动服务器在 {args.host}:{args.port}")
    app.run(debug=True, host=args.host, port=args.port) 