# -*- coding: utf-8 -*-
"""
节点处理器 - 执行各种类型的节点逻辑
"""

import colorama
from colorama import Fore, Style
import requests
import os
import json
from dotenv import load_dotenv
from .config_loader import render_template

# 初始化彩色输出
colorama.init()

class NodeProcessor:
    """处理所有类型节点的执行逻辑"""
    
    def __init__(self, config):
        self.config = config
        self.nodes = config['nodes']
        # 加载环境变量
        load_dotenv()
        
        # 支持多种API Key格式
        self.api_key = os.getenv('API_KEY', '').strip('"\'')
        if not self.api_key:
            self.api_key = os.getenv('ZHIPU_API_KEY', '').strip('"\'')  # 兼容旧格式
        if not self.api_key:
            self.api_key = os.getenv('OPENAI_API_KEY', '').strip('"\'')
        if not self.api_key:
            self.api_key = os.getenv('ANTHROPIC_API_KEY', '').strip('"\'')
        if not self.api_key:
            self.api_key = os.getenv('DASHSCOPE_API_KEY', '').strip('"\'')  # 通义千问
        if not self.api_key:
            self.api_key = os.getenv('GEMINI_API_KEY', '').strip('"\'')  # Gemini
        
        self.model = os.getenv('MODEL', '').strip('"\'')
        if not self.model:
            self.model = os.getenv('ZHIPU_MODEL', 'glm-3-turbo').strip('"\'')  # 兼容旧格式
        
        self.provider = os.getenv('PROVIDER', 'zhipu').strip('"\'')
        
        # 兼容旧代码
        self.zhipu_api_key = self.api_key
        self.zhipu_model = self.model
    
    def update_api_config(self, api_key: str, model: str, provider: str = 'zhipu'):
        """
        动态更新 API Key、Model 和 Provider
        
        Args:
            api_key: 新的 API Key
            model: 新的模型名称
            provider: 模型提供商 (zhipu/openai/anthropic)
        """
        self.api_key = api_key.strip('"\'')
        self.model = model.strip('"\'')
        self.provider = provider.strip('"\'')
        
        # 兼容旧代码
        self.zhipu_api_key = self.api_key
        self.zhipu_model = self.model
    
    def get_tools_definition(self):
        """
        获取工具定义（用于结构化 tool_calls）
        
        Returns:
            list: 工具定义列表
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_cases",
                    "description": "检索文档知识库，根据关键词查找相关文档片段",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "检索关键词，用空格分隔，例如：'ESG 销售' 或 '基金产品'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    def call_zhipu_ai(self, prompt, max_tokens=None, tools=None):
        """
        调用大模型 API（支持多个提供商）
        
        Args:
            prompt: 提示词
            max_tokens: 最大输出token数，None时使用默认值
                       - 默认值：1500（适合 Thought/Action）
                       - Final Answer 建议使用：3000
            tools: 工具定义列表，None时使用默认工具定义
        
        Returns:
            str 或 dict: 
                - 如果模型返回 tool_calls，返回 dict: {'content': str, 'tool_calls': list}
                - 否则返回 str（纯文本响应，兼容旧方式）
        """
        if not self.api_key:
            return "请配置API_KEY环境变量"
        
        if len(self.api_key) < 10:
            return f"API密钥格式可能不正确，长度: {len(self.api_key)}"
        
        # 如果没有指定，使用默认值
        if max_tokens is None:
            max_tokens = 1500  # 默认值，适合 Thought/Action 阶段
        
        # 如果没有指定工具，使用默认工具定义
        if tools is None:
            tools = self.get_tools_definition()
        
        # 根据提供商选择不同的API端点
        if self.provider == 'openai':
            return self._call_openai(prompt, max_tokens, tools)
        elif self.provider == 'anthropic':
            return self._call_anthropic(prompt, max_tokens, tools)
        elif self.provider == 'qwen':
            return self._call_qwen(prompt, max_tokens, tools)
        elif self.provider == 'gemini':
            return self._call_gemini(prompt, max_tokens, tools)
        else:  # 默认使用智谱AI
            return self._call_zhipu(prompt, max_tokens, tools)
    
    def _call_with_retry(self, url, headers, data, provider_name, max_retries=2, timeout=90, params=None):
        """带重试机制的API调用"""
        import time
        for attempt in range(max_retries + 1):
            try:
                print(Fore.BLUE + f"   正在调用 {self.model} ({provider_name})..." + Style.RESET_ALL)
                if attempt > 0:
                    print(Fore.YELLOW + f"   第 {attempt + 1} 次重试（等待 {attempt} 秒）..." + Style.RESET_ALL)
                    time.sleep(attempt)  # 重试前等待
                
                if params:
                    response = requests.post(url, headers=headers, json=data, params=params, timeout=timeout)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=timeout)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    error_msg = f"API调用失败: {response.status_code} - {response.text}"
                    print(Fore.RED + f"   {error_msg}" + Style.RESET_ALL)
                    if attempt < max_retries:
                        continue
                    return {"error": error_msg}
                    
            except requests.exceptions.Timeout:
                error_msg = f"请求超时（{timeout}秒）"
                print(Fore.RED + f"   {error_msg}" + Style.RESET_ALL)
                if attempt < max_retries:
                    print(Fore.YELLOW + f"   正在重试..." + Style.RESET_ALL)
                    continue
                return {"error": f"请求超时，已重试{max_retries}次仍失败"}
            except Exception as e:
                error_msg = f"请求异常: {str(e)}"
                print(Fore.RED + f"   {error_msg}" + Style.RESET_ALL)
                if attempt < max_retries:
                    continue
                return {"error": error_msg}
        
        return {"error": "请求失败"}
    
    def _call_zhipu(self, prompt, max_tokens, tools=None):
        """调用智谱AI API"""
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens
        }
        
        # 如果提供了工具定义，添加到请求中
        if tools:
            data["tools"] = tools
            data["tool_choice"] = "auto"  # 让模型决定是否调用工具
        
        result = self._call_with_retry(url, headers, data, "智谱AI")
        if "error" in result:
            return result["error"]
        try:
            if 'choices' not in result or not result['choices']:
                return f"API返回格式异常：缺少choices字段。返回内容：{str(result)[:500]}"
            
            message = result['choices'][0]['message']
            
            # 检查是否有 tool_calls（现代方式）
            if 'tool_calls' in message and message['tool_calls']:
                return {
                    'content': message.get('content', ''),
                    'tool_calls': message['tool_calls']
                }
            
            # 降级：返回纯文本（兼容旧方式）
            return message.get('content', '')
        except (KeyError, IndexError, TypeError) as e:
            return f"API返回格式解析失败：{str(e)}。返回内容：{str(result)[:500]}"
    
    def _call_openai(self, prompt, max_tokens, tools=None):
        """调用OpenAI API"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens
        }
        
        # 如果提供了工具定义，添加到请求中
        if tools:
            data["tools"] = tools
            data["tool_choice"] = "auto"
        
        result = self._call_with_retry(url, headers, data, "OpenAI")
        if "error" in result:
            return result["error"]
        try:
            if 'choices' not in result or not result['choices']:
                return f"API返回格式异常：缺少choices字段。返回内容：{str(result)[:500]}"
            
            message = result['choices'][0]['message']
            
            # 检查是否有 tool_calls（现代方式）
            if 'tool_calls' in message and message['tool_calls']:
                return {
                    'content': message.get('content', ''),
                    'tool_calls': message['tool_calls']
                }
            
            # 降级：返回纯文本（兼容旧方式）
            return message.get('content', '')
        except (KeyError, IndexError, TypeError) as e:
            return f"API返回格式解析失败：{str(e)}。返回内容：{str(result)[:500]}"
    
    def _call_anthropic(self, prompt, max_tokens, tools=None):
        """调用Anthropic (Claude) API"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        # Anthropic 使用 tools 参数（如果提供）
        if tools:
            # 转换工具格式为 Anthropic 格式
            anthropic_tools = []
            for tool in tools:
                if tool.get('type') == 'function':
                    anthropic_tools.append({
                        "name": tool['function']['name'],
                        "description": tool['function'].get('description', ''),
                        "input_schema": tool['function']['parameters']
                    })
            if anthropic_tools:
                data["tools"] = anthropic_tools
        
        result = self._call_with_retry(url, headers, data, "Anthropic")
        if "error" in result:
            return result["error"]
        try:
            if 'content' not in result or not result['content']:
                return f"API返回格式异常：缺少content字段。返回内容：{str(result)[:500]}"
            
            # Anthropic 返回格式：content 是数组，可能包含 text 或 tool_use
            content_items = result['content']
            tool_calls = []
            text_content = []
            
            for item in content_items:
                if item.get('type') == 'tool_use':
                    # 转换 Anthropic 的 tool_use 格式为标准格式
                    tool_calls.append({
                        'id': item.get('id', ''),
                        'type': 'function',
                        'function': {
                            'name': item.get('name', ''),
                            'arguments': json.dumps(item.get('input', {}))
                        }
                    })
                elif item.get('type') == 'text':
                    text_content.append(item.get('text', ''))
            
            # 如果有 tool_calls，返回结构化响应
            if tool_calls:
                return {
                    'content': '\n'.join(text_content),
                    'tool_calls': tool_calls
                }
            
            # 降级：返回纯文本
            return result['content'][0].get('text', '')
        except (KeyError, IndexError, TypeError) as e:
            return f"API返回格式解析失败：{str(e)}。返回内容：{str(result)[:500]}"
    
    def _call_qwen(self, prompt, max_tokens, tools=None):
        """调用通义千问 API"""
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "max_tokens": max_tokens,
                "result_format": "message"  # 添加这个参数，确保返回message格式
            }
        }
        
        # 如果提供了工具定义，添加到请求中
        if tools:
            data["input"]["tools"] = tools
        
        result = self._call_with_retry(url, headers, data, "通义千问")
        if "error" in result:
            return result["error"]
        try:
            if 'output' not in result:
                return f"API返回格式异常：缺少output字段。返回内容：{str(result)[:500]}"
            
            output = result['output']
            
            # 检查是否有 tool_calls
            if 'choices' in output and output['choices']:
                message = output['choices'][0].get('message', {})
                if 'tool_calls' in message and message['tool_calls']:
                    return {
                        'content': message.get('content', ''),
                        'tool_calls': message['tool_calls']
                    }
                # 降级：返回纯文本
                return message.get('content', '') or output.get('text', '')
            
            # 优先尝试直接返回text格式（通义千问的默认格式）
            if 'text' in output:
                return output['text']
            
            # 如果都没有，返回错误信息
            return f"API返回格式异常：output中既没有text也没有choices字段。返回内容：{str(output)[:500]}"
        except (KeyError, IndexError, TypeError) as e:
            return f"API返回格式解析失败：{str(e)}。返回内容：{str(result)[:500]}"
    
    def _call_gemini(self, prompt, max_tokens, tools=None):
        """调用Google Gemini API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": self.api_key
        }
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens
            }
        }
        
        # Gemini 使用 tools 参数（如果提供）
        if tools:
            # 转换工具格式为 Gemini 格式
            gemini_tools = {
                "functionDeclarations": []
            }
            for tool in tools:
                if tool.get('type') == 'function':
                    gemini_tools["functionDeclarations"].append({
                        "name": tool['function']['name'],
                        "description": tool['function'].get('description', ''),
                        "parameters": tool['function']['parameters']
                    })
            if gemini_tools["functionDeclarations"]:
                data["tools"] = [gemini_tools]
        
        result = self._call_with_retry(url, headers, data, "Gemini", params=params)
        if "error" in result:
            return result["error"]
        try:
            if 'candidates' not in result or not result['candidates']:
                return f"API返回格式异常：缺少candidates字段。返回内容：{str(result)[:500]}"
            
            candidate = result['candidates'][0]
            parts = candidate.get('content', {}).get('parts', [])
            
            # 检查是否有 functionCall（Gemini 的工具调用格式）
            tool_calls = []
            text_content = []
            
            for part in parts:
                if 'functionCall' in part:
                    # 转换 Gemini 的 functionCall 格式为标准格式
                    func_call = part['functionCall']
                    tool_calls.append({
                        'id': f"gemini_{func_call.get('name', '')}",
                        'type': 'function',
                        'function': {
                            'name': func_call.get('name', ''),
                            'arguments': json.dumps(func_call.get('args', {}))
                        }
                    })
                elif 'text' in part:
                    text_content.append(part['text'])
            
            # 如果有 tool_calls，返回结构化响应
            if tool_calls:
                return {
                    'content': '\n'.join(text_content),
                    'tool_calls': tool_calls
                }
            
            # 降级：返回纯文本
            return parts[0].get('text', '') if parts else ''
        except (KeyError, IndexError, TypeError) as e:
            return f"API返回格式解析失败：{str(e)}。返回内容：{str(result)[:500]}"
    
    def process_node(self, node_name, state):
        """执行指定节点的逻辑"""
        if node_name not in self.nodes:
            print(Fore.RED + f" 错误：节点 '{node_name}' 不存在" + Style.RESET_ALL)
            return "end"
        
        node = self.nodes[node_name]
        node_type = node.get('type', 'unknown')
        
        print(Fore.CYAN + f"\n[{node_type.upper()}] " + Style.RESET_ALL, end="")
        
        # 根据type调用对应的处理函数
        processor_method = getattr(self, f"process_{node_type}", self.process_unknown)
        next_node = processor_method(node, state)
        
        return next_node or node.get('next')
    
    def process_start(self, node, state):
        """处理开始节点"""
        print("对话开始")
        return node.get('next')
    
    def process_input(self, node, state):
        """处理输入节点"""
        prompt = node.get('prompt', '请输入: ')
        variable_name = node.get('variable', 'user_input')
        
        user_input = input(Fore.YELLOW + prompt + Style.RESET_ALL)
        state.set_variable(variable_name, user_input)
        
        return node.get('next')
    
    def process_message(self, node, state):
        """处理消息节点"""
        content = node.get('content', '')
        rendered_content = render_template(content, state.variables)
        print(Fore.GREEN + rendered_content + Style.RESET_ALL)
        return node.get('next')
    
    def process_llm_call(self, node, state):
        """处理大模型调用节点 - 调用真实的AI API"""
        print("调用AI模型中...")
        
        try:
            prompt_template = node.get('prompt_template', '')
            rendered_prompt = render_template(prompt_template, state.variables)
            
            print(Fore.BLUE + f"   给AI的提示: {rendered_prompt[:100]}..." + Style.RESET_ALL)
            
            # 调用真实的大模型API
            ai_response = self.call_zhipu_ai(rendered_prompt)
            
            variable_name = node.get('variable', 'ai_response')
            state.set_variable(variable_name, ai_response)
            
            print(Fore.BLUE + "   AI回复生成完成" + Style.RESET_ALL)
            
            return node.get('next')
            
        except Exception as e:
            print(Fore.RED + f"    AI调用失败: {e}" + Style.RESET_ALL)
            user_question = state.get_variable("user_question", "未知问题")
            fallback_response = f"抱歉，AI服务暂时不可用。您的问题是：{user_question}"
            state.set_variable(node.get('variable', 'ai_response'), fallback_response)
            return node.get('next')
    
    def process_condition(self, node, state):
        """处理条件判断节点"""
        print("进行条件判断...")
        user_choice = state.get_variable('continue_choice', '').lower()
        
        if user_choice == 'y':
            print("   条件为真 → 继续对话")
            return node.get('if_true')
        else:
            print("   条件为假 → 结束对话") 
            return node.get('if_false')
    
    def process_end(self, node, state):
        """处理结束节点"""
        message = node.get('message', '对话结束')
        print(Fore.MAGENTA + f"{message}" + Style.RESET_ALL)
        return "EXIT"
    
    def process_unknown(self, node, state):
        """处理未知节点类型"""
        print(Fore.RED + f"未知的节点类型: {node.get('type')}" + Style.RESET_ALL)
        return "end"

