# -*- coding: utf-8 -*-
"""
状态管理器 - 管理对话状态和数据
"""

class ConversationState:
    """管理对话状态和变量"""
    
    def __init__(self):
        #存储所有变量（用户输入、AI回复等）
        self.variables = {}
        
        # 记录当前执行到哪个节点
        self.current_node = "start"
        
        #对话历史记录（用于调试和追溯）
        self.history = []
        
        # 多轮对话记录（每轮包含用户输入和AI回复）
        self.conversation_turns = []
        
        # 当前对话轮次
        self.current_round = 0
        
        # print("对话状态管理器初始化完成")  # 减少启动时的输出
    
    def set_variable(self, key, value):
        """保存变量到状态中"""
        self.variables[key] = value
        self.history.append(f"保存变量: {key} = {value}")
        # print(f"变量已保存: {key} = {value}")  # 减少输出
    
    def get_variable(self, key, default=None):
        """从状态中获取变量"""
        value = self.variables.get(key, default)
        return value
    
    def move_to_node(self, node_name):
        """跳转到指定节点"""
        old_node = self.current_node
        self.current_node = node_name
        self.history.append(f"节点跳转: {old_node} → {node_name}")
    
    def add_conversation_turn(self, user_input: str, ai_response: str):
        """添加一轮对话记录"""
        self.current_round += 1
        turn = {
            "round": self.current_round,
            "user_input": user_input,
            "ai_response": ai_response
        }
        self.conversation_turns.append(turn)
    
    def get_recent_turns(self, n: int = 3):
        """获取最近 n 轮对话"""
        return self.conversation_turns[-n:] if self.conversation_turns else []
    
    def clear_history(self):
        """清空对话历史，开始新对话"""
        self.variables = {}
        self.current_node = "start"
        self.history = []
        self.conversation_turns = []
        self.current_round = 0
    
    def display_status(self):
        """显示当前状态概览"""
        print("\n" + "="*50)
        print("当前对话状态:")
        print(f"   当前节点: {self.current_node}")
        print(f"   当前轮次: {self.current_round}")
        print(f"   存储变量: {len(self.variables)} 个")
        for key, value in self.variables.items():
            print(f"     - {key}: {value}")
        print(f"   对话轮次: {len(self.conversation_turns)} 轮")
        print("="*50)

