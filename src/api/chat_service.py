from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional
from uuid import uuid4

from src.engine.config_loader import load_config, render_template
from src.engine.node_processor import NodeProcessor
from src.engine.state_manager import ConversationState
from src.tools.search_cases import search_cases
from .schemas import SourceChunk, ThoughtStep

TraceCallback = Optional[Callable[[str, Dict], None]]


@dataclass
class SessionRuntime:
    state: ConversationState = field(default_factory=ConversationState)
    last_trace: List[ThoughtStep] = field(default_factory=list)
    last_sources: List[SourceChunk] = field(default_factory=list)


class ChatService:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.config_path = os.path.join(project_root, "config", "config.yaml")
        self.config = load_config(self.config_path)
        self.processor = NodeProcessor(self.config)
        self.cases_dir = os.path.join(project_root, self.config["cases_dir"])
        self.sessions: Dict[str, SessionRuntime] = {}

    def new_session(self) -> str:
        session_id = uuid4().hex
        self.sessions[session_id] = SessionRuntime()
        return session_id

    def get_session(self, session_id: Optional[str]) -> tuple[str, SessionRuntime]:
        if session_id and session_id in self.sessions:
            return session_id, self.sessions[session_id]
        sid = self.new_session()
        return sid, self.sessions[sid]

    def extract_thought(self, text: str) -> str:
        thought_match = re.search(r"Thought:\s*", text, re.IGNORECASE)
        if thought_match:
            start_pos = thought_match.end()
            next_section = re.search(r"\n\s*(Action:|Final Answer:)", text[start_pos:], re.IGNORECASE)
            if next_section:
                return text[start_pos:start_pos + next_section.start()].strip()
            return text[start_pos:].strip()
        return ""

    def extract_final_answer(self, text: str) -> str:
        final_answer_match = re.search(r"Final Answer:\s*", text, re.IGNORECASE)
        if final_answer_match:
            start_pos = final_answer_match.end()
            next_section = re.search(r"\n\s*(Observation:|Action:)", text[start_pos:], re.IGNORECASE)
            if next_section:
                return text[start_pos:start_pos + next_section.start()].strip()
            return text[start_pos:].strip()
        parts = text.split("Final Answer:")
        return parts[-1].strip() if len(parts) > 1 else text.strip()

    def extract_action_json(self, text: str):
        action_match = re.search(r"Action:\s*", text, re.IGNORECASE)
        if not action_match:
            return None
        action_start = action_match.end()
        action_str = text[action_start:].split("Final Answer:")[0].strip()
        if action_str.lower().strip() == "null":
            return None
        json_start = -1
        bracket_type = None
        bracket_count = 0
        for i, char in enumerate(action_str):
            if char in ["[", "{"]:
                if json_start == -1:
                    json_start = i
                    bracket_type = char
                    bracket_count = 1
                elif bracket_type == char:
                    bracket_count += 1
            elif char in ["]", "}"]:
                if bracket_type == "[" and char == "]":
                    bracket_count -= 1
                elif bracket_type == "{" and char == "}":
                    bracket_count -= 1
                if bracket_count == 0 and json_start != -1:
                    action_str = action_str[json_start:i + 1]
                    break
        if json_start == -1:
            return None
        try:
            return json.loads(action_str)
        except json.JSONDecodeError:
            return None

    def _emit(self, cb: TraceCallback, event: str, payload: Dict):
        if cb:
            cb(event, payload)

    def _parse_sources(self, observation: str) -> List[SourceChunk]:
        chunks: List[SourceChunk] = []
        for block in observation.split("\n---\n"):
            m = re.search(r"【来源：(.*?)\s*\|\s*匹配度：(\d+)】", block)
            if not m:
                continue
            title = m.group(1).strip()
            score = float(m.group(2))
            snippet = re.sub(r"^【来源：.*?】\n?", "", block).strip()
            chunks.append(SourceChunk(doc_id=title, title=title, snippet=snippet, score=score))
        return chunks

    def run_chat(self, query: str, session_id: Optional[str] = None, trace_cb: TraceCallback = None):
        sid, session = self.get_session(session_id)
        state = session.state
        start = time.time()

        state.set_variable("user_demand", query)
        current_node = self.config["start_node"]
        node = self.config["nodes"][current_node]
        max_steps = node.get("max_steps", 6)

        current_round_history: List[str] = []
        trace: List[ThoughtStep] = []
        sources: List[SourceChunk] = []

        if state.conversation_turns:
            current_round_history.append("【多轮对话历史】")
            for turn in state.conversation_turns[-3:]:
                current_round_history.append(f"第{turn['round']}轮 - 用户：{turn['user_input']}")
                current_round_history.append(f"第{turn['round']}轮 - AI：{turn['ai_response']}")
            current_round_history.append("")

        final_answer = ""
        for step in range(1, max_steps + 1):
            history_text = "\n".join(current_round_history) if current_round_history else ""
            prompt = render_template(node["prompt_template"], state.variables).replace("{{history}}", history_text)

            self._emit(trace_cb, "trace", {"step": step, "type": "plan", "content": f"第 {step} 步推理中"})
            response = self.processor.call_zhipu_ai(prompt, max_tokens=3000, tools=self.processor.get_tools_definition())
            response_text = response.get("content", "") if isinstance(response, dict) else str(response)
            tool_calls = response.get("tool_calls", []) if isinstance(response, dict) else []

            thought = self.extract_thought(response_text)
            if thought:
                ts = datetime.utcnow().isoformat()
                trace_step = ThoughtStep(type="reasoning", content=thought, ts=ts)
                trace.append(trace_step)
                current_round_history.append(f"Thought: {thought}")
                self._emit(trace_cb, "trace", trace_step.model_dump())

            has_final = "final answer:" in response_text.lower()
            has_action = bool(tool_calls) or ("action:" in response_text.lower())
            action_data = None

            if tool_calls:
                action_data = []
                for tool_call in tool_calls:
                    try:
                        action_data.append({
                            "tool": tool_call["function"]["name"],
                            "args": json.loads(tool_call["function"].get("arguments", "{}")),
                        })
                    except Exception:
                        continue
                if action_data:
                    current_round_history.append(f"Action: {json.dumps(action_data, ensure_ascii=False)}")
            elif has_action:
                action_data = self.extract_action_json(response_text)
                current_round_history.append(f"Action: {json.dumps(action_data, ensure_ascii=False)}" if action_data else "Action: null")

            if has_final:
                final_answer = self.extract_final_answer(response_text)
                if final_answer:
                    ts = datetime.utcnow().isoformat()
                    t = ThoughtStep(type="answer", content=final_answer, ts=ts)
                    trace.append(t)
                    current_round_history.append(f"Final Answer: {final_answer}")
                    self._emit(trace_cb, "token", {"content": final_answer})
                    self._emit(trace_cb, "done", {"answer": final_answer})
                    break

            if has_action and action_data:
                actions = action_data if isinstance(action_data, list) else [action_data]
                all_observations = []
                for action in actions:
                    tool_name = action.get("tool", "")
                    args = action.get("args", {})
                    if tool_name == "search_cases":
                        observation = search_cases(args.get("query", ""), self.cases_dir)
                    else:
                        observation = f"未知工具: {tool_name}"
                    all_observations.append(observation)
                    self._emit(trace_cb, "retrieval", {"tool": tool_name, "query": args.get("query", ""), "content": observation})
                    sources.extend(self._parse_sources(observation))
                if all_observations:
                    combined = '\n\n---\n\n'.join(all_observations)
                    current_round_history.append(f"Observation: {combined}")
            elif not has_final:
                current_round_history.append("Observation: 请输出 Action 或 Final Answer")

        if not final_answer:
            force_prompt = f"基于以下历史记录，回答用户问题：{query}\n\n历史记录：\n{history_text}"
            final_answer = str(self.processor.call_zhipu_ai(force_prompt, max_tokens=3000))
            self._emit(trace_cb, "done", {"answer": final_answer})

        state.add_conversation_turn(query, final_answer)
        session.last_trace = trace
        session.last_sources = sources[:3]

        return {
            "session_id": sid,
            "answer": final_answer,
            "trace": [t.model_dump() for t in trace],
            "sources": [s.model_dump() for s in session.last_sources],
            "usage": {"turn": state.current_round},
            "latency_ms": int((time.time() - start) * 1000),
        }
