# engine/ - 核心引擎模块

实现 ReAct Agent 的核心执行逻辑。

## 模块功能

### config_loader.py - 配置加载器

**功能**：加载和解析 YAML 配置文件，支持模板变量渲染。

**主要函数**：
- `load_config(config_path)`: 加载 YAML 配置文件
- `validate_config(config)`: 验证配置格式
- `render_template(template, variables)`: 渲染模板（替换 `{{variable}}`）

**使用示例**：
```python
config = load_config("config/config.yaml")
prompt = render_template("需求：{{user_demand}}", {"user_demand": "ESG基金"})
```

### state_manager.py - 状态管理器

**功能**：管理对话状态和历史记录。

**核心类**：`ConversationState`

**主要属性**：
- `variables`: 存储变量（如用户需求）
- `history`: 对话历史记录列表
- `current_node`: 当前执行的节点

**主要方法**：
- `set_variable(key, value)`: 设置变量
- `get_variable(key, default)`: 获取变量
- `move_to_node(node_name)`: 跳转到指定节点

## 重要规则（影响性能和内存）

### 历史记录管理

**当前实现**：
- `current_round_history`: 在 ReAct 循环中使用局部变量，存储当前轮次的所有步骤
- 每次循环时，将 Thought + Action + Observation 添加到 `current_round_history`
- Observation 会在执行后立即添加到历史记录，下一次循环时 LLM 可以看到
- `conversation_turns`: 存储多轮对话历史（每轮包含用户输入和AI回复）

**历史记录传递机制**：
- 每次循环开始时，将 `current_round_history` 转换为字符串传递给 prompt 的 `{{history}}`
- LLM 在思考时可以看到之前所有步骤的 Thought、Action 和 Observation
- Prompt 强制要求 LLM 首先检查历史记录，避免重复检索

**影响**：
- ✅ **单轮对话**：当前设计适合单轮对话场景
- ✅ **历史记录实时更新**：Observation 会在执行后立即出现在下一次循环的 history 中
- 💡 **多轮对话**：`conversation_turns` 存储多轮对话历史，可在 prompt 中引用

**使用示例**：
```python
# 在 ReAct 循环中
current_round_history = []
# 第1步：添加 Thought 和 Action
current_round_history.append(f"Thought: {thought}")
current_round_history.append(f"Action: {action}")
# 执行工具后，添加 Observation
current_round_history.append(f"Observation: {observation}")
# 第2步：构建历史记录传递给 prompt
history_text = "\n".join(current_round_history)  # 包含第1步的所有内容
```

### node_processor.py - 节点处理器

**功能**：处理节点执行逻辑，调用 LLM API。

**核心类**：`NodeProcessor`

**主要方法**：
- `call_zhipu_ai(prompt, max_tokens=None)`: 调用智谱 AI API
  - `prompt`: 提示词
  - `max_tokens`: 最大输出token数（None时使用默认值1500）
- `process_node(node_name, state)`: 执行指定节点

**LLM 调用流程**：
1. 构建 prompt（包含用户需求、历史记录）
2. 调用智谱 AI API
3. 返回 LLM 响应

**环境变量**：
- `ZHIPU_API_KEY`: API 密钥（必需）
- `ZHIPU_MODEL`: 模型名称（默认：glm-3-turbo）

## 重要规则（影响性能和效果）

### LLM API 调用参数

**关键参数设置**：
- `max_tokens`: **动态调整**
  - **默认值：1500**（适合 Thought/Action 阶段）
  - **Final Answer 阶段：3000**（确保完整输出）
  - **自动调整逻辑**：
    - 如果历史中有 Observation（检索结果），使用 3000
    - 否则使用 1500
  - 影响：确保 Final Answer 不会被截断
- `timeout`: **30秒**（请求超时时间）
  - 影响：网络慢时可能超时失败

**API 端点**：
- URL: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- 请求格式：标准 OpenAI 兼容格式

### 错误处理

- **API 密钥检查**：长度 < 10 时返回错误提示
- **HTTP 错误**：返回状态码和错误信息
- **网络异常**：捕获异常并返回错误信息

**影响**：
- ⚠️ 如果 API 调用失败，会返回错误信息字符串，可能影响后续流程
- 💡 建议：在生产环境中添加重试机制

## 工作流程

```
加载配置 → 创建状态管理器 → 创建节点处理器 → 执行节点 → 调用工具 → 更新状态
```

