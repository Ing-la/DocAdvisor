#!/usr/bin/env python3
"""
DocAdvisor - ReAct 命令行主入口
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 项目根目录
sys.path.insert(0, project_root)

from src.engine.config_loader import load_config, render_template
from src.engine.state_manager import ConversationState
from src.engine.node_processor import NodeProcessor
from src.tools.search_cases import search_cases


def extract_thought(text: str) -> str:
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


def extract_final_answer(text: str) -> str:
    """提取Final Answer内容"""
    import re
    final_answer_match = re.search(r'Final Answer:\s*', text, re.IGNORECASE)
    if final_answer_match:
        start_pos = final_answer_match.end()
        # 查找下一个section（Observation或Action）或文本结束
        next_section = re.search(r'\n\s*(Observation:|Action:)', text[start_pos:], re.IGNORECASE)
        if next_section:
            return text[start_pos:start_pos + next_section.start()].strip()
        else:
            return text[start_pos:].strip()
    else:
        # 如果没有找到Final Answer标记，尝试从文本末尾提取
        parts = text.split("Final Answer:")
        if len(parts) > 1:
            return parts[-1].strip()
    return ""


def extract_action_json(text: str):
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


def run_react_cycle(user_demand: str, state: ConversationState, processor: NodeProcessor, 
                    config: dict, cases_dir: str) -> str:
    """
    执行 ReAct 循环（真正的循环版本）
    
    流程：
    1. LLM 思考并输出 Thought + Action + Final Answer
    2. 如果有 Action，执行工具，获得 Observation
    3. 将 Observation 添加到历史记录
    4. 如果有 Final Answer（且无 Action），返回结果
    5. 如果没有 Final Answer，继续循环（最多 max_steps 次）
    
    Args:
        user_demand: 用户需求
        state: 对话状态
        processor: 节点处理器
        config: 配置信息
        cases_dir: 案例目录路径
        
    Returns:
        最终答案
    """
    state.set_variable("user_demand", user_demand)
    
    current_node = config['start_node']
    node = config['nodes'][current_node]
    max_steps = node.get('max_steps', 6)
    
    # 初始化当前轮次的历史记录（用于ReAct循环）
    current_round_history = []
    
    # 添加多轮对话历史
    if state.conversation_turns:
        current_round_history.append("【多轮对话历史】")
        for turn in state.conversation_turns[-3:]:
            current_round_history.append(f"第{turn['round']}轮 - 用户：{turn['user_input']}")
            current_round_history.append(f"第{turn['round']}轮 - AI：{turn['ai_response']}")
        current_round_history.append("")
    
    # ReAct 循环
    step = 0
    while step < max_steps:
        step += 1
        print(f"\n🤔 第 {step} 步思考中...")
        
        # 构建历史记录（包含当前轮次的所有 Thought + Action + Observation）
        history_text = "\n".join(current_round_history) if current_round_history else ""
        
        # 渲染prompt
        prompt = render_template(node['prompt_template'], state.variables)
        prompt = prompt.replace("{{history}}", history_text)
        
        # 调用LLM
        response = processor.call_zhipu_ai(prompt, max_tokens=3000)
        print(f"\nAgent 回复：\n{response}")
        
        # 提取并添加Thought到历史记录
        thought = extract_thought(response)
        if thought:
            current_round_history.append(f"Thought: {thought}")
        
        # 解析响应
        response_lower = response.lower()
        has_action = "action:" in response_lower
        has_final = "final answer:" in response_lower
        
        # 提取Action
        action_data = None
        if has_action:
            action_data = extract_action_json(response)
            if action_data:
                current_round_history.append(f"Action: {json.dumps(action_data, ensure_ascii=False)}")
            else:
                # Action为null，也记录到历史
                current_round_history.append("Action: null")
        
        # 提取Final Answer
        final_answer = None
        if has_final:
            final_answer = extract_final_answer(response)
            # 记录Final Answer到历史（避免重复）
            if final_answer:
                current_round_history.append(f"Final Answer: {final_answer}")
            # 只要有Final Answer就结束，不需要判断Action
            if final_answer:
                print(f"\n🎯 最终答案：\n{final_answer}")
                return final_answer
        
        # 如果有Action，执行工具
        if has_action and action_data:
            try:
                if isinstance(action_data, list):
                    actions = action_data
                else:
                    actions = [action_data]
                
                all_observations = []
                for action in actions:
                    tool_name = action.get("tool", "")
                    args = action.get("args", {})
                    
                    print(f"🔧 执行工具: {tool_name}，参数: {args}")
                    
                    if tool_name == "search_cases":
                        query = args.get("query", "")
                        observation = search_cases(query, cases_dir)
                        all_observations.append(observation)
                        print(f"🔍 检索结果：\n{observation}")
                    else:
                        observation = f"未知工具: {tool_name}"
                        all_observations.append(observation)
                        print(f"⚠️  {observation}")
                
                # 将Observation添加到历史记录
                if all_observations:
                    combined_observation = "\n\n---\n\n".join(all_observations)
                    current_round_history.append(f"Observation: {combined_observation}")
                
            except Exception as e:
                error_msg = f"工具执行失败: {str(e)}"
                print(f"❌ {error_msg}")
                current_round_history.append(f"Observation: {error_msg}")
        
        # 如果没有Action也没有Final Answer，提示继续
        if not has_action and not has_final:
            print("⚠️  未检测到 Action 或 Final Answer，继续循环...")
            current_round_history.append("Observation: 请输出 Action（如果需要检索）或 Final Answer（如果已有足够信息）。")
    
    # 达到最大步数，强制生成答案
    print(f"\n⚠️  达到最大步数 {max_steps}，强制生成最终答案...")
    force_prompt = f"基于以下历史记录，回答用户问题：{user_demand}\n\n历史记录：\n{history_text}"
    final_answer = processor.call_zhipu_ai(force_prompt, max_tokens=3000)
    print(f"\n🎯 最终答案：\n{final_answer}")
    return final_answer


def main():
    print("DocAdvisor - 通用文档智能顾问启动中...")
    print("=" * 60)

    try:
        # 配置文件路径：config/config.yaml
        config_path = os.path.join(project_root, 'config', 'config.yaml')
        config = load_config(config_path)

        required = ['name', 'version', 'cases_dir', 'start_node', 'nodes']
        for key in required:
            if key not in config:
                raise ValueError(f"config.yaml 缺少必要字段: {key}")

        state = ConversationState()
        processor = NodeProcessor(config)
        cases_dir = os.path.join(project_root, config['cases_dir'])

        print(f"欢迎使用 {config['name']} v{config['version']}")
        print("我可以帮您基于文档知识库生成专业方案和建议")
        print("=" * 60)
        print("\n💡 提示：")
        print("  - 输入 'exit' 或 'quit' 退出程序")
        print("  - 输入 'new' 开始新对话（清空历史）")
        print("  - 直接输入问题可继续对话")
        print("=" * 60)

        # 多轮对话循环
        while True:
            # 显示对话历史摘要
            if state.conversation_turns:
                print(f"\n📋 当前对话轮次：{state.current_round} 轮")
                recent = state.get_recent_turns(2)
                if recent:
                    print("最近对话：")
                    for turn in recent:
                        print(f"  第{turn['round']}轮 - {turn['user_input'][:60]}...")
                print("-" * 60)
            
            user_demand = input(f"\n[第 {state.current_round + 1} 轮] 请输入您的问题或需求：\n").strip()
            
            if not user_demand:
                print("输入不能为空，请重新输入。")
                continue
            
            # 处理特殊命令
            user_demand_lower = user_demand.lower()
            if user_demand_lower in ['exit', 'quit', '退出']:
                print("\n感谢使用 DocAdvisor，再见！")
                break
            
            if user_demand_lower in ['new', 'newchat', '新对话', '清空']:
                state.clear_history()
                print("✅ 已清空对话历史，开始新对话")
                continue
            
            # 执行 ReAct 循环
            try:
                final_answer = run_react_cycle(user_demand, state, processor, config, cases_dir)
                
                # 记录本轮对话
                if final_answer:
                    state.add_conversation_turn(user_demand, final_answer)
                
                print("\n" + "=" * 60)
                print("本轮对话完成")
                print("=" * 60)
                
            except KeyboardInterrupt:
                print("\n\n用户中断，退出程序")
                break
            except Exception as e:
                print(f"\n❌ 处理异常: {e}")
                import traceback
                traceback.print_exc()
                print("\n您可以继续输入新问题，或输入 'exit' 退出")

    except Exception as e:
        print(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

