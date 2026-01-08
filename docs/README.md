# DocAdvisor - 基于 ReAct + RAG 的通用文档智能顾问系统

## 📋 项目概述

**DocAdvisor** 是一个基于 **ReAct (Reasoning + Acting)** 框架实现的简化版 **RAG (Retrieval-Augmented Generation) Agent**，支持任意领域的文档知识库。

一个通用的文档智能问答与方案生成平台，通过 ReAct 框架和 RAG 技术，自动检索相关文档并生成专业建议。

### 核心功能

- 🎯 **智能需求理解**：用户输入任意领域的咨询问题、方案设计、策略规划等需求
- 🔄 **ReAct 循环推理**：Agent 通过 ReAct 循环（Thought → Action → Observation）自动调用本地文档检索工具
- 📚 **知识库检索**：优先基于 `cases/` 目录中的文档知识库生成专业、结构化的方案建议
- 🔀 **智能回退机制**：当检索不到足够相关文档时，回退到通用知识生成方案

项目采用 **节点式流程引擎 + YAML 配置驱动** 的轻量架构，代码清晰、易调试、易扩展，是学习和快速搭建 ReAct Agent 的优秀实践案例。

## 🏗️ 项目架构

### 技术栈

- **Python 3.x**
- **大语言模型 API**：支持多个提供商
  - 智谱 AI (GLM 系列)
  - OpenAI (GPT 系列)
  - Anthropic (Claude 系列)
  - 通义千问 (Qwen 系列)
  - Google Gemini
- **YAML**：流程配置
- **关键词检索**：本地文件搜索（可扩展为向量检索）

### 核心模块

#### 📂 src/engine/ - 核心引擎模块
- **config_loader.py**: 加载 YAML 配置，支持模板渲染（`{{variable}}`）
- **state_manager.py**: 管理对话状态（变量、历史记录）
- **node_processor.py**: 处理节点逻辑，调用大模型 API

> 📖 详细说明：[src/engine/README.md](../src/engine/README.md)

#### 📂 src/tools/ - 工具模块
- **search_cases.py**: 案例检索工具（关键词匹配，返回 Top 3 片段，每个片段15行非空行）

> 📖 详细说明：[src/tools/README.md](../src/tools/README.md)

#### 📂 scripts/ - 脚本目录
- **main.py**: 命令行版本（交互式）
- **tkinter_app.py**: GUI 版本（图形界面）

> 📖 详细说明：[scripts/README.md](../scripts/README.md)

#### 📂 config/ - 配置文件
- **config.yaml**: 主配置文件（定义 ReAct 流程和提示模板）
- **.env.example**: 环境变量模板

> 📖 详细说明：[config/README.md](../config/README.md)

#### 📂 cases/ - 知识库
- 文档知识库（支持任意领域的文档，如产品需求、策略方案、技术文档等）

## 📁 项目结构

```
DocAdvisor/
├── src/                            # 源代码目录（详见 src/README.md）
│   ├── engine/                     # 核心引擎模块（详见 src/engine/README.md）
│   ├── tools/                      # 工具模块（详见 src/tools/README.md）
│   └── utils/                      # 工具函数
├── scripts/                        # 脚本目录（详见 scripts/README.md）
│   ├── main.py                     # 命令行版本
│   └── tkinter_app.py              # GUI 版本
├── config/                         # 配置文件（详见 config/README.md）
│   ├── config.yaml                 # 主配置文件
│   └── README.md                   # 配置说明
├── cases/                          # 知识库
│   ├── *.md                        # 文档知识库文件（支持任意领域）
├── tests/                          # 测试目录（预留）
├── docs/                           # 文档目录
│   ├── README.md                   # 本文档（详细说明）
│   └── 优化方向.md                  # 项目优化建议
├── .env                            # 环境变量（需自行创建，参考 .env.example）
├── .env.example                    # 环境变量模板
├── requirements.txt                # 依赖列表
├── setup.py                        # 项目安装配置
└── README.md                       # 项目简介（简洁版）
```

> 💡 **提示**：每个目录都有独立的 README.md，详细说明该模块的功能和使用方法。

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.7+，并创建虚拟环境（推荐）：

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表：
- `PyYAML>=6.0`：YAML 配置文件解析
- `requests`：HTTP 请求（调用大模型 API）
- `python-dotenv`：环境变量管理
- `colorama`：终端彩色输出
- `tkinter`：GUI 界面（Python 内置，无需安装）

### 3. 配置大模型 API

#### 方式一：通过 GUI 界面配置（推荐）

启动 GUI 程序后，如果未配置模型，会自动弹出提示。点击界面上的 **"⚙️ 模型配置"** 按钮，在弹出的配置窗口中：

1. **选择提供商**：支持以下大模型服务提供商
   - **智谱AI (zhipu)**：GLM 系列模型
   - **OpenAI**：GPT 系列模型
   - **Anthropic (Claude)**：Claude 系列模型
   - **通义千问 (qwen)**：Qwen 系列模型
   - **Google Gemini**：Gemini 系列模型

2. **选择模型**：根据选择的提供商，选择对应的模型
   - 智谱AI：glm-3-turbo, glm-4, glm-4-flash, glm-4-plus
   - OpenAI：gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini
   - Anthropic：claude-3-5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku
   - 通义千问：qwen-turbo, qwen-plus, qwen-max, qwen-max-longcontext
   - Gemini：gemini-pro, gemini-pro-vision, gemini-1.5-pro, gemini-1.5-flash

3. **输入 API Key**：从对应提供商获取的 API Key

4. **保存配置**：点击"保存"按钮，配置将保存到 `.env` 文件

#### 方式二：手动编辑 .env 文件

复制 `.env.example` 为 `.env`，然后编辑：

```env
# 统一配置格式
API_KEY=your_api_key_here
MODEL=glm-4-flash
PROVIDER=zhipu
```

> **注意**：
> - 请将 `your_api_key_here` 替换为你的真实 API Key
> - 智谱 AI：可在 [智谱 AI 开放平台](https://open.bigmodel.cn/) 申请
> - OpenAI：可在 [OpenAI Platform](https://platform.openai.com/) 申请
> - Anthropic：可在 [Anthropic Console](https://www.anthropic.com/) 申请
> - 通义千问：可在 [阿里云 DashScope](https://dashscope.aliyun.com/) 申请
> - Google Gemini：可在 [Google AI Studio](https://ai.google.dev/) 申请

### 4. 准备知识库

将你的文档知识库放入 `cases/` 目录，支持任意领域的 Markdown 文档。

**示例**：
- 产品需求文档
- 策略方案文档
- 技术文档
- 业务案例文档
- 其他任意领域的文档

系统会自动检索这些文档并基于它们生成专业建议。

### 5. 启动程序

#### 方式一：命令行界面（CLI）

**方法一：使用快捷方式**
- 双击 `启动命令行.bat` 文件即可启动

**方法二：命令行启动**
```bash
python scripts/main.py
```

程序启动后，按提示输入你的需求，例如：
```
设计一款ESG可持续投资基金的销售策略
```
或任意其他领域的咨询问题。

**多轮对话功能**：
- 输入问题后，Agent 会处理并返回答案
- 可以继续输入新问题，Agent 会基于之前的对话上下文回答
- 输入 `exit` 或 `quit` 退出程序
- 输入 `new` 开始新对话（清空历史）

#### 方式二：Tkinter GUI 界面

**方法一：使用快捷方式（推荐）**
- 双击 `启动GUI.bat` 文件即可启动

**方法二：命令行启动**
```bash
python scripts/tkinter_app.py
```

启动后会打开图形界面窗口，在界面中输入问题或需求并点击"提交查询"按钮即可。

**GUI 功能**：
- ⚙️ **模型配置**：点击"模型配置"按钮可配置大模型 API Key 和模型选择
- 📋 **一键复制**：点击"一键复制"按钮可快速复制回答结果到剪贴板
- 💬 **多轮对话**：支持连续对话，对话历史会显示在顶部区域，可点击"查看详情"查看完整回答
- 🔄 **新建对话**：点击"新建对话"按钮可清空历史，开始新对话
- 📊 **窗口布局**：对话历史、推理过程、回答结果三个区域，可拖动分隔条调整大小
- 📱 **配置状态**：界面顶部显示当前使用的模型（不显示 API Key 以保护隐私）
- 🔍 **检索结果优化显示**：推理过程中的检索结果只显示前3行，超过3行时显示"查看详情"链接，点击可查看完整内容

Agent 将自动检索相关案例并生成结构化方案。支持多轮连续对话，可以基于前一轮对话继续深入讨论。

## 💡 使用示例

### 示例一：问答类问题

**输入**：
```
请输入您的需求：
ESG基金的风险是什么？
```

**输出**：简洁回答，直接说明 ESG 基金的风险点。

### 示例二：方案生成类问题

**输入**：
```
请输入您的需求：
设计一款ESG可持续投资基金的销售策略
```

**输出示例**：
```
🤔 第 1 步思考中...

Agent 回复：
Thought: 用户意图是"方案生成"，需求涉及ESG基金销售策略，关键词：ESG 销售策略
Action: [{"tool": "search_cases", "args": {"query": "ESG 销售"}}]

🔧 执行工具: search_cases，参数: {'query': 'ESG 销售'}
🔍 检索结果：
【来源：fund_sales_strategy.md | 匹配度：高】
...（相关文档片段）...

🤔 第 2 步思考中...

Agent 回复：
Thought: 已获取ESG销售策略相关文档，可以基于这些文档生成完整方案。
Final Answer: 
### ESG可持续投资基金销售策略
...（结构化方案）...

🎯 最终方案：
### ESG可持续投资基金销售策略
...（完整方案内容）...
```

### 示例三：多轮对话

**第1轮**：
```
[第 1 轮] 请输入您的问题或需求：
ESG基金的风险是什么？
```
Agent 回答：ESG基金的风险包括...

**第2轮**（基于第1轮继续）：
```
[第 2 轮] 请输入您的问题或需求：
那如何降低这些风险？
```
Agent 会基于前一轮关于ESG基金风险的讨论，提供降低风险的建议。

**第3轮**（继续深入）：
```
[第 2 轮] 请输入您的问题或需求：
请给我一个具体的风险管理方案
```
Agent 会结合前两轮的对话，生成具体的风险管理方案。

**退出或新建对话**：
- 输入 `exit` 或 `quit` 退出程序
- 输入 `new` 清空历史，开始新对话

## 🔧 工作原理

### ReAct 循环流程

```
用户输入需求
    ↓
[Thought] Agent 分析需求，决定行动
    ↓
[Action] 调用工具（如 search_cases）
    ↓
[Observation] 获取工具返回结果
    ↓
重复 Thought → Action → Observation
    ↓
[Final Answer] 生成最终方案
```

**详细说明**：
- **Thought**: Agent 分析用户需求，判断意图（问答 vs 方案生成），决定下一步行动
  - **强制检查历史记录**：每次思考时必须首先检查历史记录中的 Observation，避免重复检索
- **Action**: 调用工具（如 `search_cases`）检索相关文档，或输出 `null`（如果已有足够信息）
- **Observation**: 获取工具返回的检索结果，会立即添加到历史记录，下一次循环时可见
- **Final Answer**: 根据用户意图生成回答
  - **问答类**：简洁回答（1-3段），直接回答问题
  - **方案生成类**：结构化方案（标题、要点、实施效果、适用场景等）

### 模块协作流程

```
scripts/main.py 或 scripts/tkinter_app.py
    ↓ 加载配置
config/config.yaml
    ↓ 创建引擎
src/engine/state_manager.py (状态管理)
src/engine/node_processor.py (LLM 调用)
    ↓ 调用工具
src/tools/search_cases.py
    ↓ 检索案例
cases/*.md
    ↓ 返回结果
生成最终方案
```

### 检索机制

- **关键词匹配**：支持多关键词 OR 匹配，全文搜索所有 `.md` 文件
- **匹配度排序**：按关键词出现次数排序，返回 Top 3 最相关片段
- **片段优化**：每个片段包含前7行非空行+匹配行+后7行非空行（共15行非空行），每个文件最多处理5个匹配位置
- **智能回退**：如果检索不到相关文档，基于通用知识回答
- **历史记录检查**：Prompt 强制要求 LLM 首先检查历史记录中的 Observation，避免重复检索相同关键词

### 意图识别

系统会自动判断用户意图，并调整输出格式：

- **问答类**（如："ESG基金的风险是什么？"、"什么是量化基金？"）
  - 输出：简洁回答，直接回答问题
- **方案生成类**（如："设计一款ESG基金的销售策略"、"制定产品需求文档"）
  - 输出：结构化方案，包含标题、要点、实施效果等

> 📖 更多技术细节请查看各模块的 README.md

## 📈 项目特性

### 已实现功能

✅ **ReAct 循环控制**
- 最大步数限制（默认 6 步），防止无限循环
- 自动解析 LLM 输出（Thought / Action / Final Answer）
- 严格约束 LLM 行为（禁止跳步、强制工具格式）

✅ **本地关键词 RAG 检索**
- 支持多关键词 OR 匹配
- 全文搜索 `cases/` 下所有 `.md` 文件
- 按匹配度排序返回 Top 3 片段

✅ **状态管理**
- 保存用户需求、Observation 历史、变量
- 支持 `{{variable}}` 模板渲染
- 支持多轮对话状态持久化

✅ **多轮对话**
- 支持连续多轮对话，保持上下文记忆
- **对话记忆**：LLM 能够记住之前轮次的对话内容，理解当前问题是基于之前对话的追问、细化或修改
- CLI 版本：支持 `exit`/`quit` 退出，`new` 开始新对话
- GUI 版本：显示对话历史，支持"新建对话"功能，可点击查看完整回答详情
- 自动记录每轮对话的用户输入和 AI 回复
- **智能检索策略**：Prompt 强制要求 LLM 首先检查历史记录中的 Observation，避免重复检索相同关键词，优先使用已有信息
- **推理过程优化**：GUI 版本中，检索结果只显示前3行，超过3行时显示"查看详情"链接，点击可查看完整内容，保持界面简洁

✅ **智能检索与分析**
- 检索作为上下文增强：检索到的文档用于提供背景信息，LLM 基于这些信息进行分析推理
- **MVP原则**：检索次数尽可能少（一般一次就够了），一次检索可以包含多个关键词（用空格分隔）
- **关键词策略**：关键词颗粒度要小（2-3个字），但一次检索可以包含多个关键词
- **检索优化**：返回最匹配的 Top 3 片段，每个片段15行非空行，内容精简高效
- **自动优化**：检索失败时自动优化关键词（提取2-3个字的核心词）重试
- **历史记录检查**：Prompt 强制要求 LLM 首先检查历史记录中的 Observation，避免重复检索，优先使用已有信息

✅ **LLM 调用**
- 支持多个大模型服务提供商：
  - **智谱AI**：GLM 系列（glm-3-turbo, glm-4, glm-4-flash, glm-4-plus）
  - **OpenAI**：GPT 系列（gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini）
  - **Anthropic**：Claude 系列（claude-3-5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku）
  - **通义千问**：Qwen 系列（qwen-turbo, qwen-plus, qwen-max, qwen-max-longcontext）
  - **Google Gemini**：Gemini 系列（gemini-pro, gemini-pro-vision, gemini-1.5-pro, gemini-1.5-flash）
- GUI 界面可视化配置，无需手动编辑文件
- 超时重试机制：90秒超时，自动重试2次，提高稳定性
- 完整错误处理、彩色日志输出

✅ **知识库**
- 支持任意领域的文档知识库
- 内容简洁但覆盖关键要素，便于关键词检索实验

### 当前限制

⚠️ **关键词检索**：使用简单的关键词匹配，无语义搜索能力  
⚠️ **工具单一**：目前仅支持 `search_cases` 一个工具

## 🔮 扩展建议

### 性能优化

- 🔍 **向量检索**：替换为向量检索（Chroma + embeddings）提升语义匹配准确度
- ⚡ **索引优化**：引入全文搜索引擎（如 Whoosh）预建索引，实现毫秒级查询
- 💾 **结果缓存**：添加查询结果缓存（lru_cache 或 Redis）

### 功能扩展

- 🛠️ **多工具支持**：在 `src/tools/` 目录下添加更多工具（网络搜索、计算器、数据库查询）
- 🎨 **UI 增强**：进一步优化 Tkinter GUI，支持更丰富的交互功能
- 🔗 **框架集成**：接入 LangChain / LlamaIndex 实现更完整的 Agent 框架
- 📚 **知识库扩展**：增加更多领域文档，扩展知识库覆盖范围
- 💾 **对话持久化**：支持将对话历史保存到文件，支持导入导出

### 架构优化

- 📊 **性能监控**：添加性能监控（cProfile）
- 🧪 **单元测试**：补充单元测试和集成测试
- 📝 **API 接口**：提供 RESTful API 接口，支持 Web 集成

## 📝 配置说明

### 环境变量配置

在项目根目录创建 `.env` 文件（参考 `.env.example`）：

```env
API_KEY=your_api_key_here
MODEL=glm-4-flash
PROVIDER=zhipu
```

### 主配置文件

`config/config.yaml` 定义 ReAct 流程和提示模板。主要字段：
- `start_node`: 入口节点
- `nodes`: 节点定义（包含提示模板、最大步数等）

> 📖 详细配置说明：[config/README.md](../config/README.md)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](../LICENSE) 文件。

## 🙏 致谢

- 基于 ReAct 框架设计理念
- 使用多个大语言模型服务提供商的支持

---

**祝你玩得开心，快速搭建属于自己的智能文档顾问！** 🚀

