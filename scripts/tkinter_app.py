#!/usr/bin/env python3
"""
DocAdvisor - Tkinter GUI 入口
"""

import os
import sys
import json
import threading
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 项目根目录
sys.path.insert(0, project_root)

# 加载 .env 文件（从项目根目录）
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from src.engine.config_loader import load_config, render_template
from src.engine.state_manager import ConversationState
from src.engine.node_processor import NodeProcessor
from src.tools.search_cases import search_cases


class DocAdvisorGUI:
    """DocAdvisor GUI 应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DocAdvisor - 通用文档智能顾问")
        self.root.geometry("900x800")
        
        # 初始化状态
        self.config = None
        self.processor = None
        self.is_running = False
        self.state = ConversationState()  # 持久化对话状态
        self.cases_dir = None
        self.env_path = os.path.join(project_root, '.env')  # .env 文件路径
        
        # 加载配置
        self.load_config()
        
        # 创建界面
        self.create_widgets()
        
        # 检查环境变量
        self.check_environment()
    
    def load_config(self):
        """加载配置文件"""
        try:
            config_path = os.path.join(project_root, 'config', 'config.yaml')
            self.config = load_config(config_path)
            
            required = ['name', 'version', 'cases_dir', 'start_node', 'nodes']
            for key in required:
                if key not in self.config:
                    raise ValueError(f"config.yaml 缺少必要字段: {key}")
            
            self.processor = NodeProcessor(self.config)
            self.cases_dir = os.path.join(project_root, self.config['cases_dir'])
        except Exception as e:
            messagebox.showerror("配置错误", f"加载配置失败：{str(e)}")
            sys.exit(1)
    
    def check_environment(self):
        """检查环境变量，如果未配置则提示用户"""
        api_key, model, provider = self.load_env_config()
        if not api_key or not model:
            # 首次运行时，如果未配置，自动弹出提示
            self.root.after(100, self.show_first_time_setup)
    
    def show_first_time_setup(self):
        """首次运行时的配置提示"""
        if not os.path.exists(self.env_path):
            # 如果 .env 文件不存在，提示用户配置
            result = messagebox.askyesno(
                "欢迎使用 DocAdvisor",
                "检测到您首次使用 DocAdvisor！\n\n"
                "需要配置大模型 API Key 才能使用。\n\n"
                "是否现在配置？\n\n"
                "（您也可以稍后点击'模型配置'按钮进行配置）",
                icon='question'
            )
            if result:
                self.open_settings()
    
    def load_env_config(self):
        """从 .env 文件加载配置"""
        # 支持多种API Key格式
        api_key = os.getenv('API_KEY', '').strip('"\'')
        if not api_key:
            api_key = os.getenv('ZHIPU_API_KEY', '').strip('"\'')  # 兼容旧格式
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY', '').strip('"\'')
        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY', '').strip('"\'')
        
        model = os.getenv('MODEL', '').strip('"\'')
        if not model:
            model = os.getenv('ZHIPU_MODEL', 'glm-3-turbo').strip('"\'')  # 兼容旧格式
        
        provider = os.getenv('PROVIDER', 'zhipu').strip('"\'')
        return api_key, model, provider
    
    def save_env_config(self, api_key: str, model: str, provider: str):
        """保存配置到 .env 文件"""
        try:
            # 读取现有配置（如果有）
            existing_config = {}
            if os.path.exists(self.env_path):
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            existing_config[key.strip()] = value.strip()
            
            # 更新配置（使用统一格式）
            existing_config['API_KEY'] = api_key
            existing_config['MODEL'] = model
            existing_config['PROVIDER'] = provider
            
            # 保留旧的ZHIPU配置以兼容（如果使用智谱）
            if provider == 'zhipu':
                existing_config['ZHIPU_API_KEY'] = api_key
                existing_config['ZHIPU_MODEL'] = model
            
            # 写入文件
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.write("# DocAdvisor 配置文件\n")
                f.write("# 请妥善保管您的 API Key，不要泄露给他人\n\n")
                f.write(f"# 统一配置格式\n")
                f.write(f"API_KEY={api_key}\n")
                f.write(f"MODEL={model}\n")
                f.write(f"PROVIDER={provider}\n")
                if provider == 'zhipu':
                    f.write(f"\n# 智谱AI兼容配置\n")
                    f.write(f"ZHIPU_API_KEY={api_key}\n")
                    f.write(f"ZHIPU_MODEL={model}\n")
                elif provider == 'qwen':
                    f.write(f"\n# 通义千问兼容配置\n")
                    f.write(f"DASHSCOPE_API_KEY={api_key}\n")
                elif provider == 'gemini':
                    f.write(f"\n# Gemini兼容配置\n")
                    f.write(f"GEMINI_API_KEY={api_key}\n")
                if provider == 'zhipu':
                    f.write(f"\n# 智谱AI兼容配置\n")
                    f.write(f"ZHIPU_API_KEY={api_key}\n")
                    f.write(f"ZHIPU_MODEL={model}\n")
            
            # 重新加载环境变量
            load_dotenv(self.env_path, override=True)
            
            # 更新 processor 的配置
            if self.processor:
                self.processor.update_api_config(api_key, model, provider)
            
            return True
        except Exception as e:
            messagebox.showerror("保存失败", f"保存配置失败：{str(e)}")
            return False
    
    def update_config_status(self):
        """更新配置状态显示"""
        api_key, model, provider = self.load_env_config()
        if api_key and model:
            status_text = f"当前模型: {model}"
            self.config_status_label.config(text=status_text, fg="green")
        else:
            self.config_status_label.config(text="⚠️ 未配置模型，请点击'模型配置'进行设置", fg="red")
    
    def open_settings(self):
        """打开配置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("模型配置")
        settings_window.geometry("550x450")
        settings_window.resizable(False, False)
        
        # 居中显示
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 加载当前配置
        current_api_key, current_model, current_provider = self.load_env_config()
        
        # 定义各提供商的模型列表
        model_options = {
            'zhipu': ['glm-3-turbo', 'glm-4', 'glm-4-flash', 'glm-4-plus'],
            'openai': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini'],
            'anthropic': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
            'qwen': ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-max-longcontext'],
            'gemini': ['gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro', 'gemini-1.5-flash']
        }
        
        # 标题
        title_label = tk.Label(
            settings_window,
            text="大模型配置",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # 提供商选择
        provider_frame = tk.Frame(settings_window)
        provider_frame.pack(fill=tk.X, padx=20, pady=10)
        
        provider_label = tk.Label(
            provider_frame,
            text="提供商:",
            font=("Arial", 10),
            width=12,
            anchor='w'
        )
        provider_label.pack(side=tk.LEFT)
        
        provider_var = tk.StringVar(value=current_provider)
        provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=provider_var,
            font=("Arial", 10),
            width=37,
            state="readonly"
        )
        provider_combo['values'] = ('zhipu', 'openai', 'anthropic', 'qwen', 'gemini')
        provider_combo.pack(side=tk.LEFT, padx=5)
        
        # Model 选择
        model_frame = tk.Frame(settings_window)
        model_frame.pack(fill=tk.X, padx=20, pady=10)
        
        model_label = tk.Label(
            model_frame,
            text="模型:",
            font=("Arial", 10),
            width=12,
            anchor='w'
        )
        model_label.pack(side=tk.LEFT)
        
        model_var = tk.StringVar(value=current_model if current_model in model_options.get(current_provider, []) else model_options.get(current_provider, [''])[0])
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=model_var,
            font=("Arial", 10),
            width=37,
            state="readonly"
        )
        model_combo['values'] = model_options.get(current_provider, [])
        model_combo.pack(side=tk.LEFT, padx=5)
        
        # 当提供商改变时，更新模型列表
        def on_provider_change(event=None):
            provider = provider_var.get()
            models = model_options.get(provider, [])
            model_combo['values'] = models
            if models:
                model_var.set(models[0])
        
        provider_combo.bind('<<ComboboxSelected>>', on_provider_change)
        
        # API Key 输入
        api_frame = tk.Frame(settings_window)
        api_frame.pack(fill=tk.X, padx=20, pady=10)
        
        api_label = tk.Label(
            api_frame,
            text="API Key:",
            font=("Arial", 10),
            width=12,
            anchor='w'
        )
        api_label.pack(side=tk.LEFT)
        
        api_entry = tk.Entry(
            api_frame,
            font=("Arial", 10),
            width=40,
            show="*"  # 密码形式显示
        )
        api_entry.pack(side=tk.LEFT, padx=5)
        api_entry.insert(0, current_api_key)
        
        # 显示/隐藏 API Key 按钮
        def toggle_api_visibility():
            if api_entry.cget('show') == '*':
                api_entry.config(show='')
                toggle_btn.config(text="隐藏")
            else:
                api_entry.config(show='*')
                toggle_btn.config(text="显示")
        
        toggle_btn = tk.Button(
            api_frame,
            text="显示",
            command=toggle_api_visibility,
            font=("Arial", 8),
            width=6
        )
        toggle_btn.pack(side=tk.LEFT, padx=2)
        
        # 说明文字
        info_text = """配置说明：
1. 提供商：选择大模型服务提供商
   - 智谱AI (zhipu): https://open.bigmodel.cn/
   - OpenAI: https://platform.openai.com/
   - Anthropic (Claude): https://www.anthropic.com/
   - 通义千问 (qwen): https://dashscope.aliyun.com/
   - Google Gemini: https://ai.google.dev/
2. 模型：选择要使用的大模型
3. API Key：从对应提供商获取
4. 配置将保存到项目根目录的 .env 文件"""
        
        info_label = tk.Label(
            settings_window,
            text=info_text,
            font=("Arial", 9),
            fg="gray",
            justify=tk.LEFT,
            anchor='w'
        )
        info_label.pack(fill=tk.X, padx=20, pady=10)
        
        # 按钮区域
        button_frame = tk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        def save_config():
            api_key = api_entry.get().strip()
            model = model_var.get().strip()
            provider = provider_var.get().strip()
            
            if not api_key:
                messagebox.showwarning("配置错误", "请输入 API Key")
                return
            
            if not model:
                messagebox.showwarning("配置错误", "请选择模型")
                return
            
            if not provider:
                messagebox.showwarning("配置错误", "请选择提供商")
                return
            
            if self.save_env_config(api_key, model, provider):
                messagebox.showinfo("成功", "配置已保存！")
                self.update_config_status()
                settings_window.destroy()
        
        save_btn = tk.Button(
            button_frame,
            text="💾 保存",
            command=save_config,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
            height=2
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            command=settings_window.destroy,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 10),
            width=10,
            height=2
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_frame = tk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="🎯 DocAdvisor - 通用文档智能顾问",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="基于 ReAct + RAG 的通用文档智能顾问系统",
            font=("Arial", 10)
        )
        subtitle_label.pack()
        
        # 配置状态显示和设置按钮
        config_frame = tk.Frame(title_frame)
        config_frame.pack(pady=5)
        
        self.config_status_label = tk.Label(
            config_frame,
            text="",
            font=("Arial", 9),
            fg="gray"
        )
        self.config_status_label.pack(side=tk.LEFT, padx=5)
        
        settings_btn = tk.Button(
            config_frame,
            text="⚙️ 模型配置",
            command=self.open_settings,
            bg="#607D8B",
            fg="white",
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=2
        )
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # 更新配置状态显示
        self.update_config_status()
        
        # 输入区域
        input_frame = tk.LabelFrame(self.root, text="输入问题或需求", font=("Arial", 10, "bold"))
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.input_text = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.input_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.submit_btn = tk.Button(
            button_frame,
            text="🚀 提交查询",
            command=self.on_submit,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2
        )
        self.submit_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🔄 清空输入",
            command=self.on_clear_input,
            bg="#f44336",
            fg="white",
            font=("Arial", 10),
            height=2
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.new_chat_btn = tk.Button(
            button_frame,
            text="💬 新建对话",
            command=self.on_new_chat,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10),
            height=2
        )
        self.new_chat_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.StringVar(value="就绪")
        self.progress_label = tk.Label(
            button_frame,
            textvariable=self.progress_var,
            font=("Arial", 9),
            fg="gray"
        )
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        # 使用 PanedWindow 来分配窗口大小
        paned = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 对话历史区域（新增）
        self.history_frame = tk.LabelFrame(paned, text=f"💬 对话历史（当前：{self.state.current_round} 轮）", font=("Arial", 10, "bold"))
        paned.add(self.history_frame, minsize=100)
        
        history_content = tk.Frame(self.history_frame)
        history_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.history_text = scrolledtext.ScrolledText(
            history_content,
            wrap=tk.WORD,
            font=("Arial", 9),
            bg="#f0f0f0",
            height=5,
            state=tk.DISABLED
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # 推理过程区域（较小）
        reasoning_frame = tk.LabelFrame(paned, text="🤔 推理过程", font=("Arial", 10, "bold"))
        paned.add(reasoning_frame, minsize=150)
        
        reasoning_content = tk.Frame(reasoning_frame)
        reasoning_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.reasoning_text = scrolledtext.ScrolledText(
            reasoning_content,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#f5f5f5",
            height=8
        )
        self.reasoning_text.pack(fill=tk.BOTH, expand=True)
        
        # 回答结果区域（较大）
        result_frame = tk.LabelFrame(paned, text="🎯 回答结果", font=("Arial", 10, "bold"))
        paned.add(result_frame, minsize=200)
        
        result_header = tk.Frame(result_frame)
        result_header.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        copy_btn = tk.Button(
            result_header,
            text="📋 一键复制",
            command=self.on_copy_result,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=2
        )
        copy_btn.pack(side=tk.RIGHT)
        
        result_content = tk.Frame(result_frame)
        result_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(
            result_content,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#fff9e6",
            height=15
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 设置 PanedWindow 的初始比例（通过设置 sashpos）
        # 在窗口显示后设置，确保窗口大小已确定
        def set_pane_ratio():
            try:
                self.root.update_idletasks()  # 强制更新布局
                # 获取窗口高度，设置分隔条位置
                height = paned.winfo_height()
                if height > 0:
                    # 第一个分隔条：对话历史区域（约15%）
                    paned.sashpos(0, int(height * 0.15))
                    # 第二个分隔条：推理过程区域（约35%）
                    paned.sashpos(1, int(height * 0.35))
            except Exception as e:
                # 如果设置失败，不影响程序运行
                pass
        
        # 延迟设置，确保窗口已渲染
        self.root.after(200, set_pane_ratio)
        
        # 示例提示
        example_label = tk.Label(
            self.root,
            text="💡 示例：ESG基金的风险是什么？（问答）| 设计一款产品的销售策略（方案生成）",
            font=("Arial", 8),
            fg="gray"
        )
        example_label.pack(pady=5)
    
    def on_submit(self):
        """提交按钮事件"""
        if self.is_running:
            messagebox.showwarning("提示", "正在处理中，请稍候...")
            return
        
        user_demand = self.input_text.get("1.0", tk.END).strip()
        if not user_demand:
            messagebox.showwarning("提示", "请输入您的问题或需求")
            return
        
        # 在新线程中运行，避免界面冻结
        self.is_running = True
        self.submit_btn.config(state=tk.DISABLED)
        self.progress_var.set("处理中...")
        
        thread = threading.Thread(target=self.run_react_agent, args=(user_demand,))
        thread.daemon = True
        thread.start()
    
    def extract_thought(self, text: str) -> str:
        """提取Thought内容"""
        import re
        thought_match = re.search(r'Thought:\s*', text, re.IGNORECASE)
        if thought_match:
            start_pos = thought_match.end()
            next_section = re.search(r'\n\s*(Action:|Final Answer:)', text[start_pos:], re.IGNORECASE)
            if next_section:
                return text[start_pos:start_pos + next_section.start()].strip()
            else:
                return text[start_pos:].strip()
        return ""
    
    def extract_final_answer(self, text: str) -> str:
        """提取Final Answer内容"""
        import re
        final_answer_match = re.search(r'Final Answer:\s*', text, re.IGNORECASE)
        if final_answer_match:
            start_pos = final_answer_match.end()
            next_section = re.search(r'\n\s*(Observation:|Action:)', text[start_pos:], re.IGNORECASE)
            if next_section:
                return text[start_pos:start_pos + next_section.start()].strip()
            else:
                return text[start_pos:].strip()
        else:
            parts = text.split("Final Answer:")
            if len(parts) > 1:
                return parts[-1].strip()
        return ""
    
    def extract_action_json(self, text: str):
        """提取Action中的JSON数据"""
        import re
        action_match = re.search(r'Action:\s*', text, re.IGNORECASE)
        if not action_match:
            return None
        
        action_start = action_match.end()
        action_str = text[action_start:].split("Final Answer:")[0].strip()
        
        # 处理null情况
        if action_str.lower().strip() == "null":
            return None
        
        # 智能提取JSON：找到第一个[或{，提取到匹配的]或}（处理嵌套）
        json_start = -1
        bracket_type = None
        bracket_count = 0
        
        for i, char in enumerate(action_str):
            if char in ['[', '{']:
                if json_start == -1:
                    json_start = i
                    bracket_type = char
                    bracket_count = 1
                elif bracket_type == char:
                    bracket_count += 1
            elif char in [']', '}']:
                if bracket_type == '[' and char == ']':
                    bracket_count -= 1
                elif bracket_type == '{' and char == '}':
                    bracket_count -= 1
                if bracket_count == 0 and json_start != -1:
                    action_str = action_str[json_start:i+1]
                    break
        
        if json_start == -1:
            return None
        
        try:
            return json.loads(action_str)
        except json.JSONDecodeError:
            return None
    
    def run_react_agent(self, user_demand: str):
        """运行 ReAct Agent（在后台线程中）- 真正的循环版本"""
        try:
            # 清空推理过程和结果区域（但保留对话历史）
            self.root.after(0, self.reasoning_text.delete, "1.0", tk.END)
            self.root.after(0, self.result_text.delete, "1.0", tk.END)
            
            # 使用持久化的 state
            self.state.set_variable("user_demand", user_demand)
            
            # 更新对话历史显示
            self.update_history_display()
            
            current_node = self.config['start_node']
            node = self.config['nodes'][current_node]
            max_steps = node.get('max_steps', 6)
            
            # 初始化当前轮次的历史记录（用于ReAct循环）
            current_round_history = []
            
            # 添加多轮对话历史
            if self.state.conversation_turns:
                current_round_history.append("【多轮对话历史】")
                for turn in self.state.conversation_turns[-3:]:
                    current_round_history.append(f"第{turn['round']}轮 - 用户：{turn['user_input']}")
                    current_round_history.append(f"第{turn['round']}轮 - AI：{turn['ai_response']}")
                current_round_history.append("")
            
            # ReAct 循环
            step = 0
            final_answer = None
            while step < max_steps:
                step += 1
                step_msg = f"🤔 第 {step} 步思考中...\n\n"
                self.root.after(0, self.append_reasoning, step_msg)
                
                # 构建历史记录（包含当前轮次的所有 Thought + Action + Observation）
                history_text = "\n".join(current_round_history) if current_round_history else ""
                
                # 渲染prompt
                prompt = render_template(node['prompt_template'], self.state.variables)
                prompt = prompt.replace("{{history}}", history_text)
                
                # 调用LLM（传入工具定义以支持结构化 tool_calls）
                tools_definition = self.processor.get_tools_definition()
                response = self.processor.call_zhipu_ai(prompt, max_tokens=3000, tools=tools_definition)
                
                # 检查是否是结构化响应（包含 tool_calls）
                response_text = ""
                tool_calls = None
                if isinstance(response, dict) and 'tool_calls' in response:
                    # 现代方式：使用 tool_calls
                    response_text = response.get('content', '')
                    tool_calls = response.get('tool_calls', [])
                    response_msg = f"Agent 回复：\n{response_text}\n\n"
                    if tool_calls:
                        response_msg += f"🔧 检测到 {len(tool_calls)} 个工具调用（结构化方式）\n\n"
                    self.root.after(0, self.append_reasoning, response_msg)
                else:
                    # 降级：使用正则表达式提取（兼容旧模型）
                    response_text = response if isinstance(response, str) else str(response)
                    response_msg = f"Agent 回复：\n{response_text}\n\n"
                    self.root.after(0, self.append_reasoning, response_msg)
                
                # 提取并添加Thought到历史记录
                thought = self.extract_thought(response_text)
                if thought:
                    current_round_history.append(f"Thought: {thought}")
                
                # 解析响应：优先使用 tool_calls，降级到正则表达式
                has_action = False
                has_final = False
                action_data = None
                
                if tool_calls:
                    # 现代方式：从 tool_calls 提取 Action
                    has_action = len(tool_calls) > 0
                    if has_action:
                        action_data = []
                        for tool_call in tool_calls:
                            try:
                                func_name = tool_call['function']['name']
                                func_args = json.loads(tool_call['function'].get('arguments', '{}'))
                                action_data.append({
                                    "tool": func_name,
                                    "args": func_args
                                })
                            except (KeyError, json.JSONDecodeError) as e:
                                error_msg = f"⚠️  工具调用解析失败: {e}\n\n"
                                self.root.after(0, self.append_reasoning, error_msg)
                                continue
                        
                        if action_data:
                            current_round_history.append(f"Action: {json.dumps(action_data, ensure_ascii=False)}")
                else:
                    # 降级：使用正则表达式提取（兼容旧方式）
                    response_lower = response_text.lower()
                    has_action = "action:" in response_lower
                    has_final = "final answer:" in response_lower
                    
                    if has_action:
                        action_data = self.extract_action_json(response_text)
                        if action_data:
                            current_round_history.append(f"Action: {json.dumps(action_data, ensure_ascii=False)}")
                        else:
                            # Action为null，也记录到历史
                            current_round_history.append("Action: null")
                
                # 提取Final Answer
                final_answer = None
                if not has_final:
                    has_final = "final answer:" in response_text.lower()
                
                if has_final:
                    final_answer = self.extract_final_answer(response_text)
                    # 记录Final Answer到历史（避免重复）
                    if final_answer:
                        current_round_history.append(f"Final Answer: {final_answer}")
                    # 只要有Final Answer就结束，不需要判断Action
                    if final_answer:
                        self.root.after(0, self.result_text.insert, tk.END, final_answer)
                        self.state.add_conversation_turn(user_demand, final_answer)
                        self.root.after(0, self.update_history_display)
                        self.root.after(0, self.progress_var.set, "完成")
                        return
                
                # 如果有Action，执行工具
                if has_action and action_data:
                    try:
                        if isinstance(action_data, list):
                            actions = action_data
                        else:
                            actions = [action_data]
                        
                        all_observations = []
                        obs_counter = 0  # 用于生成唯一的observation ID
                        for action in actions:
                            tool_name = action.get("tool", "")
                            args = action.get("args", {})
                            
                            tool_msg = f"🔧 执行工具: {tool_name}，参数: {args}\n\n"
                            self.root.after(0, self.append_reasoning, tool_msg)
                            
                            if tool_name == "search_cases":
                                query = args.get("query", "")
                                observation = search_cases(query, self.cases_dir)
                                all_observations.append(observation)
                                # 使用新的方法显示Observation（只显示前3行）
                                obs_id = step * 1000 + obs_counter  # 生成唯一ID
                                obs_counter += 1
                                self.append_observation(observation, obs_id)
                            else:
                                observation = f"未知工具: {tool_name}"
                                all_observations.append(observation)
                                warning_msg = f"⚠️  {observation}\n\n"
                                self.root.after(0, self.append_reasoning, warning_msg)
                        
                        # 将Observation添加到历史记录
                        if all_observations:
                            combined_observation = "\n\n---\n\n".join(all_observations)
                            current_round_history.append(f"Observation: {combined_observation}")
                        
                    except Exception as e:
                        error_msg = f"工具执行失败: {str(e)}"
                        error_display = f"❌ {error_msg}\n\n"
                        self.root.after(0, self.append_reasoning, error_display)
                        current_round_history.append(f"Observation: {error_msg}")
                
                # 如果没有Action也没有Final Answer，提示继续
                if not has_action and not has_final:
                    warning_msg = "⚠️  未检测到 Action 或 Final Answer，继续循环...\n\n"
                    self.root.after(0, self.append_reasoning, warning_msg)
                    current_round_history.append("Observation: 请输出 Action（如果需要检索）或 Final Answer（如果已有足够信息）。")
            
            # 达到最大步数，强制生成答案
            warning_msg = f"⚠️  达到最大步数 {max_steps}，强制生成最终答案...\n\n"
            self.root.after(0, self.append_reasoning, warning_msg)
            force_prompt = f"基于以下历史记录，回答用户问题：{user_demand}\n\n历史记录：\n{history_text}"
            force_response = self.processor.call_zhipu_ai(force_prompt, max_tokens=3000)
            # 处理可能的结构化响应
            if isinstance(force_response, dict) and 'content' in force_response:
                final_answer = force_response['content']
            else:
                final_answer = force_response if isinstance(force_response, str) else str(force_response)
            
            # 显示回答结果
            if final_answer:
                self.root.after(0, self.result_text.insert, tk.END, final_answer)
                self.state.add_conversation_turn(user_demand, final_answer)
                self.root.after(0, self.update_history_display)
            
            self.root.after(0, self.progress_var.set, "完成")
            
        except Exception as e:
            error_msg = f"❌ 程序异常: {str(e)}"
            self.root.after(0, self.append_reasoning, error_msg)
            self.root.after(0, messagebox.showerror, "错误", error_msg)
            self.root.after(0, self.progress_var.set, "错误")
        finally:
            self.is_running = False
            self.root.after(0, self.submit_btn.config, {"state": tk.NORMAL})
    
    def append_reasoning(self, text):
        """追加推理过程文本（线程安全）"""
        self.reasoning_text.insert(tk.END, text)
        self.reasoning_text.see(tk.END)
        self.root.update_idletasks()
    
    def append_observation(self, observation: str, observation_id: int):
        """追加Observation到推理过程，只显示前3行，超过则添加查看详情链接"""
        lines = observation.split('\n')
        preview_lines = lines[:3]
        preview_text = '\n'.join(preview_lines)
        
        # 显示预览
        obs_preview = f"🔍 检索结果：\n{preview_text}"
        
        # 如果超过3行，添加查看详情链接
        if len(lines) > 3:
            remaining_lines = lines[3:]
            remaining_text = '\n'.join(remaining_lines)
            obs_preview += "\n..."
            
            # 在主线程中执行UI更新
            self.root.after(0, lambda: self._insert_observation_with_detail(
                obs_preview, observation_id, observation
            ))
        else:
            # 不超过3行，直接显示
            obs_preview += "\n\n"
            self.root.after(0, lambda: self.append_reasoning(obs_preview))
    
    def _insert_observation_with_detail(self, preview_text: str, obs_id: int, full_observation: str):
        """在推理文本中插入带查看详情链接的Observation"""
        self.reasoning_text.insert(tk.END, preview_text)
        
        # 添加查看详情链接
        detail_tag = f"obs_detail_{obs_id}"
        self.reasoning_text.insert(tk.END, " [查看详情]", detail_tag)
        self.reasoning_text.insert(tk.END, "\n\n")
        
        # 配置链接样式
        self.reasoning_text.tag_config(detail_tag, foreground="#2196F3", underline=True, font=("Consolas", 9, "underline"))
        self.reasoning_text.tag_bind(detail_tag, "<Button-1>", 
                                     lambda e, obs=full_observation: self.show_observation_detail(obs))
        self.reasoning_text.tag_bind(detail_tag, "<Enter>", 
                                     lambda e, tag=detail_tag: self.reasoning_text.config(cursor="hand2"))
        self.reasoning_text.tag_bind(detail_tag, "<Leave>", 
                                     lambda e: self.reasoning_text.config(cursor=""))
        
        self.reasoning_text.see(tk.END)
        self.root.update_idletasks()
    
    def show_observation_detail(self, full_observation: str):
        """显示完整的Observation详情"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title("检索结果详情")
        detail_window.geometry("800x600")
        detail_window.resizable(True, True)
        
        # 创建滚动文本框
        detail_text = scrolledtext.ScrolledText(
            detail_window,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="white",
            padx=10,
            pady=10
        )
        detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 插入完整Observation
        detail_text.insert("1.0", full_observation)
        detail_text.config(state=tk.DISABLED)
        
        # 添加复制按钮
        button_frame = tk.Frame(detail_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        copy_btn = tk.Button(
            button_frame,
            text="📋 复制内容",
            command=lambda: self.copy_to_clipboard(full_observation, detail_window),
            bg="#2196F3",
            fg="white",
            font=("Arial", 9),
            padx=15,
            pady=5
        )
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(
            button_frame,
            text="关闭",
            command=detail_window.destroy,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 9),
            padx=15,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def on_clear_input(self):
        """清空输入框"""
        self.input_text.delete("1.0", tk.END)
    
    def on_new_chat(self):
        """新建对话按钮事件"""
        if self.is_running:
            messagebox.showwarning("提示", "正在处理中，请稍候...")
            return
        
        # 确认对话框
        if messagebox.askyesno("确认", "确定要开始新对话吗？这将清空所有对话历史。"):
            self.state.clear_history()
            self.input_text.delete("1.0", tk.END)
            self.reasoning_text.delete("1.0", tk.END)
            self.result_text.delete("1.0", tk.END)
            self.progress_var.set("就绪")
            self.update_history_display()
            messagebox.showinfo("成功", "已开始新对话")
    
    def show_answer_detail(self, round_num: int, full_answer: str):
        """显示完整的AI回答详情"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"第 {round_num} 轮 - AI 完整回答")
        detail_window.geometry("800x600")
        detail_window.resizable(True, True)
        
        # 创建滚动文本框
        detail_text = scrolledtext.ScrolledText(
            detail_window,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="white",
            padx=10,
            pady=10
        )
        detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 插入完整回答
        detail_text.insert("1.0", full_answer)
        detail_text.config(state=tk.DISABLED)
        
        # 添加复制按钮
        button_frame = tk.Frame(detail_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        copy_btn = tk.Button(
            button_frame,
            text="📋 复制内容",
            command=lambda: self.copy_to_clipboard(full_answer, detail_window),
            bg="#2196F3",
            fg="white",
            font=("Arial", 9),
            padx=15,
            pady=5
        )
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(
            button_frame,
            text="关闭",
            command=detail_window.destroy,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 9),
            padx=15,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def copy_to_clipboard(self, content: str, window: tk.Toplevel):
        """复制内容到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("成功", "内容已复制到剪贴板！", parent=window)
    
    def update_history_display(self):
        """更新对话历史显示"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)
        
        # 更新标题
        self.history_frame.config(text=f"💬 对话历史（当前：{self.state.current_round} 轮）")
        
        if self.state.conversation_turns:
            for idx, turn in enumerate(self.state.conversation_turns):
                self.history_text.insert(tk.END, f"第 {turn['round']} 轮\n", "round_tag")
                self.history_text.insert(tk.END, f"  用户：{turn['user_input']}\n", "user_tag")
                
                # 显示AI回答的预览
                preview = turn['ai_response'][:100] + "..." if len(turn['ai_response']) > 100 else turn['ai_response']
                self.history_text.insert(tk.END, f"  AI：{preview}", "ai_tag")
                
                # 如果回答超过100字符，添加"查看详情"链接
                if len(turn['ai_response']) > 100:
                    detail_tag = f"detail_{idx}"
                    self.history_text.insert(tk.END, " [查看详情]", detail_tag)
                    self.history_text.tag_config(detail_tag, foreground="#2196F3", underline=True, font=("Arial", 9, "underline"))
                    self.history_text.tag_bind(detail_tag, "<Button-1>", 
                                              lambda e, r=turn['round'], a=turn['ai_response']: self.show_answer_detail(r, a))
                    self.history_text.tag_bind(detail_tag, "<Enter>", 
                                              lambda e, tag=detail_tag: self.history_text.config(cursor="hand2"))
                    self.history_text.tag_bind(detail_tag, "<Leave>", 
                                              lambda e: self.history_text.config(cursor=""))
                
                self.history_text.insert(tk.END, "\n\n", "ai_tag")
        else:
            self.history_text.insert(tk.END, "暂无对话历史\n", "empty_tag")
        
        # 配置标签样式
        self.history_text.tag_config("round_tag", font=("Arial", 9, "bold"), foreground="#2196F3")
        self.history_text.tag_config("user_tag", font=("Arial", 9), foreground="#4CAF50")
        self.history_text.tag_config("ai_tag", font=("Arial", 9), foreground="#666666")
        self.history_text.tag_config("empty_tag", font=("Arial", 9), foreground="#999999")
        
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
    
    def on_copy_result(self):
        """复制回答结果到剪贴板"""
        content = self.result_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("提示", "回答结果为空，无法复制")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("成功", "回答结果已复制到剪贴板！")


def main():
    """主函数"""
    root = tk.Tk()
    app = DocAdvisorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

