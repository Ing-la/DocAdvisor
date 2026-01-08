# -*- coding: utf-8 -*-
"""
配置加载器 - 读取和解析YAML配置文件
"""

import yaml
import os

def load_config(config_path="config.yaml"):
    """
    加载YAML配置文件
    
    返回:
        config字典对象
    """
    # print(f"正在加载配置文件: {config_path}")  # 减少启动时的输出
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        # print("配置文件加载成功")  # 减少启动时的输出
        return config
    except yaml.YAMLError as e:
        print(f"YAML格式错误: {e}")
        raise

def validate_config(config):
    """
    验证配置文件格式是否正确
    """
    # print("验证配置文件完整性...")  # 减少启动时的输出
    
    # 检查必需字段
    required_keys = ['name', 'version', 'start_node', 'nodes']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"缺少必需字段: {key}")
    
    # 检查起始节点是否存在
    start_node = config['start_node']
    if start_node not in config['nodes']:
        raise ValueError(f"起始节点不存在: {start_node}")
    
    # print(f"配置验证通过: {config['name']} v{config['version']}")  # 减少启动时的输出

def render_template(template, variables):
    """
    模板渲染：将 {{变量名}} 替换为实际值
    
    示例:
        render_template("你好{{name}}", {"name": "张三"})
        返回: "你好张三"
    """
    result = template
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    return result

