# config/ - 配置文件目录

项目配置文件存放目录。

## 文件说明

### config.yaml - 主配置文件

**功能**：定义 ReAct Agent 的流程和提示模板。

**主要字段**：
- `name`: 项目名称
- `version`: 版本号
- `cases_dir`: 文档知识库目录（相对于项目根目录）
- `start_node`: 入口节点名称
- `nodes`: 节点定义字典

**节点结构**：
```yaml
nodes:
  react_start:
    type: "react_loop"          # 节点类型
    prompt_template: |           # 提示模板
      ...
    max_steps: 6                 # 最大迭代步数
```

**模板变量**：
- `{{user_demand}}`: 用户输入的需求
- `{{history}}`: 对话历史记录

**提示模板规则**：
1. 必须包含 Thought、Action、Final Answer 的格式说明
2. 描述可用工具及其调用格式
3. 约束 LLM 行为（禁止跳步、强制格式）
4. **强制检查历史记录**：要求 LLM 首先检查历史记录中的 Observation，避免重复检索

## 重要规则（影响 Agent 行为）

### max_steps 参数

**默认值**：6 步

**影响**：
- 控制 ReAct 循环的最大迭代次数
- 达到最大步数时，强制生成通用方案（不基于检索结果）
- 建议值：
  - 简单查询：3-4 步
  - 复杂查询：6-8 步
  - 调试模式：10+ 步

### prompt_template 关键约束

**格式要求**：
- LLM 必须严格按照 `Thought:` → `Action:` → `Final Answer:` 格式输出
- 禁止在 Action 后立即写 Final Answer（防止跳步）

**工具调用约束**：
- 关键词数量：1-3 个短关键词，不要用长句
- 检索策略：如果首次未找到，减少词或换同义词再试
- **强制检查历史记录**：每次思考时必须首先检查历史记录中的 Observation
  - 如果历史记录不为空，必须在 Thought 中明确说明看到了什么内容
  - 如果历史记录中有 Observation，必须优先使用，禁止重复检索相同或类似的关键词
  - 除非历史记录中的所有 Observation 完全无关，否则不再进行新检索
- 早停规则：如果历史中已有 1-2 个相关文档，直接生成 Final Answer

**意图判断机制**：
- **问答类**：询问信息、解释概念、分析问题（如："XX是什么？"、"XX的风险？"）
  - Final Answer 格式：简洁回答（1-3段），直接回答问题
- **方案生成类**：设计、规划、制定策略（如："设计XX"、"制定XX策略"）
  - Final Answer 格式：结构化方案（标题、要点、实施效果、适用场景等）
- LLM 在 Thought 阶段自动判断用户意图，并据此调整 Final Answer 格式

**历史记录检查机制**：
- **强制检查**：每次思考时必须首先检查历史记录，这是最重要的一步
- **明确说明**：如果历史记录不为空，必须在 Thought 中明确说明看到了什么内容
- **禁止重复检索**：如果历史记录中已有 Observation，必须优先使用，禁止重复检索相同或类似的关键词
- **宽容评估**：评估 Observation 时极为宽容，只要涉及相关主题即视为有用信息

**影响**：
- ✅ 严格约束可提高输出质量，避免重复检索
- ✅ 强制检查历史记录可确保 LLM 充分利用已有信息
- ⚠️ 过于严格可能导致 LLM 困惑
- 💡 根据实际效果调整约束强度

### .env.example - 环境变量示例

**功能**：环境变量配置模板。

**必需变量**：
- `ZHIPU_API_KEY`: 智谱 AI API 密钥

**可选变量**：
- `ZHIPU_MODEL`: 使用的模型（默认：glm-3-turbo）

**使用方法**：
1. 复制 `.env.example` 为 `.env`
2. 填入真实的 API Key
3. 程序会自动加载 `.env` 文件

## 配置修改指南

### 修改最大步数
```yaml
nodes:
  react_start:
    max_steps: 10  # 改为 10 步
```

### 添加新工具描述
在 `prompt_template` 中添加工具说明：
```yaml
prompt_template: |
  ...
  可用工具：
  - search_cases: 搜索文档库
    格式: {"tool": "search_cases", "args": {"query": "关键词"}}
  - calculator: 执行计算
    格式: {"tool": "calculator", "args": {"expression": "1+1"}}
```

### 修改提示词
直接编辑 `prompt_template` 字段，注意保持格式规范。

